#!/usr/bin/env python3
"""
Infrastructure Logs Daemon - Tail /var/log/* to Cassandra

Daemon que monitorea archivos de log del sistema operativo y los envia
a Cassandra para almacenamiento centralizado (Capa 3 - Infrastructure Logs).

Arquitectura 3 Capas:
- Capa 1: DORA Metrics (proceso desarrollo)
- Capa 2: Application Logs (runtime Django)
- Capa 3: Infrastructure Logs (sistema operativo) <- ESTE SCRIPT

Uso:
    # Desarrollo (foreground)
    python infrastructure_logs_daemon.py --foreground

    # Produccion (daemon)
    python infrastructure_logs_daemon.py --daemon

    # Systemd service
    systemctl start infrastructure-logs-daemon

Features:
- Tail multiple log files (/var/log/nginx/, /var/log/postgresql/, etc.)
- Batch inserts a Cassandra (1000 logs/batch)
- Log rotation handling (inotify)
- Graceful shutdown (SIGTERM, SIGINT)
- Health check endpoint (HTTP)
- Metrics collection (logs_tailed, logs_written, errors)
"""

import sys
import os
import time
import signal
import argparse
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
from collections import deque
import threading
from queue import Queue, Full
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

try:
    from cassandra.cluster import Cluster
    from cassandra.query import BatchStatement, PreparedStatement
    from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
    from cassandra import ConsistencyLevel
except ImportError:
    print("ERROR: cassandra-driver not installed")
    print("Install with: pip install cassandra-driver")
    sys.exit(1)

try:
    import pyinotify
except ImportError:
    print("ERROR: pyinotify not installed")
    print("Install with: pip install pyinotify")
    sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_LOG_PATHS = [
    "/var/log/nginx/access.log",
    "/var/log/nginx/error.log",
    "/var/log/postgresql/postgresql-*.log",
    "/var/log/mysql/error.log",
    "/var/log/syslog",
    "/var/log/auth.log",
]

DEFAULT_CASSANDRA_HOSTS = ["127.0.0.1"]
DEFAULT_KEYSPACE = "logging"
DEFAULT_BATCH_SIZE = 1000
DEFAULT_BATCH_TIMEOUT = 5.0  # seconds
DEFAULT_QUEUE_MAXSIZE = 100000
DEFAULT_HEALTH_PORT = 9090


# ============================================================================
# Cassandra Connection
# ============================================================================

class CassandraWriter:
    """Escribe logs de infraestructura a Cassandra en batches."""

    def __init__(
        self,
        contact_points: List[str] = None,
        keyspace: str = DEFAULT_KEYSPACE,
        batch_size: int = DEFAULT_BATCH_SIZE,
        batch_timeout: float = DEFAULT_BATCH_TIMEOUT,
    ):
        self.contact_points = contact_points or DEFAULT_CASSANDRA_HOSTS
        self.keyspace = keyspace
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout

        self.cluster = None
        self.session = None
        self.insert_stmt: Optional[PreparedStatement] = None

        self.stats = {
            "logs_written": 0,
            "batches_written": 0,
            "errors": 0,
            "last_write": None,
        }

        self._connect()

    def _connect(self):
        """Conectar a Cassandra cluster."""
        load_balancing_policy = TokenAwarePolicy(DCAwareRoundRobinPolicy())

        self.cluster = Cluster(
            contact_points=self.contact_points,
            load_balancing_policy=load_balancing_policy,
            protocol_version=4,
        )

        self.session = self.cluster.connect(self.keyspace)

        # Prepared statement
        insert_cql = """
        INSERT INTO infrastructure_logs (
            log_date, timestamp, source, level, message, hostname, pid, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.insert_stmt = self.session.prepare(insert_cql)
        self.insert_stmt.consistency_level = ConsistencyLevel.LOCAL_QUORUM

    def write_batch(self, logs: List[Dict]):
        """
        Escribe batch de logs a Cassandra.

        Args:
            logs: Lista de dicts con campos de log
        """
        if not logs:
            return

        batch = BatchStatement(consistency_level=ConsistencyLevel.LOCAL_QUORUM)

        for log_entry in logs:
            batch.add(
                self.insert_stmt,
                (
                    date.today(),
                    log_entry.get("timestamp", datetime.now()),
                    log_entry.get("source", "unknown"),
                    log_entry.get("level", "INFO"),
                    log_entry.get("message", ""),
                    log_entry.get("hostname", ""),
                    log_entry.get("pid", None),
                    log_entry.get("metadata", {}),
                ),
            )

        try:
            self.session.execute(batch)
            self.stats["logs_written"] += len(logs)
            self.stats["batches_written"] += 1
            self.stats["last_write"] = datetime.now().isoformat()
        except Exception as e:
            self.stats["errors"] += 1
            logging.error(f"Error writing batch to Cassandra: {e}")
            raise

    def close(self):
        """Cerrar conexion a Cassandra."""
        if self.cluster:
            self.cluster.shutdown()


# ============================================================================
# Log Parser
# ============================================================================

class LogParser:
    """Parsea diferentes formatos de logs (nginx, syslog, postgresql)."""

    # Regex patterns
    NGINX_ACCESS_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
        r'(?P<status>\d+) (?P<bytes>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )

    NGINX_ERROR_PATTERN = re.compile(
        r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
        r'\[(?P<level>\w+)\] (?P<pid>\d+)#(?P<tid>\d+): '
        r'\*(?P<connection>\d+) (?P<message>.*)'
    )

    SYSLOG_PATTERN = re.compile(
        r'(?P<timestamp>\w+ \d+ \d{2}:\d{2}:\d{2}) '
        r'(?P<hostname>\S+) (?P<process>\S+?)(\[(?P<pid>\d+)\])?: '
        r'(?P<message>.*)'
    )

    POSTGRESQL_PATTERN = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+ \S+) '
        r'\[(?P<pid>\d+)\] (?P<level>\w+):  (?P<message>.*)'
    )

    @classmethod
    def parse_line(cls, line: str, source: str) -> Optional[Dict]:
        """
        Parsea linea de log segun formato.

        Args:
            line: Linea de log
            source: Archivo fuente (para determinar formato)

        Returns:
            Dict con campos parseados o None si no se pudo parsear
        """
        if "nginx/access" in source:
            return cls._parse_nginx_access(line, source)
        elif "nginx/error" in source:
            return cls._parse_nginx_error(line, source)
        elif "syslog" in source or "auth.log" in source:
            return cls._parse_syslog(line, source)
        elif "postgresql" in source:
            return cls._parse_postgresql(line, source)
        else:
            # Formato generico
            return cls._parse_generic(line, source)

    @classmethod
    def _parse_nginx_access(cls, line: str, source: str) -> Optional[Dict]:
        match = cls.NGINX_ACCESS_PATTERN.match(line)
        if not match:
            return None

        return {
            "timestamp": datetime.strptime(
                match.group("timestamp"), "%d/%b/%Y:%H:%M:%S %z"
            ),
            "source": source,
            "level": "INFO",
            "message": line.strip(),
            "hostname": "",
            "pid": None,
            "metadata": {
                "ip": match.group("ip"),
                "method": match.group("method"),
                "path": match.group("path"),
                "status": match.group("status"),
                "bytes": match.group("bytes"),
                "user_agent": match.group("user_agent"),
            },
        }

    @classmethod
    def _parse_nginx_error(cls, line: str, source: str) -> Optional[Dict]:
        match = cls.NGINX_ERROR_PATTERN.match(line)
        if not match:
            return None

        return {
            "timestamp": datetime.strptime(
                match.group("timestamp"), "%Y/%m/%d %H:%M:%S"
            ),
            "source": source,
            "level": match.group("level").upper(),
            "message": match.group("message"),
            "hostname": "",
            "pid": int(match.group("pid")),
            "metadata": {
                "connection": match.group("connection"),
            },
        }

    @classmethod
    def _parse_syslog(cls, line: str, source: str) -> Optional[Dict]:
        match = cls.SYSLOG_PATTERN.match(line)
        if not match:
            return None

        # Syslog timestamp sin año, asumir año actual
        timestamp_str = match.group("timestamp")
        current_year = datetime.now().year
        timestamp = datetime.strptime(
            f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S"
        )

        return {
            "timestamp": timestamp,
            "source": source,
            "level": "INFO",
            "message": match.group("message"),
            "hostname": match.group("hostname"),
            "pid": int(match.group("pid")) if match.group("pid") else None,
            "metadata": {
                "process": match.group("process"),
            },
        }

    @classmethod
    def _parse_postgresql(cls, line: str, source: str) -> Optional[Dict]:
        match = cls.POSTGRESQL_PATTERN.match(line)
        if not match:
            return None

        return {
            "timestamp": datetime.strptime(
                match.group("timestamp"), "%Y-%m-%d %H:%M:%S.%f %Z"
            ),
            "source": source,
            "level": match.group("level"),
            "message": match.group("message"),
            "hostname": "",
            "pid": int(match.group("pid")),
            "metadata": {},
        }

    @classmethod
    def _parse_generic(cls, line: str, source: str) -> Dict:
        """Fallback para formatos no reconocidos."""
        return {
            "timestamp": datetime.now(),
            "source": source,
            "level": "INFO",
            "message": line.strip(),
            "hostname": "",
            "pid": None,
            "metadata": {},
        }


# ============================================================================
# Log Tailer
# ============================================================================

class LogTailer:
    """Tail multiple log files usando inotify."""

    def __init__(
        self,
        log_paths: List[str],
        queue: Queue,
        follow_existing: bool = True,
    ):
        self.log_paths = log_paths
        self.queue = queue
        self.follow_existing = follow_existing

        self.file_handles: Dict[str, any] = {}
        self.file_positions: Dict[str, int] = {}
        self.wm = pyinotify.WatchManager()
        self.notifier = pyinotify.Notifier(self.wm, self._handle_event)

        self._setup_watches()

    def _setup_watches(self):
        """Setup inotify watches para log files."""
        mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO

        for log_path in self.log_paths:
            # Expand globs
            for path in Path("/var/log").glob(log_path.replace("/var/log/", "")):
                if path.is_file():
                    self.wm.add_watch(str(path), mask)
                    self.file_handles[str(path)] = open(path, "r")

                    if self.follow_existing:
                        # Read existing content
                        for line in self.file_handles[str(path)]:
                            self._enqueue_line(line, str(path))
                    else:
                        # Seek to end
                        self.file_handles[str(path)].seek(0, 2)

                    self.file_positions[str(path)] = self.file_handles[
                        str(path)
                    ].tell()

    def _handle_event(self, event):
        """Handle inotify event (file modification)."""
        path = event.pathname

        if path not in self.file_handles:
            # New file created
            self.file_handles[path] = open(path, "r")
            self.file_positions[path] = 0

        fh = self.file_handles[path]

        # Read new lines
        fh.seek(self.file_positions[path])
        for line in fh:
            self._enqueue_line(line, path)

        self.file_positions[path] = fh.tell()

    def _enqueue_line(self, line: str, source: str):
        """Parse y enqueue log line."""
        parsed = LogParser.parse_line(line, source)
        if parsed:
            try:
                self.queue.put_nowait(parsed)
            except Full:
                logging.warning(f"Queue full, dropping log from {source}")

    def run(self):
        """Run tailer loop (blocking)."""
        logging.info(f"Tailing {len(self.file_handles)} log files")
        self.notifier.loop()

    def stop(self):
        """Stop tailer."""
        self.notifier.stop()
        for fh in self.file_handles.values():
            fh.close()


# ============================================================================
# Daemon
# ============================================================================

class InfrastructureLogsDaemon:
    """Main daemon para tail logs -> Cassandra."""

    def __init__(
        self,
        log_paths: List[str],
        cassandra_hosts: List[str],
        keyspace: str = DEFAULT_KEYSPACE,
        batch_size: int = DEFAULT_BATCH_SIZE,
        batch_timeout: float = DEFAULT_BATCH_TIMEOUT,
        queue_maxsize: int = DEFAULT_QUEUE_MAXSIZE,
        health_port: int = DEFAULT_HEALTH_PORT,
    ):
        self.log_paths = log_paths
        self.cassandra_hosts = cassandra_hosts
        self.keyspace = keyspace
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.queue_maxsize = queue_maxsize
        self.health_port = health_port

        self.queue = Queue(maxsize=queue_maxsize)
        self.cassandra_writer: Optional[CassandraWriter] = None
        self.log_tailer: Optional[LogTailer] = None
        self.worker_thread: Optional[threading.Thread] = None
        self.tailer_thread: Optional[threading.Thread] = None
        self.health_server: Optional[HTTPServer] = None

        self.running = False
        self.stats = {
            "logs_tailed": 0,
            "logs_written": 0,
            "batches_written": 0,
            "errors": 0,
            "start_time": None,
        }

    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown."""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def _setup_signals(self):
        """Setup signal handlers."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _worker_loop(self):
        """Worker thread que consume queue y escribe a Cassandra."""
        batch = []
        last_flush = time.time()

        while self.running:
            try:
                # Get log from queue (timeout para check running flag)
                log_entry = self.queue.get(timeout=1.0)
                batch.append(log_entry)
                self.stats["logs_tailed"] += 1

                # Flush batch si lleno o timeout
                if (
                    len(batch) >= self.batch_size
                    or (time.time() - last_flush) >= self.batch_timeout
                ):
                    self.cassandra_writer.write_batch(batch)
                    self.stats["logs_written"] += len(batch)
                    self.stats["batches_written"] += 1
                    batch = []
                    last_flush = time.time()

            except Exception as e:
                if self.running:  # Only log if not shutting down
                    logging.error(f"Worker error: {e}")
                    self.stats["errors"] += 1

        # Flush remaining logs
        if batch:
            self.cassandra_writer.write_batch(batch)
            self.stats["logs_written"] += len(batch)
            self.stats["batches_written"] += 1

    def _start_health_server(self):
        """Start HTTP health check server."""
        daemon = self

        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()

                    response = {
                        "status": "healthy" if daemon.running else "stopped",
                        "stats": daemon.stats,
                        "cassandra_stats": daemon.cassandra_writer.stats,
                        "queue_size": daemon.queue.qsize(),
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress HTTP logs

        self.health_server = HTTPServer(("0.0.0.0", self.health_port), HealthHandler)
        health_thread = threading.Thread(target=self.health_server.serve_forever)
        health_thread.daemon = True
        health_thread.start()
        logging.info(f"Health check server running on port {self.health_port}")

    def start(self):
        """Start daemon."""
        logging.info("Starting Infrastructure Logs Daemon")
        self._setup_signals()

        self.running = True
        self.stats["start_time"] = datetime.now().isoformat()

        # Connect to Cassandra
        self.cassandra_writer = CassandraWriter(
            contact_points=self.cassandra_hosts,
            keyspace=self.keyspace,
            batch_size=self.batch_size,
            batch_timeout=self.batch_timeout,
        )

        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=False)
        self.worker_thread.start()

        # Start health server
        self._start_health_server()

        # Start log tailer (blocking)
        self.log_tailer = LogTailer(self.log_paths, self.queue)
        self.log_tailer.run()

    def stop(self):
        """Stop daemon."""
        logging.info("Stopping Infrastructure Logs Daemon")
        self.running = False

        if self.log_tailer:
            self.log_tailer.stop()

        if self.worker_thread:
            self.worker_thread.join(timeout=10)

        if self.cassandra_writer:
            self.cassandra_writer.close()

        if self.health_server:
            self.health_server.shutdown()

        logging.info("Daemon stopped")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Infrastructure Logs Daemon - Tail /var/log/* to Cassandra"
    )
    parser.add_argument(
        "--log-paths",
        nargs="+",
        default=DEFAULT_LOG_PATHS,
        help="Log file paths to tail (supports globs)",
    )
    parser.add_argument(
        "--cassandra-hosts",
        nargs="+",
        default=DEFAULT_CASSANDRA_HOSTS,
        help="Cassandra contact points",
    )
    parser.add_argument(
        "--keyspace", default=DEFAULT_KEYSPACE, help="Cassandra keyspace"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Batch size for Cassandra writes",
    )
    parser.add_argument(
        "--batch-timeout",
        type=float,
        default=DEFAULT_BATCH_TIMEOUT,
        help="Batch timeout (seconds)",
    )
    parser.add_argument(
        "--queue-maxsize",
        type=int,
        default=DEFAULT_QUEUE_MAXSIZE,
        help="Max queue size",
    )
    parser.add_argument(
        "--health-port",
        type=int,
        default=DEFAULT_HEALTH_PORT,
        help="Health check HTTP port",
    )
    parser.add_argument(
        "--foreground", action="store_true", help="Run in foreground (not daemon)"
    )
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Create daemon
    daemon = InfrastructureLogsDaemon(
        log_paths=args.log_paths,
        cassandra_hosts=args.cassandra_hosts,
        keyspace=args.keyspace,
        batch_size=args.batch_size,
        batch_timeout=args.batch_timeout,
        queue_maxsize=args.queue_maxsize,
        health_port=args.health_port,
    )

    # Run
    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        daemon.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
