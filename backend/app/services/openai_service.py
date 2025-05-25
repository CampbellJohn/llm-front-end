import logging
import time
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError, APIConnectionError
from pydantic import ValidationError

from app.api.v1.models.openai_models import Message
from app.core.config import settings

# Set up logger
logger = logging.getLogger(__name__)

# Global client instance
_client = None

def get_openai_client() -> AsyncOpenAI:
    """
    Get or create the OpenAI client.
    
    Returns:
        AsyncOpenAI: An instance of the OpenAI client.
        
    Raises:
        RuntimeError: If client initialization fails
    """
    global _client
    
    log_context = {"operation": "get_openai_client"}
    
    if _client is not None:
        logger.debug("Returning existing OpenAI client instance", extra=log_context)
        return _client
        
    logger.debug("Initializing new OpenAI client", extra=log_context)
    
    try:
        # Log configuration (safely, without exposing sensitive data)
        config = {
            "has_api_key": bool(settings.OPENAI_API_KEY),
            "timeout": getattr(settings, 'OPENAI_API_TIMEOUT', 30.0),
            "api_base": getattr(settings, 'OPENAI_API_BASE', 'default')
        }
        logger.debug("OpenAI client configuration", extra={"config": config, **log_context})
        
        _client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=getattr(settings, 'OPENAI_API_TIMEOUT', 30.0),
            max_retries=3
        )
        
        logger.info("Successfully initialized OpenAI client", extra=log_context)
        return _client
        
    except ValidationError as e:
        error_msg = "Invalid configuration for OpenAI client"
        logger.error(
            error_msg,
            extra={"error": str(e), "config": config, **log_context},
            exc_info=True
        )
        raise RuntimeError(f"{error_msg}: {str(e)}") from e
        
    except Exception as e:
        error_msg = "Failed to initialize OpenAI client"
        logger.error(
            error_msg,
            extra={"error": str(e), **log_context},
            exc_info=True
        )
        raise RuntimeError(f"{error_msg}: {str(e)}") from e

async def get_openai_response(
    messages: List[Message],
    model: str,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    stream: bool = False,
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get a response from the OpenAI API with enhanced logging and error handling.
    
    Args:
        messages: List of message objects for the conversation
        model: The model to use for completion
        max_tokens: Maximum number of tokens to generate (default: 4000)
        temperature: Sampling temperature (0-2, default: 0.7)
        stream: Whether to stream the response (default: False)
        request_id: Optional request ID for tracing
        **kwargs: Additional arguments to pass to the API
        
    Returns:
        Dict containing the response content and usage information
        
    Raises:
        ValueError: If input validation fails
        RateLimitError: For rate limiting errors
        APITimeoutError: For request timeouts
        APIConnectionError: For connection issues
        APIError: For general API errors
        Exception: For any other unexpected errors
    """
    """
    Get a response from the OpenAI API.
    
    Args:
        messages: List of message objects for the conversation
        model: The model to use for completion
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0-2)
        stream: Whether to stream the response
        request_id: Optional request ID for tracing
        **kwargs: Additional arguments to pass to the API
        
    Returns:
        Dict containing the response content and usage information
        
    Raises:
        APIError: For general API errors
        RateLimitError: For rate limiting errors
        APITimeoutError: For request timeouts
        APIConnectionError: For connection issues
        Exception: For any other errors
    """
    start_time = time.perf_counter()
    request_id = request_id or f"openai_req_{int(time.time() * 1000)}"
    
    # Prepare log context with request metadata
    log_context = {
        "operation": "get_openai_response",
        "request_id": request_id,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
        "message_count": len(messages),
        "has_custom_kwargs": bool(kwargs)
    }
    
    # Log additional kwargs (excluding any that might contain sensitive data)
    if kwargs:
        safe_kwargs = {k: v for k, v in kwargs.items() 
                      if not any(skip in k.lower() for skip in ['key', 'token', 'secret'])}
        if safe_kwargs:
            log_context["custom_args"] = safe_kwargs
    
    # Input validation
    if not messages:
        error_msg = "Empty messages"
        logger.error(error_msg, extra=log_context)
        raise ValueError(error_msg)
        
    if not isinstance(messages, list):
        error_msg = f"Messages must be a list, got {type(messages).__name__}"
        logger.error(error_msg, extra=log_context)
        raise ValueError(error_msg)
        
    try:
        client = get_openai_client()
    except Exception as e:
        logger.critical("Failed to get OpenAI client", extra={"error": str(e), **log_context}, exc_info=True)
        raise
    
    try:
        # Log the request with message summaries
        message_summaries = [
            {
                "role": msg.role,
                "content_length": len(msg.content or ""),
                "content_preview": (msg.content[:100] + '...') if msg.content and len(msg.content) > 100 else msg.content
            } for msg in messages
        ]
        
        logger.info(
            "Sending request to OpenAI API",
            extra={
                **log_context,
                "messages": message_summaries,
                "total_content_length": sum(len(msg.content or '') for msg in messages)
            }
        )
        
        # Validate and convert messages
        openai_messages = []
        for i, msg in enumerate(messages):
            if not isinstance(msg, Message):
                error_msg = f"Invalid message type at index {i}: {type(msg).__name__}"
                logger.error(error_msg, extra={"message_index": i, **log_context})
                raise ValueError(error_msg)
                
            if not msg.role or not isinstance(msg.role, str):
                error_msg = f"Invalid role at message index {i}: {msg.role}"
                logger.error(error_msg, extra={"message_index": i, **log_context})
                raise ValueError(error_msg)
                
            openai_messages.append({"role": msg.role, "content": msg.content or ""})
        
        if stream:
            logger.debug("Streaming response requested, preparing streaming response container", extra=log_context)
            return {
                "content": "",
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "stream": True
            }
            
        # Log API call details
        api_call_log = {
            **log_context,
            "model": model,
            "message_count": len(openai_messages),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "has_stream": stream
        }
        logger.debug("Preparing OpenAI API call", extra=api_call_log)
        
        # Prepare API call parameters
        api_params = {
            "model": model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # Log the actual API call (without sensitive data)
        safe_params = {k: v for k, v in api_params.items() 
                      if k not in ['api_key', 'token', 'secret']}
        logger.debug("Calling OpenAI API", extra={
            **log_context,
            "api_params": safe_params,
            "param_count": len(api_params)
        })
        
        # Make the API call with timing
        api_start_time = time.perf_counter()
        try:
            response = await client.chat.completions.create(**api_params)
            api_duration = time.perf_counter() - api_start_time
            
            # Log API call duration
            logger.debug(
                "OpenAI API call completed",
                extra={
                    **log_context,
                    "api_duration_sec": round(api_duration, 3),
                    "status": "success"
                }
            )
            
        except Exception as api_error:
            api_duration = time.perf_counter() - api_start_time
            logger.error(
                "OpenAI API call failed",
                extra={
                    **log_context,
                    "api_duration_sec": round(api_duration, 3),
                    "status": "failed",
                    "error": str(api_error)
                },
                exc_info=True
            )
            raise
        
        # Process the response
        try:
            response_content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": response.model
            }
            
            # Calculate total processing time
            total_duration = time.perf_counter() - start_time
            
            # Log successful response with performance metrics
            logger.info(
                "Successfully received response from OpenAI API",
                extra={
                    **log_context,
                    "response_length": len(response_content or ""),
                    "usage": usage,
                    "processing_time_sec": round(total_duration, 3),
                    "api_time_sec": round(api_duration, 3),
                    "overhead_sec": round(total_duration - api_duration, 3),
                    "tokens_per_second": round(usage["total_tokens"] / total_duration, 1) if total_duration > 0 else 0
                }
            )
            
            return {
                "content": response_content,
                "usage": usage,
                "model": response.model,
                "id": response.id,
                "created": response.created
            }
            
        except Exception as process_error:
            logger.error(
                "Failed to process OpenAI API response",
                extra={
                    **log_context,
                    "error": str(process_error),
                    "response_type": type(response).__name__
                },
                exc_info=True
            )
            raise RuntimeError("Failed to process OpenAI API response") from process_error
        
    except RateLimitError as e:
        duration = time.perf_counter() - start_time
        error_msg = "OpenAI API rate limit exceeded"
        logger.error(
            error_msg,
            extra={
                **log_context,
                "error_type": "RateLimitError",
                "error": str(e),
                "processing_time_sec": round(duration, 3),
                "suggestion": "Consider implementing exponential backoff or reducing request frequency"
            },
            exc_info=True
        )
        # Re-raise with additional context
        e.duration = duration
        raise
        
    except APITimeoutError as e:
        duration = time.perf_counter() - start_time
        error_msg = "OpenAI API request timed out"
        logger.error(
            error_msg,
            extra={
                **log_context,
                "error_type": "APITimeoutError",
                "error": str(e),
                "processing_time_sec": round(duration, 3),
                "timeout_seconds": getattr(settings, 'OPENAI_API_TIMEOUT', 30.0),
                "suggestion": "Consider increasing the timeout or checking your network connection"
            },
            exc_info=True
        )
        # Add context to the exception
        e.duration = duration
        raise
        
    except APIConnectionError as e:
        duration = time.perf_counter() - start_time
        error_msg = "Failed to connect to OpenAI API"
        logger.error(
            error_msg,
            extra={
                **log_context,
                "error_type": "APIConnectionError",
                "error": str(e),
                "processing_time_sec": round(duration, 3),
                "suggestion": "Check your internet connection and OpenAI API status"
            },
            exc_info=True
        )
        # Add context to the exception
        e.duration = duration
        raise
        
    except APIError as e:
        duration = time.perf_counter() - start_time
        error_msg = f"OpenAI API error: {str(e)}"
        logger.error(
            error_msg,
            extra={
                **log_context,
                "error_type": "APIError",
                "error": str(e),
                "status_code": getattr(e, 'status_code', None),
                "code": getattr(e, 'code', None),
                "param": getattr(e, 'param', None),
                "processing_time_sec": round(duration, 3)
            },
            exc_info=True
        )
        # Add context to the exception
        e.duration = duration
        raise
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        error_type = type(e).__name__
        error_msg = f"Unexpected {error_type} calling OpenAI API: {str(e)}"
            
        logger.critical(
            error_msg,
            extra={
                **log_context,
                "error": str(e),
                "error_type": error_type,
                "processing_time_sec": round(duration, 3),
                "stack_trace": True  # Ensure stack trace is included
            },
            exc_info=True
        )
        # Wrap in a more specific exception if it's not already one
        if not isinstance(e, (APIError, APITimeoutError, RateLimitError, APIConnectionError)):
            raise RuntimeError(error_msg) from e
        raise
        
    # Process the response
    try:
        response_content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "model": response.model
        }
        
        # Calculate total processing time
        total_duration = time.perf_counter() - start_time
        
        # Log successful response with performance metrics
        logger.info(
            "Successfully received response from OpenAI API",
            extra={
                **log_context,
                "response_length": len(response_content or ""),
                "usage": usage,
                "processing_time_sec": round(total_duration, 3),
                "api_time_sec": round(api_duration, 3),
                "overhead_sec": round(total_duration - api_duration, 3),
                "tokens_per_second": round(usage["total_tokens"] / total_duration, 1) if total_duration > 0 else 0
            }
        )
        
        return {
            "content": response_content,
            "usage": usage,
            "model": response.model,
            "id": response.id,
            "created": response.created
        }
        
    except Exception as process_error:
        logger.error(
            "Failed to process OpenAI API response",
            extra={
                **log_context,
                "error": str(process_error),
                "response_type": type(response).__name__
            },
            exc_info=True
        )
        raise RuntimeError("Failed to process OpenAI API response") from process_error