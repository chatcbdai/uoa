# llm/__init__.py
from .base import BaseLLM, Message, LLMResponse
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .prompts import (
    WEB_ASSISTANT_SYSTEM_PROMPT,
    TASK_PLANNING_PROMPT,
    WEB_ACTION_MAPPING_PROMPT
)

__all__ = [
    "BaseLLM",
    "Message",
    "LLMResponse",
    "OpenAIClient",
    "AnthropicClient",
    "WEB_ASSISTANT_SYSTEM_PROMPT",
    "TASK_PLANNING_PROMPT",
    "WEB_ACTION_MAPPING_PROMPT"
]