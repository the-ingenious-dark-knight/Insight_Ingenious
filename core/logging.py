"""
Simple logging configuration for the AutoGen FastAPI template.

Provides structured logging without unnecessary complexity.
"""

import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime

from .config import get_config


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """Simple text formatter for human-readable logs."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging() -> None:
    """
    Setup logging configuration based on config settings.
    
    Configures the root logger with appropriate handlers and formatters.
    """
    config = get_config()
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on configuration
    if config.logging.format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = SimpleFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Suppress some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding structured data to log records.
    
    Allows easy addition of context data to log messages.
    """
    
    def process(self, msg: Any, kwargs: Dict[str, Any]) -> tuple:
        """Process the logging call to add extra data."""
        extra_data = kwargs.pop("extra_data", {})
        if self.extra:
            extra_data.update(self.extra)
        
        if extra_data:
            kwargs["extra"] = {"extra_data": extra_data}
        
        return msg, kwargs


def get_structured_logger(name: str, **context) -> LoggerAdapter:
    """
    Get a structured logger with default context.
    
    Args:
        name: Logger name
        **context: Default context data to include in all log messages
        
    Returns:
        LoggerAdapter instance with context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)
