# agent/planner.py - Task planning and decomposition
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import logging

from llm.base import BaseLLM, Message
from llm.prompts import TASK_PLANNING_PROMPT
from .capabilities import CAPABILITIES

logger = logging.getLogger(__name__)

@dataclass
class TaskStep:
    """Represents a single step in a task plan"""
    id: str
    description: str
    action_type: str
    dependencies: List[str] = None
    priority: int = 1
    estimated_time: int = 30  # seconds
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass 
class TaskPlan:
    """Represents a complete task plan"""
    task_description: str
    steps: List[TaskStep]
    total_estimated_time: int = 0
    complexity: str = "medium"  # low, medium, high
    
    def __post_init__(self):
        # Calculate total time
        self.total_estimated_time = sum(step.estimated_time for step in self.steps)

class TaskPlanner:
    """Breaks down complex tasks into executable steps"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.capabilities = CAPABILITIES
    
    async def create_plan(self, task: str, context: List[Message] = None) -> TaskPlan:
        """Create a task plan from natural language description"""
        try:
            # Prepare planning prompt
            planning_prompt = TASK_PLANNING_PROMPT.format(user_request=task)
            
            # Build messages
            messages = context or []
            messages.append(Message(role="user", content=planning_prompt))
            
            # Get plan from LLM
            response = await self.llm.generate(
                messages=messages,
                temperature=0.3,  # Lower temperature for structured planning
                max_tokens=1500
            )
            
            # Parse the plan
            plan = self._parse_plan_response(response.content, task)
            
            # Validate and enhance the plan
            plan = self._enhance_plan(plan)
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            # Return a simple fallback plan
            return self._create_fallback_plan(task)
    
    def _parse_plan_response(self, response: str, task: str) -> TaskPlan:
        """Parse LLM response into a structured plan"""
        steps = []
        lines = response.strip().split('\n')
        
        step_counter = 1
        current_step_text = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a number (new step)
            if any(line.startswith(f"{i}.") or line.startswith(f"{i})") for i in range(1, 20)):
                # Save previous step if exists
                if current_step_text:
                    step = self._create_step_from_text(
                        f"step_{step_counter-1}",
                        current_step_text
                    )
                    steps.append(step)
                
                # Start new step
                current_step_text = line
                step_counter += 1
            else:
                # Continue current step
                current_step_text += " " + line
        
        # Don't forget the last step
        if current_step_text:
            step = self._create_step_from_text(
                f"step_{step_counter-1}",
                current_step_text
            )
            steps.append(step)
        
        # If no steps were parsed, create a single step
        if not steps:
            steps.append(TaskStep(
                id="step_1",
                description=task,
                action_type=self._guess_action_type(task)
            ))
        
        return TaskPlan(
            task_description=task,
            steps=steps,
            complexity=self._estimate_complexity(steps)
        )
    
    def _create_step_from_text(self, step_id: str, text: str) -> TaskStep:
        """Create a TaskStep from text description"""
        # Clean the text
        text = text.strip()
        for i in range(1, 20):
            text = text.replace(f"{i}.", "").replace(f"{i})", "").strip()
        
        return TaskStep(
            id=step_id,
            description=text,
            action_type=self._guess_action_type(text),
            priority=self._estimate_priority(text),
            estimated_time=self._estimate_time(text)
        )
    
    def _guess_action_type(self, text: str) -> str:
        """Guess the action type from text"""
        text_lower = text.lower()
        
        action_keywords = {
            "navigate": ["go to", "navigate", "open", "visit"],
            "search": ["search", "find", "look for", "query"],
            "click": ["click", "press", "select", "choose"],
            "fill_form": ["fill", "enter", "type", "input"],
            "screenshot": ["screenshot", "capture", "snapshot"],
            "scrape": ["scrape", "extract", "collect", "gather"],
            "compare": ["compare", "contrast", "versus"],
            "monitor": ["monitor", "watch", "track", "observe"]
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return action
        
        return "navigate"  # default
    
    def _estimate_priority(self, text: str) -> int:
        """Estimate step priority (1-5, higher is more important)"""
        if any(word in text.lower() for word in ["first", "initial", "start", "begin"]):
            return 5
        elif any(word in text.lower() for word in ["critical", "important", "essential"]):
            return 4
        elif any(word in text.lower() for word in ["finally", "last", "end"]):
            return 2
        else:
            return 3
    
    def _estimate_time(self, text: str) -> int:
        """Estimate time in seconds for a step"""
        action_type = self._guess_action_type(text)
        
        time_estimates = {
            "navigate": 5,
            "search": 10,
            "click": 2,
            "fill_form": 15,
            "screenshot": 5,
            "scrape": 30,
            "compare": 60,
            "monitor": 120
        }
        
        return time_estimates.get(action_type, 10)
    
    def _estimate_complexity(self, steps: List[TaskStep]) -> str:
        """Estimate overall task complexity"""
        num_steps = len(steps)
        total_time = sum(step.estimated_time for step in steps)
        
        if num_steps <= 2 and total_time <= 30:
            return "low"
        elif num_steps <= 5 and total_time <= 120:
            return "medium"
        else:
            return "high"
    
    def _enhance_plan(self, plan: TaskPlan) -> TaskPlan:
        """Enhance plan with dependencies and optimizations"""
        # Add dependencies based on logical flow
        for i, step in enumerate(plan.steps):
            if i > 0:
                # Most steps depend on the previous one
                step.dependencies = [plan.steps[i-1].id]
        
        # Identify steps that can run in parallel
        # (This is a simplified version - could be more sophisticated)
        parallel_actions = ["screenshot", "scrape"]
        for i in range(len(plan.steps) - 1):
            if (plan.steps[i].action_type in parallel_actions and 
                plan.steps[i+1].action_type in parallel_actions):
                # These can run in parallel - remove dependency
                plan.steps[i+1].dependencies = []
        
        return plan
    
    def _create_fallback_plan(self, task: str) -> TaskPlan:
        """Create a simple fallback plan when parsing fails"""
        return TaskPlan(
            task_description=task,
            steps=[
                TaskStep(
                    id="step_1",
                    description=task,
                    action_type="navigate",
                    priority=3
                )
            ],
            complexity="low"
        )
    
    def validate_plan(self, plan: TaskPlan) -> bool:
        """Validate that a plan is executable"""
        if not plan.steps:
            return False
        
        # Check that all action types are valid
        valid_actions = set(self.capabilities.keys())
        for step in plan.steps:
            if step.action_type not in valid_actions:
                logger.warning(f"Invalid action type: {step.action_type}")
                return False
        
        # Check dependency graph for cycles
        if self._has_circular_dependencies(plan):
            return False
        
        return True
    
    def _has_circular_dependencies(self, plan: TaskPlan) -> bool:
        """Check if the plan has circular dependencies"""
        # Build adjacency list
        graph = {step.id: step.dependencies for step in plan.steps}
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step in plan.steps:
            if step.id not in visited:
                if has_cycle(step.id):
                    return True
        
        return False
    
    def optimize_plan(self, plan: TaskPlan) -> TaskPlan:
        """Optimize a plan for better performance"""
        # This is a placeholder for more sophisticated optimization
        # Could include:
        # - Reordering steps for efficiency
        # - Combining similar actions
        # - Parallelizing independent steps
        # - Caching repeated operations
        
        return plan