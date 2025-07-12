# llm/openai_client.py - OpenAI client implementation with latest 2025 patterns
import os
from typing import List, Dict, Any, AsyncIterator
from openai import AsyncOpenAI
import openai
from .base import BaseLLM, Message, LLMResponse
from config import config

class OpenAIClient(BaseLLM):
    """OpenAI client using latest SDK patterns"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.llm.openai_api_key or os.environ.get("OPENAI_API_KEY")
        )
        self.default_model = config.llm.default_model or "gpt-4o"
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResponse:
        """Generate response using OpenAI API"""
        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            if stream:
                # Streaming response
                return await self._generate_stream(
                    openai_messages, temperature, max_tokens
                )
            else:
                # Regular response
                response = await self.client.chat.completions.create(
                    model=self.default_model,
                    messages=openai_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    tokens_used=response.usage.total_tokens,
                    request_id=response.id
                )
                
        except openai.APIConnectionError as e:
            raise Exception(f"Failed to connect to OpenAI: {e}")
        except openai.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {e}")
        except openai.APIStatusError as e:
            raise Exception(f"OpenAI API error: {e.status_code} - {e.response}")
    
    async def _generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[str]:
        """Generate streaming response"""
        stream = await self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate_with_tools(
        self,
        messages: List[Message],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response with function calling"""
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=openai_messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature
        )
        
        # Handle tool calls if present
        if response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            # Process tool calls here
            pass
        
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            tokens_used=response.usage.total_tokens,
            request_id=response.id
        )