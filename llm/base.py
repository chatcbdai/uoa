# llm/base.py - Abstract base class for LLM providers
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Message:
    role: str  # "system", "user", or "assistant"
    content: str

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    request_id: Optional[str] = None

class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_with_tools(
        self,
        messages: List[Message],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate a response with tool/function calling"""
        pass