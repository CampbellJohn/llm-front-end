from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import AsyncOpenAI
from app.api.v1.models.openai_models import Message
from app.core.config import settings

# Global client instance
_client = None

def get_openai_client() -> AsyncOpenAI:
    """Get or create the OpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client

async def get_openai_response(
    messages: List[Message],
    model: str,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Get a response from the OpenAI API.
    For streaming responses, this just returns an empty response as the streaming
    is handled by the route handler directly.
    """
    client = get_openai_client()
    
    # Convert our internal message format to OpenAI's format
    openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    try:
        if stream:
            # For streaming, we'll handle it in the route
            return {
                "content": "",
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
        else:
            # Handle normal response
            response = await client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return {
            "content": response_content,
            "usage": usage
        }
        
    except Exception as e:
        # Log the error and re-raise
        print(f"Error calling OpenAI API: {str(e)}")
        raise