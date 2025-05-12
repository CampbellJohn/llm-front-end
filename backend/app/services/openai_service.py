from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.api.v1.models.openai_models import Message
from app.core.config import settings

async def get_openai_response(
    messages: List[Message],
    model: str,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Get a response from the OpenAI API.
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Convert our internal message format to OpenAI's format
    openai_messages = []
    
    for msg in messages:
        openai_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    try:
        if stream:
            # Handle streaming response
            response_content = ""
            response_stream = await client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    response_content += chunk.choices[0].delta.content
                    # In a real app, you would yield this to the client
            
            # OpenAI streaming doesn't return token usage, so we need to estimate
            usage = {
                "prompt_tokens": len("".join([m.content for m in messages])) // 4,  # Rough estimate
                "completion_tokens": len(response_content) // 4  # Rough estimate
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