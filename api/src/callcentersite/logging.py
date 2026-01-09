"""
Custom logging formatters para el proyecto IACT.

TASK-010: Logging Estructurado JSON
- JSONStructuredFormatter: Formatter custom con contexto enriquecido
- Layer 2: Application logs (preparado para Cassandra)
- AI-parseable format
"""

import json
import logging
from datetime import datetime
from typing import Any


class JSONStructuredFormatter(logging.Formatter):
    """
    Formatter para logs en formato JSON estructurado.

    Incluye contexto enriquecido:
    - timestamp (ISO 8601 format)
    - level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - logger name
    - message
    - module, function, line
    - process_id, thread_id
    - request_id (if available)
    - user_id (if available)
    - session_id (if available)
    - exception (if present)

    Uso:
        logger = logging.getLogger('callcentersite')
        logger.info('User login', extra={
            'request_id': 'req-123',
            'user_id': 42,
            'session_id': 'sess-abc'
        })
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: LogRecord instance

        Returns:
            JSON string
        """
        # Base log data
        log_data: dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
            'thread_name': record.threadName,
        }

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id

        # Add pathname for debugging
        if record.pathname:
            log_data['pathname'] = record.pathname

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info),
            }

        # Add any extra fields passed via extra parameter
        # Skip internal fields
        skip_fields = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'message', 'pathname', 'process', 'processName',
            'relativeCreated', 'thread', 'threadName', 'exc_info',
            'exc_text', 'stack_info', 'request_id', 'user_id', 'session_id'
        }

        for key, value in record.__dict__.items():
            if key not in skip_fields and not key.startswith('_'):
                log_data[key] = value

        # Return JSON string
        return json.dumps(log_data, default=str)


class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter que agrega contexto automaticamente a todos los logs.

    Uso:
        logger = logging.getLogger('callcentersite')
        logger = ContextLoggerAdapter(logger, {
            'request_id': 'req-123',
            'user_id': 42
        })
        logger.info('User action')  # Automaticamente incluye request_id y user_id
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        Process log message and kwargs.

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            Tuple of (msg, kwargs) with extra context
        """
        # Merge adapter context with message extra
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs


def get_logger_with_context(name: str, **context: Any) -> ContextLoggerAdapter:
    """
    Get logger with automatic context.

    Args:
        name: Logger name
        **context: Context to add to all logs

    Returns:
        ContextLoggerAdapter instance

    Example:
        logger = get_logger_with_context(
            'callcentersite.views',
            request_id='req-123',
            user_id=42
        )
        logger.info('Processing request')
    """
    base_logger = logging.getLogger(name)
    return ContextLoggerAdapter(base_logger, context)
