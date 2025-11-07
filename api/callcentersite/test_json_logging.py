#!/usr/bin/env python
"""
Test script para validar JSON logging.

TASK-010: Logging Estructurado JSON
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings.development')
sys.path.insert(0, '/home/user/IACT---project/api/callcentersite')

django.setup()

import logging
from callcentersite.logging import get_logger_with_context

def test_basic_json_logging():
    """Test basic JSON logging"""
    print("=" * 80)
    print("TEST 1: Basic JSON Logging")
    print("=" * 80)

    logger = logging.getLogger('callcentersite')
    logger.info('Test message - basic JSON logging')
    logger.warning('Warning message - test')
    logger.error('Error message - test')

    print("✓ Basic logs written\n")


def test_context_logging():
    """Test logging with context"""
    print("=" * 80)
    print("TEST 2: Logging with Context")
    print("=" * 80)

    logger = logging.getLogger('callcentersite')
    logger.info('User login attempt', extra={
        'request_id': 'req-test-123',
        'user_id': 42,
        'session_id': 'sess-abc-def',
        'ip_address': '192.168.1.100'
    })

    print("✓ Context logs written\n")


def test_logger_adapter():
    """Test ContextLoggerAdapter"""
    print("=" * 80)
    print("TEST 3: Logger Adapter with Auto-Context")
    print("=" * 80)

    logger = get_logger_with_context(
        'callcentersite.views',
        request_id='req-adapter-456',
        user_id=99
    )

    logger.info('Processing request')
    logger.info('Request completed', extra={'duration_ms': 125})

    print("✓ Adapter logs written\n")


def test_exception_logging():
    """Test exception logging"""
    print("=" * 80)
    print("TEST 4: Exception Logging")
    print("=" * 80)

    logger = logging.getLogger('callcentersite')

    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.exception('Division by zero', extra={
            'request_id': 'req-error-789',
            'user_id': 1
        })

    print("✓ Exception logs written\n")


def verify_log_file():
    """Verify log file was created and contains valid JSON"""
    print("=" * 80)
    print("VERIFICATION: Check Log Files")
    print("=" * 80)

    log_file = '/var/log/iact/app.json.log'

    if os.path.exists(log_file):
        print(f"✓ Log file exists: {log_file}")

        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"✓ Log entries written: {len(lines)}")

            if lines:
                print("\n--- Sample log entry (last) ---")
                import json
                try:
                    log_entry = json.loads(lines[-1])
                    print(json.dumps(log_entry, indent=2))
                    print("✓ Valid JSON format")
                except json.JSONDecodeError as e:
                    print(f"✗ Invalid JSON: {e}")
    else:
        print(f"✗ Log file not found: {log_file}")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("TASK-010: JSON Structured Logging Test")
    print("=" * 80 + "\n")

    test_basic_json_logging()
    test_context_logging()
    test_logger_adapter()
    test_exception_logging()
    verify_log_file()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80 + "\n")
