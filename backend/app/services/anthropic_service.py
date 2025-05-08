from typing import List, Dict, Any, Optional
import anthropic
from app.api.models import Message
from app.core.config import settings

async def get_anthropic_response(
    messages: List[Message],
    model: str,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Get a response from the Anthropic Claude API.
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    # Convert our internal message format to Anthropic's format
    anthropic_messages = []
    
    for msg in messages:
        anthropic_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    try:
        if stream:
            # Handle streaming response
            response_content = ""
            with client.messages.stream(
                model=model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature
            ) as stream:
                for text in stream.text_stream:
                    response_content += text
                    # In a real app, you would yield this to the client
                
                usage = {
                    "input_tokens": stream.usage.input_tokens,
                    "output_tokens": stream.usage.output_tokens
                }
        else:
            # Handle normal response
            response = client.messages.create(
                model=model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_content = response.content[0].text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        
        return {
            "content": response_content,
            "usage": usage
        }
        
    except Exception as e:
        # Log the error and re-raise
        print(f"Error calling Anthropic API: {str(e)}")
        raise