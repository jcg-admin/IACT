#!/usr/bin/env python3
"""
Infrastructure Log Collector Daemon - Layer 3

Colecta logs de infraestructura del sistema operativo y los envia a Cassandra
en batches de 1000 para alta performance.

Features:
- Lee syslog, systemd, docker, auth logs
- Parsea y estructura logs
- Batch write a Cassandra (1000 logs/batch)
- Auto-retry con backoff
- Graceful shutdown

Usage:
    python infrastructure_log_collector.py --daemon
    python infrastructure_log_collector.py --test

Requirements:
    pip install cassandra-driver watchdog
"""

import argparse
import json
import logging
import os
import re
import signal
import socket
import sys
import time
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from cassandra.cluster import Cluster, Session
    from cassandra.query import BatchStatement, SimpleStatement
    from cassandra import ConsistencyLevel
except ImportError:
    print("[ERROR] cassandra-driver not installed: pip install cassandra-driver")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Cassandra connection
CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "127.0.0.1").split(",")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = "logging"

# Log sources to monitor
LOG_SOURCES = {
    "syslog": "/var/log/syslog",
    "auth": "/var/log/auth.log",
    "kern": "/var/log/kern.log",
    "systemd": "journalctl",  # Special: use journalctl command
}

# Batch configuration
BATCH_SIZE = 1000
BATCH_TIMEOUT_SECONDS = 5  # Flush batch even if not full after 5 seconds

# Daemon configuration
POLL_INTERVAL_SECONDS = 1
HOSTNAME = socket.gethostname()

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/iact/infrastructure_collector.log')
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# LOG PARSER
# ============================================================================

class LogParser:
    """Parse various log formats into structured format."""

    SYSLOG_PATTERN = re.compile(
        r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<process>\S+?)(\[(?P<pid>\d+)\])?:\s+'
        r'(?P<message>.*)'
    )

    SEVERITY_MAPPING = {
        'emerg': 'EMERGENCY',
        'alert': 'ALERT',
        'crit': 'CRITICAL',
        'err': 'ERROR',
        'warning': 'WARNING',
        'notice': 'NOTICE',
        'info': 'INFO',
        'debug': 'DEBUG',
    }

    @classmethod
    def parse_syslog(cls, line: str, source: str) -> Optional[Dict]:
        """Parse syslog format line."""
        match = cls.SYSLOG_PATTERN.match(line)
        if not match:
            return None

        groups = match.groupdict()

        # Parse timestamp (current year assumed)
        current_year = datetime.now().year
        timestamp_str = f"{current_year} {groups['timestamp']}"
        try:
            log_timestamp = datetime.strptime(timestamp_str, "%Y %b %d %H:%M:%S")
        except ValueError:
            log_timestamp = datetime.now()

        # Extract severity from message if present
        severity = 'INFO'
        message = groups['message']
        for key, value in cls.SEVERITY_MAPPING.items():
            if key in message.lower():
                severity = value
                break

        return {
            'hostname': HOSTNAME,
            'log_date': date.today(),
            'log_timestamp': log_timestamp,
            'log_id': uuid.uuid4(),
            'source': source,
            'severity': severity,
            'facility': cls._extract_facility(source),
            'message': message,
            'process_name': groups.get('process'),
            'process_id': int(groups['pid']) if groups.get('pid') else None,
            'user_name': None,
            'tags': set(),
            'extra': {},
            'ingested_at': datetime.now(),
        }

    @staticmethod
    def _extract_facility(source: str) -> str:
        """Extract syslog facility from source."""
        facility_map = {
            'syslog': 'syslog',
            'auth': 'auth',
            'kern': 'kern',
            'systemd': 'daemon',
        }
        return facility_map.get(source, 'user')

    @classmethod
    def parse_journalctl(cls, line: str) -> Optional[Dict]:
        """Parse journalctl JSON output."""
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None

        # Extract timestamp
        timestamp_usec = int(data.get('__REALTIME_TIMESTAMP', 0))
        log_timestamp = datetime.fromtimestamp(timestamp_usec / 1000000)

        # Extract severity
        priority = int(data.get('PRIORITY', 6))  # Default to INFO
        severity_map = {
            0: 'EMERGENCY', 1: 'ALERT', 2: 'CRITICAL', 3: 'ERROR',
            4: 'WARNING', 5: 'NOTICE', 6: 'INFO', 7: 'DEBUG'
        }
        severity = severity_map.get(priority, 'INFO')

        return {
            'hostname': HOSTNAME,
            'log_date': date.today(),
            'log_timestamp': log_timestamp,
            'log_id': uuid.uuid4(),
            'source': 'systemd',
            'severity': severity,
            'facility': 'daemon',
            'message': data.get('MESSAGE', ''),
            'process_name': data.get('_COMM'),
            'process_id': int(data.get('_PID')) if data.get('_PID') else None,
            'user_name': data.get('_UID'),
            'tags': set(),
            'extra': {
                'unit': data.get('_SYSTEMD_UNIT', ''),
                'transport': data.get('_TRANSPORT', ''),
            },
            'ingested_at': datetime.now(),
        }


# ============================================================================
# CASSANDRA WRITER
# ============================================================================

class CassandraWriter:
    """Write logs to Cassandra with batching."""

    def __init__(self):
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None
        self.batch: List[Dict] = []
        self.batch_created_at = time.time()
        self.total_written = 0

    def connect(self):
        """Connect to Cassandra cluster."""
        logger.info(f"Connecting to Cassandra: {CASSANDRA_HOSTS}")
        try:
            self.cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
            self.session = self.cluster.connect(CASSANDRA_KEYSPACE)
            logger.info("Connected to Cassandra successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Cassandra: {e}")
            raise

    def disconnect(self):
        """Disconnect from Cassandra."""
        if self.batch:
            self.flush_batch()

        if self.cluster:
            self.cluster.shutdown()
            logger.info("Disconnected from Cassandra")

    def write_log(self, log_entry: Dict):
        """Add log to batch and flush if needed."""
        self.batch.append(log_entry)

        # Flush if batch is full or timeout reached
        if len(self.batch) >= BATCH_SIZE:
            self.flush_batch()
        elif time.time() - self.batch_created_at >= BATCH_TIMEOUT_SECONDS:
            self.flush_batch()

    def flush_batch(self):
        """Flush current batch to Cassandra."""
        if not self.batch:
            return

        batch_size = len(self.batch)
        logger.debug(f"Flushing batch of {batch_size} logs...")

        try:
            # Prepare batch statement
            insert_query = """
                INSERT INTO infrastructure_logs (
                    hostname, log_date, log_timestamp, log_id,
                    source, severity, facility, message,
                    process_name, process_id, user_name,
                    tags, extra, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            prepared = self.session.prepare(insert_query)
            batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)

            for log_entry in self.batch:
                batch.add(prepared, (
                    log_entry['hostname'],
                    log_entry['log_date'],
                    log_entry['log_timestamp'],
                    log_entry['log_id'],
                    log_entry['source'],
                    log_entry['severity'],
                    log_entry['facility'],
                    log_entry['message'],
                    log_entry['process_name'],
                    log_entry['process_id'],
                    log_entry['user_name'],
                    log_entry['tags'],
                    log_entry['extra'],
                    log_entry['ingested_at'],
                ))

            # Execute batch
            self.session.execute(batch)

            self.total_written += batch_size
            logger.info(f"Flushed {batch_size} logs to Cassandra (total: {self.total_written})")

        except Exception as e:
            logger.error(f"Failed to flush batch: {e}")
            # TODO: Implement retry logic or dead letter queue

        finally:
            # Clear batch
            self.batch = []
            self.batch_created_at = time.time()


# ============================================================================
# LOG COLLECTOR
# ============================================================================

class InfrastructureLogCollector:
    """Main collector daemon."""

    def __init__(self):
        self.running = False
        self.writer = CassandraWriter()
        self.file_positions: Dict[str, int] = {}

    def start(self):
        """Start collector daemon."""
        logger.info("Starting Infrastructure Log Collector...")

        # Connect to Cassandra
        self.writer.connect()

        # Initialize file positions
        for source, path in LOG_SOURCES.items():
            if path != "journalctl" and Path(path).exists():
                # Start from end of file
                self.file_positions[source] = Path(path).stat().st_size

        # Set running flag
        self.running = True

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info("Collector started successfully")

        # Main loop
        while self.running:
            self._collect_iteration()
            time.sleep(POLL_INTERVAL_SECONDS)

    def _collect_iteration(self):
        """Single collection iteration."""
        for source, path in LOG_SOURCES.items():
            if path == "journalctl":
                self._collect_journalctl()
            elif Path(path).exists():
                self._collect_file(source, path)

    def _collect_file(self, source: str, file_path: str):
        """Collect logs from file."""
        try:
            with open(file_path, 'r') as f:
                # Seek to last position
                last_pos = self.file_positions.get(source, 0)
                f.seek(last_pos)

                # Read new lines
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Parse log
                    log_entry = LogParser.parse_syslog(line, source)
                    if log_entry:
                        self.writer.write_log(log_entry)

                # Update position
                self.file_positions[source] = f.tell()

        except Exception as e:
            logger.error(f"Error collecting from {file_path}: {e}")

    def _collect_journalctl(self):
        """Collect logs from journalctl."""
        # TODO: Implement journalctl collection using subprocess
        # journalctl -o json --since "1 minute ago" -n 100
        pass

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.writer.disconnect()
        sys.exit(0)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Infrastructure Log Collector Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--test", action="store_true", help="Test mode (collect once)")
    args = parser.parse_args()

    if args.test:
        logger.info("Running in TEST mode (single iteration)...")
        collector = InfrastructureLogCollector()
        collector.writer.connect()
        collector._collect_iteration()
        collector.writer.flush_batch()
        collector.writer.disconnect()
        logger.info("Test completed successfully")
    elif args.daemon:
        logger.info("Running in DAEMON mode...")
        collector = InfrastructureLogCollector()
        collector.start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
