# llm/anthropic_client.py - Anthropic Claude client implementation
import os
from typing import List, Dict, Any
import anthropic
from .base import BaseLLM, Message, LLMResponse
from config import config

class AnthropicClient(BaseLLM):
    """Anthropic Claude client using latest SDK"""
    
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=config.llm.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.default_model = config.llm.default_model or "claude-sonnet-4-20250514"
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResponse:
        """Generate response using Anthropic API"""
        # Separate system message from user/assistant messages
        system_message = None
        claude_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        if stream:
            return await self._generate_stream(
                claude_messages, system_message, temperature, max_tokens
            )
        else:
            response = await self.client.messages.create(
                model=self.default_model,
                system=system_message,
                messages=claude_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract text content from response
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
            
            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                request_id=response.id
            )
    
    async def _generate_stream(
        self,
        messages: List[Dict[str, str]],
        system: str,
        temperature: float,
        max_tokens: int
    ):
        """Generate streaming response"""
        async with self.client.messages.stream(
            model=self.default_model,
            system=system,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    async def generate_with_tools(
        self,
        messages: List[Message],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response with tool use"""
        # Convert to Claude format
        system_message = None
        claude_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        response = await self.client.beta.tools.messages.create(
            model=self.default_model,
            system=system_message,
            messages=claude_messages,
            tools=tools,
            temperature=temperature
        )
        
        # Process tool use if present
        content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content += block.text
        
        return LLMResponse(
            content=content,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            request_id=response.id
        )