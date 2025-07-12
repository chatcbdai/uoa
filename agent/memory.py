# agent/memory.py - Context and conversation memory
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from llm.base import Message
from llm.prompts import WEB_ASSISTANT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Single memory entry"""
    timestamp: datetime
    type: str  # "user", "assistant", "system", "action", "result"
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationMemory:
    """Manages conversation context and memory"""
    
    def __init__(self, max_messages: int = 20, max_context_length: int = 4000):
        self.max_messages = max_messages
        self.max_context_length = max_context_length
        self.messages: List[Message] = []
        self.memory_entries: List[MemoryEntry] = []
        self.context_summary: Optional[str] = None
    
    def add_user_message(self, content: str):
        """Add a user message to memory"""
        self.messages.append(Message(role="user", content=content))
        self.memory_entries.append(
            MemoryEntry(
                timestamp=datetime.now(),
                type="user",
                content=content
            )
        )
        self._trim_memory()
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to memory"""
        self.messages.append(Message(role="assistant", content=content))
        self.memory_entries.append(
            MemoryEntry(
                timestamp=datetime.now(),
                type="assistant",
                content=content
            )
        )
        self._trim_memory()
    
    def add_system_message(self, content: str):
        """Add a system message to memory"""
        self.messages.append(Message(role="system", content=content))
        self.memory_entries.append(
            MemoryEntry(
                timestamp=datetime.now(),
                type="system",
                content=content
            )
        )
    
    def add_action(self, action: Dict[str, Any]):
        """Add an action to memory"""
        self.memory_entries.append(
            MemoryEntry(
                timestamp=datetime.now(),
                type="action",
                content=action,
                metadata={"action_type": action.get("action")}
            )
        )
    
    def add_result(self, result: Any, action_type: str = None):
        """Add an action result to memory"""
        self.memory_entries.append(
            MemoryEntry(
                timestamp=datetime.now(),
                type="result",
                content=result,
                metadata={"action_type": action_type} if action_type else {}
            )
        )
    
    def get_context(self) -> List[Message]:
        """Get conversation context for LLM"""
        # Always start with system prompt
        context = [Message(role="system", content=WEB_ASSISTANT_SYSTEM_PROMPT)]
        
        # Add summary of older context if available
        if self.context_summary:
            context.append(
                Message(
                    role="system", 
                    content=f"Previous conversation summary: {self.context_summary}"
                )
            )
        
        # Add recent messages
        context.extend(self.messages[-self.max_messages:])
        
        return context
    
    def get_recent_actions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent actions from memory"""
        actions = []
        for entry in reversed(self.memory_entries):
            if entry.type == "action":
                actions.append(entry.content)
                if len(actions) >= limit:
                    break
        return list(reversed(actions))
    
    def get_recent_results(self, limit: int = 5) -> List[Any]:
        """Get recent results from memory"""
        results = []
        for entry in reversed(self.memory_entries):
            if entry.type == "result":
                results.append({
                    "content": entry.content,
                    "action_type": entry.metadata.get("action_type"),
                    "timestamp": entry.timestamp
                })
                if len(results) >= limit:
                    break
        return list(reversed(results))
    
    def search_memory(self, query: str, entry_type: str = None) -> List[MemoryEntry]:
        """Search memory for specific content"""
        results = []
        query_lower = query.lower()
        
        for entry in self.memory_entries:
            # Filter by type if specified
            if entry_type and entry.type != entry_type:
                continue
            
            # Search in content
            content_str = str(entry.content).lower()
            if query_lower in content_str:
                results.append(entry)
        
        return results
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.memory_entries:
            return "No conversation history."
        
        summary_parts = []
        
        # Count message types
        user_count = sum(1 for e in self.memory_entries if e.type == "user")
        action_count = sum(1 for e in self.memory_entries if e.type == "action")
        
        summary_parts.append(f"Conversation with {user_count} user messages and {action_count} actions.")
        
        # Add recent topics
        recent_user_messages = [
            e.content for e in self.memory_entries[-5:] 
            if e.type == "user"
        ]
        if recent_user_messages:
            summary_parts.append(f"Recent topics: {', '.join(recent_user_messages[:3])}")
        
        return " ".join(summary_parts)
    
    def _trim_memory(self):
        """Trim memory to stay within limits"""
        # Trim messages list
        if len(self.messages) > self.max_messages:
            # Keep system messages and trim older user/assistant messages
            system_messages = [m for m in self.messages if m.role == "system"]
            other_messages = [m for m in self.messages if m.role != "system"]
            
            # Keep recent messages
            self.messages = system_messages + other_messages[-self.max_messages:]
        
        # Check total context length
        total_length = sum(len(msg.content) for msg in self.messages)
        if total_length > self.max_context_length:
            # Create summary of older messages
            self._create_context_summary()
    
    def _create_context_summary(self):
        """Create a summary of older context"""
        # This is a simplified version - in production, you'd use LLM to summarize
        older_messages = self.messages[:-10]  # Keep last 10 messages
        
        summary_parts = []
        for msg in older_messages:
            if msg.role == "user":
                summary_parts.append(f"User asked about: {msg.content[:50]}...")
        
        if summary_parts:
            self.context_summary = " ".join(summary_parts[-5:])  # Last 5 topics
        
        # Remove older messages except system
        self.messages = [m for m in self.messages if m.role == "system"] + self.messages[-10:]
    
    def clear(self):
        """Clear all memory"""
        self.messages.clear()
        self.memory_entries.clear()
        self.context_summary = None
    
    def export_memory(self) -> Dict[str, Any]:
        """Export memory to dict for saving"""
        return {
            "messages": [
                {"role": msg.role, "content": msg.content} 
                for msg in self.messages
            ],
            "memory_entries": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "type": entry.type,
                    "content": entry.content,
                    "metadata": entry.metadata
                }
                for entry in self.memory_entries
            ],
            "context_summary": self.context_summary
        }
    
    def import_memory(self, data: Dict[str, Any]):
        """Import memory from dict"""
        self.clear()
        
        # Import messages
        for msg_data in data.get("messages", []):
            self.messages.append(
                Message(role=msg_data["role"], content=msg_data["content"])
            )
        
        # Import memory entries
        for entry_data in data.get("memory_entries", []):
            self.memory_entries.append(
                MemoryEntry(
                    timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                    type=entry_data["type"],
                    content=entry_data["content"],
                    metadata=entry_data.get("metadata", {})
                )
            )
        
        self.context_summary = data.get("context_summary")