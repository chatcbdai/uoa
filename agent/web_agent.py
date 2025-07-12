# agent/web_agent.py - Main agent orchestrator
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from llm.base import BaseLLM, Message
from llm.prompts import WEB_ASSISTANT_SYSTEM_PROMPT, TASK_PLANNING_PROMPT
from .planner import TaskPlanner
from .actions import ActionMapper
from .memory import ConversationMemory
from .capabilities import CAPABILITIES

logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Tracks the current state of the agent"""
    current_task: Optional[str] = None
    completed_tasks: List[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []
        if self.context is None:
            self.context = {}

class WebAgent:
    """Main web automation agent that orchestrates task planning and execution"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.planner = TaskPlanner(llm)
        self.action_mapper = ActionMapper()
        self.memory = ConversationMemory()
        self.state = AgentState()
        self.capabilities = CAPABILITIES
    
    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request and return a plan for execution"""
        try:
            # Add to memory
            self.memory.add_user_message(user_input)
            
            # Update state
            self.state.current_task = user_input
            
            # Generate task plan
            plan = await self.planner.create_plan(
                user_input,
                self.memory.get_context()
            )
            
            # Validate the plan
            if not self.planner.validate_plan(plan):
                raise ValueError("Generated plan is invalid or incomplete")
            
            # Convert plan steps to actions
            actions = []
            for step in plan.steps:
                action = await self._convert_step_to_action(step)
                if action:
                    actions.append(action)
            
            # Add assistant response to memory
            self.memory.add_assistant_message(
                f"I'll help you with: {user_input}. I've created a plan with {len(actions)} actions."
            )
            
            # Update state
            self.state.completed_tasks.append(user_input)
            
            return {
                "plan": plan,
                "actions": actions,
                "state": self.state
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise
    
    async def _convert_step_to_action(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a plan step to an executable action"""
        try:
            # Extract the instruction from the step
            instruction = step.get("description", "")
            
            # Map to action using the action mapper
            action = self.action_mapper.map_intent_to_action(instruction)
            
            # Add metadata from the step
            action["step_id"] = step.get("id")
            action["priority"] = step.get("priority", 1)
            
            return action
            
        except Exception as e:
            logger.warning(f"Could not convert step to action: {str(e)}")
            return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities"""
        return self.capabilities
    
    def get_state(self) -> AgentState:
        """Return the current agent state"""
        return self.state
    
    def reset_state(self):
        """Reset the agent state"""
        self.state = AgentState()
        self.memory.clear()
    
    async def explain_capabilities(self) -> str:
        """Generate a natural language explanation of capabilities"""
        messages = [
            Message(role="system", content=WEB_ASSISTANT_SYSTEM_PROMPT),
            Message(role="user", content="Explain your web automation capabilities in a user-friendly way.")
        ]
        
        response = await self.llm.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.content