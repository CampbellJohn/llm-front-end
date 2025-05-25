import logging
import logging.config
import logging.handlers
import json
import os
from datetime import datetime
from typing import Any, Dict
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Ensure log directory exists
LOG_DIR = "/var/log/app"
os.makedirs(LOG_DIR, exist_ok=True)

class JSONFormatter(logging.Formatter):    
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
        if hasattr(record, 'path'):
            log_record["path"] = record.path
        if hasattr(record, 'method'):
            log_record["method"] = record.method
        if hasattr(record, 'status_code'):
            log_record["status_code"] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_record["duration_ms"] = record.duration_ms
        
        # Add any extra fields
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
        if hasattr(record, 'props') and isinstance(record.props, dict):
            # Filter out non-serializable objects from props
            serializable_props = {}
            for key, value in record.props.items():
                try:
                    # Test if it's serializable
                    json.dumps({key: value})
                    serializable_props[key] = value
                except TypeError:
                    # If not serializable, convert to string
                    serializable_props[key] = f"<non-serializable: {type(value).__name__}>"
            log_record.update(serializable_props)
            
        try:
            return json.dumps(log_record)
        except TypeError:
            # If we still have serialization issues, create a simpler record
            safe_record = {
                "timestamp": log_record.get("timestamp", ""),
                "level": log_record.get("level", ""),
                "logger": log_record.get("logger", ""),
                "message": log_record.get("message", "<non-serializable log record>"),
                "error": "Log record contained non-serializable objects"
            }
            return json.dumps(safe_record)

def setup_logging() -> None:
    """Configure logging for the application."""
    # File handler with rotation (100MB per file, keep 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Console handler for local development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set log levels for specific loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        logger = logging.getLogger("fastapi")
        
        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "props": {
                    "query_params": dict(request.query_params),
                    "headers": {k: v for k, v in request.headers.items() if k.lower() not in ['authorization', 'cookie']}
                }
            }
        )
        
        # Process request and time it
        import time
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": round(process_time, 2)
                }
            )
            
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": round(process_time, 2),
                    "exc_info": True
                },
                exc_info=True
            )
            raise

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
