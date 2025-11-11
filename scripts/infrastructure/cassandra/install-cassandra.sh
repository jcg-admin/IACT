#!/bin/bash
# Install Cassandra Cluster - IACT Project
# Soporta Docker Compose y systemd nativo

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_METHOD="${1:-docker}"  # docker | systemd
CASSANDRA_VERSION="4.1"
CLUSTER_NAME="iact-logging-cluster"
NUM_NODES=3

echo -e "${GREEN}[INFO]${NC} IACT Cassandra Cluster Installation"
echo -e "${GREEN}[INFO]${NC} Method: ${INSTALL_METHOD}"
echo -e "${GREEN}[INFO]${NC} Nodes: ${NUM_NODES}"
echo ""

# ============================================================================
# Docker Compose Installation
# ============================================================================

install_docker() {
    echo -e "${GREEN}[INFO]${NC} Installing Cassandra via Docker Compose"

    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} docker-compose not found"
        echo -e "${YELLOW}[HINT]${NC} Install with: sudo apt-get install docker-compose"
        exit 1
    fi

    # Check docker running
    if ! docker ps &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Docker daemon not running"
        echo -e "${YELLOW}[HINT]${NC} Start with: sudo systemctl start docker"
        exit 1
    fi

    # Start cluster
    echo -e "${GREEN}[INFO]${NC} Starting 3-node Cassandra cluster..."
    docker-compose -f docker-compose.cassandra.yml up -d

    # Wait for cluster
    echo -e "${GREEN}[INFO]${NC} Waiting for cluster to be ready (may take 2-3 minutes)..."
    sleep 30

    # Check cluster status
    echo -e "${GREEN}[INFO]${NC} Checking cluster status..."
    docker exec cassandra-1 nodetool status || true

    # Create keyspace and schema
    echo -e "${GREEN}[INFO]${NC} Creating keyspace and schema..."
    sleep 10
    python3 scripts/logging/cassandra_schema_setup.py \
        --contact-points 127.0.0.1 \
        --replication-factor 3 \
        --create-keyspace \
        --create-tables \
        --create-indexes

    echo ""
    echo -e "${GREEN}[SUCCESS]${NC} Cassandra cluster installed successfully!"
    echo -e "${GREEN}[INFO]${NC} Connection endpoints:"
    echo -e "  - cassandra-1: localhost:9042"
    echo -e "  - cassandra-2: localhost:9043"
    echo -e "  - cassandra-3: localhost:9044"
    echo ""
    echo -e "${YELLOW}[NEXT STEPS]${NC}"
    echo -e "  1. Configure Django settings.py (see scripts/cassandra/configure-django.sh)"
    echo -e "  2. Test logging: python scripts/logging/cassandra_handler.py --test"
    echo -e "  3. Start infrastructure daemon: systemctl start infrastructure-logs-daemon"
}

# ============================================================================
# Systemd Native Installation
# ============================================================================

install_systemd() {
    echo -e "${GREEN}[INFO]${NC} Installing Cassandra via systemd (native)"

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}[ERROR]${NC} This script must be run as root for systemd installation"
        echo -e "${YELLOW}[HINT]${NC} Run with: sudo $0 systemd"
        exit 1
    fi

    # Install Java
    echo -e "${GREEN}[INFO]${NC} Installing Java 11..."
    apt-get update
    apt-get install -y openjdk-11-jdk-headless

    # Add Cassandra repository
    echo -e "${GREEN}[INFO]${NC} Adding Cassandra repository..."
    echo "deb https://debian.cassandra.apache.org 41x main" | tee /etc/apt/sources.list.d/cassandra.sources.list
    curl https://downloads.apache.org/cassandra/KEYS | apt-key add -

    # Install Cassandra
    echo -e "${GREEN}[INFO]${NC} Installing Cassandra ${CASSANDRA_VERSION}..."
    apt-get update
    apt-get install -y cassandra

    # Configure Cassandra
    echo -e "${GREEN}[INFO]${NC} Configuring Cassandra..."

    # Backup original config
    cp /etc/cassandra/cassandra.yaml /etc/cassandra/cassandra.yaml.backup

    # Update cluster name
    sed -i "s/cluster_name: .*/cluster_name: '${CLUSTER_NAME}'/" /etc/cassandra/cassandra.yaml

    # Update seeds (for single-node, use localhost; for multi-node, update manually)
    sed -i "s/seeds: .*/seeds: '127.0.0.1'/" /etc/cassandra/cassandra.yaml

    # Start Cassandra
    echo -e "${GREEN}[INFO]${NC} Starting Cassandra service..."
    systemctl start cassandra
    systemctl enable cassandra

    # Wait for Cassandra to start
    echo -e "${GREEN}[INFO]${NC} Waiting for Cassandra to be ready..."
    sleep 30

    # Check status
    echo -e "${GREEN}[INFO]${NC} Checking Cassandra status..."
    nodetool status

    # Create keyspace and schema
    echo -e "${GREEN}[INFO]${NC} Creating keyspace and schema..."
    python3 scripts/logging/cassandra_schema_setup.py \
        --contact-points 127.0.0.1 \
        --replication-factor 1 \
        --create-keyspace \
        --create-tables \
        --create-indexes

    echo ""
    echo -e "${GREEN}[SUCCESS]${NC} Cassandra installed successfully!"
    echo -e "${GREEN}[INFO]${NC} Connection endpoint: localhost:9042"
    echo ""
    echo -e "${YELLOW}[NEXT STEPS]${NC}"
    echo -e "  1. For multi-node cluster, update /etc/cassandra/cassandra.yaml seeds"
    echo -e "  2. Configure Django settings.py (see scripts/cassandra/configure-django.sh)"
    echo -e "  3. Test logging: python scripts/logging/cassandra_handler.py --test"
}

# ============================================================================
# Main
# ============================================================================

case "$INSTALL_METHOD" in
    docker)
        install_docker
        ;;
    systemd)
        install_systemd
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Invalid installation method: $INSTALL_METHOD"
        echo -e "${YELLOW}[USAGE]${NC} $0 [docker|systemd]"
        exit 1
        ;;
esac
