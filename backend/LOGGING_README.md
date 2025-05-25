# Logging Strategy

This document outlines the logging strategy for the FastAPI backend application.

## Overview

We use Python's built-in `logging` module with the following configuration:

- **Log Format**: JSON-structured logs for easy parsing and analysis
- **Log Levels**: Standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Log Rotation**: 100MB per file, keeping 5 backup files
- **Log Location**: `/var/log/app/` (mounted as a Docker volume)

## Log Levels

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems.
- **INFO**: Confirmation that things are working as expected.
- **WARNING**: An indication that something unexpected happened, but the software is still working.
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function.
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running.

## Log Structure

Each log entry is a JSON object with the following structure:

```json
{
    "timestamp": "2025-05-25T20:38:37.123456",
    "level": "INFO",
    "logger": "app.main",
    "message": "Application started",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v1/endpoint",
    "method": "GET",
    "status_code": 200,
    "duration_ms": 123.45
}
```

## Implementation

Logging is configured in `app/core/logging.py` and integrated into the FastAPI application lifecycle. The configuration includes:

1. A file handler that writes JSON-formatted logs to `/var/log/app/app.log`
2. Rotating file handler with a maximum size of 100MB per file
3. Standard output for local development
4. Structured logging with context (request ID, path, method, etc.)

## Adding Logging to Your Code

1. Import the logger:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Use appropriate log levels:
   ```python
   logger.debug("Debug information")
   logger.info("Informational message")
   logger.warning("Warning message")
   logger.error("Error message")
   logger.critical("Critical error")
   ```

3. Include structured data:
   ```python
   logger.info("User logged in", extra={"user_id": user_id, "ip": request.client.host})
   ```

## Viewing Logs

### In Development
Logs are written to both the console and the log file.

### In Production
Logs are written to `/var/log/app/app.log` and can be viewed using standard Linux tools:

```bash
# View logs in real-time
tail -f /var/log/app/app.log

# Search for errors
grep '"level": "ERROR"' /var/log/app/app.log

# View logs with jq for pretty-printing
cat /var/log/app/app.log | jq .
```

## Log Rotation

Logs are automatically rotated when they reach 100MB. Up to 5 backup files are kept with numeric extensions (.1, .2, etc.).

## Best Practices

1. Use descriptive log messages
2. Include relevant context in the extra dictionary
3. Choose the appropriate log level
4. Be mindful of logging sensitive information
5. Use structured logging for better querying and analysis
