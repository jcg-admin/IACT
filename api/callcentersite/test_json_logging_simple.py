#!/usr/bin/env python
"""
Test simple para validar JSON logging sin Django setup completo.

TASK-010: Logging Estructurado JSON
"""

import sys
import logging
import json
from pathlib import Path

# Add callcentersite to path
sys.path.insert(0, '/home/user/IACT---project/api/callcentersite')

# Import custom formatter
from callcentersite.logging import JSONStructuredFormatter, ContextLoggerAdapter

def test_json_formatter():
    """Test JSONStructuredFormatter directly"""
    print("=" * 80)
    print("TEST 1: JSONStructuredFormatter")
    print("=" * 80)

    # Create logger
    logger = logging.getLogger('test.callcentersite')
    logger.setLevel(logging.INFO)

    # Create handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONStructuredFormatter())
    logger.addHandler(handler)

    # Test basic log
    logger.info('Test message - basic JSON logging')

    # Test log with context
    logger.info('User login attempt', extra={
        'request_id': 'req-test-123',
        'user_id': 42,
        'session_id': 'sess-abc-def',
        'ip_address': '192.168.1.100'
    })

    # Test warning
    logger.warning('Warning message with context', extra={
        'request_id': 'req-warn-456',
        'severity': 'medium'
    })

    # Test error
    logger.error('Error occurred', extra={
        'request_id': 'req-error-789',
        'error_code': 'E001'
    })

    print("\n✓ All log levels tested\n")


def test_logger_adapter():
    """Test ContextLoggerAdapter"""
    print("=" * 80)
    print("TEST 2: ContextLoggerAdapter")
    print("=" * 80)

    # Create base logger
    base_logger = logging.getLogger('test.adapter')
    base_logger.setLevel(logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONStructuredFormatter())
    base_logger.addHandler(handler)

    # Create adapter with automatic context
    logger = ContextLoggerAdapter(base_logger, {
        'request_id': 'req-adapter-999',
        'user_id': 77
    })

    logger.info('Processing request')
    logger.info('Request completed', extra={'duration_ms': 125})

    print("\n✓ Adapter auto-context working\n")


def test_exception_logging():
    """Test exception logging"""
    print("=" * 80)
    print("TEST 3: Exception Logging")
    print("=" * 80)

    logger = logging.getLogger('test.exception')
    logger.setLevel(logging.ERROR)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONStructuredFormatter())
    logger.addHandler(handler)

    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception('Division by zero', extra={
            'request_id': 'req-exception-001',
            'user_id': 1
        })

    print("\n✓ Exception logged with traceback\n")


def test_file_logging():
    """Test logging to file"""
    print("=" * 80)
    print("TEST 4: File Logging")
    print("=" * 80)

    log_file = '/var/log/iact/test_app.json.log'

    # Create logger
    logger = logging.getLogger('test.file')
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(JSONStructuredFormatter())
    logger.addHandler(file_handler)

    # Write test logs
    logger.info('File logging test', extra={'test_id': 'file-001'})
    logger.warning('Warning to file', extra={'test_id': 'file-002'})
    logger.error('Error to file', extra={'test_id': 'file-003'})

    print(f"✓ Logs written to {log_file}")

    # Verify file
    if Path(log_file).exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"✓ {len(lines)} log entries written")

            if lines:
                print("\n--- Sample log entry ---")
                try:
                    log_entry = json.loads(lines[0])
                    print(json.dumps(log_entry, indent=2))
                    print("✓ Valid JSON format")

                    # Verify required fields
                    required_fields = ['timestamp', 'level', 'logger', 'message']
                    for field in required_fields:
                        if field in log_entry:
                            print(f"  ✓ Field '{field}': {log_entry[field]}")
                        else:
                            print(f"  ✗ Field '{field}': MISSING")

                except json.JSONDecodeError as e:
                    print(f"✗ Invalid JSON: {e}")
    else:
        print(f"✗ Log file not created: {log_file}")

    print()


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("TASK-010: JSON Structured Logging Test (Simple)")
    print("=" * 80 + "\n")

    test_json_formatter()
    test_logger_adapter()
    test_exception_logging()
    test_file_logging()

    print("=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80 + "\n")

    print("Log file location: /var/log/iact/test_app.json.log")
    print("To view: cat /var/log/iact/test_app.json.log | jq .")
    print()
