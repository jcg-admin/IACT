#!/bin/bash
# Configure Django settings.py for Cassandra Logging

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SETTINGS_FILE="${1:-api/callcentersite/callcentersite/settings/production.py}"

echo -e "${GREEN}[INFO]${NC} Configuring Django settings for Cassandra logging"
echo -e "${GREEN}[INFO]${NC} Settings file: $SETTINGS_FILE"

# Check if settings file exists
if [ ! -f "$SETTINGS_FILE" ]; then
    echo -e "${YELLOW}[WARNING]${NC} Settings file not found, creating from base"
    cp api/callcentersite/callcentersite/settings/base.py "$SETTINGS_FILE"
fi

# Create backup
cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup-$(date +%Y%m%d-%H%M%S)"

# Add Cassandra logging configuration
cat >> "$SETTINGS_FILE" <<'EOF'

# ============================================================================
# Cassandra Centralized Logging Configuration
# ============================================================================

CASSANDRA_LOGGING = {
    'enabled': True,
    'contact_points': [
        'cassandra-1.internal',  # Update with your Cassandra nodes
        'cassandra-2.internal',
        'cassandra-3.internal',
    ],
    'keyspace': 'logging',
    'batch_size': 100,
    'batch_timeout': 1.0,
    'queue_maxsize': 10000,
}

# Update LOGGING configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'cassandra': {
            'level': 'INFO',
            'class': 'scripts.logging.cassandra_handler.CassandraLogHandler',
            'contact_points': CASSANDRA_LOGGING['contact_points'],
            'keyspace': CASSANDRA_LOGGING['keyspace'],
            'batch_size': CASSANDRA_LOGGING['batch_size'],
            'batch_timeout': CASSANDRA_LOGGING['batch_timeout'],
            'queue_maxsize': CASSANDRA_LOGGING['queue_maxsize'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'cassandra'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'cassandra'],
            'level': 'ERROR',
            'propagate': False,
        },
        'callcentersite': {
            'handlers': ['console', 'file', 'cassandra'],
            'level': 'INFO',
            'propagate': False,
        },
        # App-specific loggers
        'analytics': {
            'handlers': ['cassandra'],
            'level': 'INFO',
            'propagate': False,
        },
        'etl': {
            'handlers': ['cassandra'],
            'level': 'INFO',
            'propagate': False,
        },
        'reports': {
            'handlers': ['cassandra'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ensure scripts.logging is in Python path
import sys
import os
sys.path.insert(0, os.path.join(BASE_DIR, '../../scripts'))
EOF

echo -e "${GREEN}[SUCCESS]${NC} Django settings configured for Cassandra logging"
echo -e "${YELLOW}[NEXT STEPS]${NC}"
echo -e "  1. Update CASSANDRA_LOGGING['contact_points'] with your actual Cassandra node IPs"
echo -e "  2. Create /var/log/iact/ directory: sudo mkdir -p /var/log/iact && sudo chown www-data:www-data /var/log/iact"
echo -e "  3. Restart Django: sudo systemctl restart iact-django"
echo -e "  4. Test logging: python manage.py shell -c \"import logging; logging.getLogger('analytics').info('Test log')\""
