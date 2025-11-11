#!/usr/bin/env python3
"""
Cassandra Schema Setup - Inicializar keyspace y tables para logs

Crea:
- Keyspace: logging (replication_factor=3)
- Table: application_logs (Capa 2 - Application Logs)
- Table: infrastructure_logs (Capa 3 - Infrastructure Logs)
- Indexes: level, logger, request_id

TTL: 90 dias automatico (7776000 segundos)
Compaction: TimeWindowCompactionStrategy (diaria)

Usage:
    python scripts/logging/cassandra_schema_setup.py \\
        --contact-points 127.0.0.1,192.168.1.2,192.168.1.3 \\
        --replication-factor 3 \\
        --dry-run

Requirements:
    pip install cassandra-driver

Related:
    - ADR-2025-004: Centralized Log Storage en Cassandra
    - OBSERVABILITY_LAYERS.md
"""

import argparse
import sys
from typing import List

try:
    from cassandra.cluster import Cluster
    from cassandra import ConsistencyLevel
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False


class CassandraSchemaSetup:
    """Setup Cassandra keyspace y tables para logging."""

    def __init__(
        self,
        contact_points: List[str],
        port: int = 9042,
        replication_factor: int = 3,
        ttl_days: int = 90
    ):
        """
        Args:
            contact_points: Lista de IPs Cassandra nodes
            port: Puerto Cassandra (default: 9042)
            replication_factor: Replication factor (default: 3)
            ttl_days: TTL en dias (default: 90)
        """
        self.contact_points = contact_points
        self.port = port
        self.replication_factor = replication_factor
        self.ttl_seconds = ttl_days * 24 * 60 * 60

        self.cluster = None
        self.session = None

    def connect(self):
        """Conectar a Cassandra cluster."""
        print(f"[1/7] Connecting to Cassandra: {self.contact_points}")

        self.cluster = Cluster(
            contact_points=self.contact_points,
            port=self.port
        )
        self.session = self.cluster.connect()

        print(f"[OK] Connected to cluster: {self.cluster.metadata.cluster_name}")

    def create_keyspace(self):
        """Crear keyspace 'logging' con replication."""
        print(f"[2/7] Creating keyspace: logging (replication_factor={self.replication_factor})")

        cql = f"""
        CREATE KEYSPACE IF NOT EXISTS logging
        WITH replication = {{
            'class': 'SimpleStrategy',
            'replication_factor': {self.replication_factor}
        }}
        AND durable_writes = true;
        """

        self.session.execute(cql)
        print("[OK] Keyspace 'logging' created")

    def create_application_logs_table(self):
        """Crear tabla application_logs (Capa 2 - Application Logs)."""
        print(f"[3/7] Creating table: application_logs (TTL={self.ttl_seconds}s / {self.ttl_seconds // 86400} days)")

        cql = f"""
        CREATE TABLE IF NOT EXISTS logging.application_logs (
            log_date DATE,
            timestamp TIMESTAMP,
            level TEXT,
            logger TEXT,
            message TEXT,

            -- Contexto
            request_id TEXT,
            user_id INT,
            session_id TEXT,

            -- Metadata
            metadata MAP<TEXT, TEXT>,
            traceback TEXT,
            duration_ms DECIMAL,

            PRIMARY KEY ((log_date), timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC)
          AND compaction = {{
              'class': 'TimeWindowCompactionStrategy',
              'compaction_window_size': 1,
              'compaction_window_unit': 'DAYS'
          }}
          AND default_time_to_live = {self.ttl_seconds}
          AND gc_grace_seconds = 86400
          AND comment = 'Application logs - OBSERVABILITY_LAYERS Capa 2';
        """

        self.session.execute(cql)
        print("[OK] Table 'application_logs' created")

    def create_infrastructure_logs_table(self):
        """Crear tabla infrastructure_logs (Capa 3 - Infrastructure Logs)."""
        print(f"[4/7] Creating table: infrastructure_logs (TTL={self.ttl_seconds}s / {self.ttl_seconds // 86400} days)")

        cql = f"""
        CREATE TABLE IF NOT EXISTS logging.infrastructure_logs (
            log_date DATE,
            timestamp TIMESTAMP,
            source TEXT,
            level TEXT,
            message TEXT,
            metadata MAP<TEXT, TEXT>,

            PRIMARY KEY ((log_date), timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC)
          AND compaction = {{
              'class': 'TimeWindowCompactionStrategy',
              'compaction_window_size': 1,
              'compaction_window_unit': 'DAYS'
          }}
          AND default_time_to_live = {self.ttl_seconds}
          AND gc_grace_seconds = 86400
          AND comment = 'Infrastructure logs - OBSERVABILITY_LAYERS Capa 3';
        """

        self.session.execute(cql)
        print("[OK] Table 'infrastructure_logs' created")

    def create_indexes(self):
        """Crear secondary indexes para queries frecuentes."""
        print("[5/7] Creating secondary indexes...")

        indexes = [
            ("idx_app_logs_level", "logging.application_logs", "level"),
            ("idx_app_logs_logger", "logging.application_logs", "logger"),
            ("idx_app_logs_request_id", "logging.application_logs", "request_id"),
            ("idx_infra_logs_source", "logging.infrastructure_logs", "source"),
            ("idx_infra_logs_level", "logging.infrastructure_logs", "level"),
        ]

        for idx_name, table, column in indexes:
            cql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column});"
            self.session.execute(cql)
            print(f"[OK] Index '{idx_name}' created on {table}({column})")

    def verify_schema(self):
        """Verificar schema creado correctamente."""
        print("[6/7] Verifying schema...")

        # Verificar keyspace
        keyspace_meta = self.cluster.metadata.keyspaces.get('logging')
        if not keyspace_meta:
            raise Exception("Keyspace 'logging' not found")

        print(f"[OK] Keyspace 'logging' exists (replication={keyspace_meta.replication_strategy})")

        # Verificar tables
        tables = ['application_logs', 'infrastructure_logs']
        for table_name in tables:
            table_meta = keyspace_meta.tables.get(table_name)
            if not table_meta:
                raise Exception(f"Table '{table_name}' not found")

            print(f"[OK] Table '{table_name}' exists (columns={len(table_meta.columns)})")

        # Verificar indexes
        app_logs_meta = keyspace_meta.tables.get('application_logs')
        if app_logs_meta:
            print(f"[OK] Indexes on 'application_logs': {len(app_logs_meta.indexes)}")

    def show_stats(self):
        """Mostrar estadísticas del schema."""
        print("[7/7] Schema statistics:")

        # Describir keyspace
        rows = self.session.execute("DESCRIBE KEYSPACE logging;")
        print("\n--- Keyspace Schema ---")
        for row in rows:
            print(row)

        print("\n[SUCCESS] Cassandra schema setup completed!")
        print(f"\nNext steps:")
        print(f"1. Configure Django LOGGING to use CassandraLogHandler")
        print(f"2. Test with: python scripts/logging/cassandra_handler.py")
        print(f"3. Monitor with: nodetool status logging")

    def close(self):
        """Cerrar conexión."""
        if self.cluster:
            self.cluster.shutdown()

    def setup(self):
        """Ejecutar setup completo."""
        try:
            self.connect()
            self.create_keyspace()
            self.create_application_logs_table()
            self.create_infrastructure_logs_table()
            self.create_indexes()
            self.verify_schema()
            self.show_stats()
        except Exception as e:
            print(f"\n[ERROR] Setup failed: {e}")
            raise
        finally:
            self.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Setup Cassandra schema para centralized logging'
    )
    parser.add_argument(
        '--contact-points',
        type=str,
        default='127.0.0.1',
        help='Cassandra contact points (comma-separated IPs) (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9042,
        help='Cassandra port (default: 9042)'
    )
    parser.add_argument(
        '--replication-factor',
        type=int,
        default=3,
        help='Replication factor (default: 3)'
    )
    parser.add_argument(
        '--ttl-days',
        type=int,
        default=90,
        help='TTL in days (default: 90)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run (show what would be created)'
    )

    args = parser.parse_args()

    # Parse contact points
    contact_points = [ip.strip() for ip in args.contact_points.split(',')]

    print("=" * 70)
    print("Cassandra Schema Setup - Centralized Logging")
    print("=" * 70)
    print(f"Contact Points: {contact_points}")
    print(f"Port: {args.port}")
    print(f"Replication Factor: {args.replication_factor}")
    print(f"TTL: {args.ttl_days} days ({args.ttl_days * 86400} seconds)")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN] Would create:")
        print("  - Keyspace: logging")
        print("  - Table: application_logs (with TTL, indexes)")
        print("  - Table: infrastructure_logs (with TTL, indexes)")
        print("  - Indexes: level, logger, request_id, source")
        return 0

    if not CASSANDRA_AVAILABLE:
        print("[ERROR] cassandra-driver not installed")
        print("Install with: pip install cassandra-driver")
        return 1

    # Confirmar
    print("\nThis will create keyspace 'logging' and tables.")
    response = input("Continue? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        return 0

    # Setup
    setup = CassandraSchemaSetup(
        contact_points=contact_points,
        port=args.port,
        replication_factor=args.replication_factor,
        ttl_days=args.ttl_days
    )

    try:
        setup.setup()
        return 0
    except Exception as e:
        print(f"\n[FAILED] {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
