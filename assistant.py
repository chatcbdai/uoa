# assistant.py - Main Web Assistant orchestrator
import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from rich.table import Table
from rich.console import Console

from config import config
from llm.openai_client import OpenAIClient
from llm.anthropic_client import AnthropicClient
from llm.base import Message
from llm.prompts import (
    WEB_ASSISTANT_SYSTEM_PROMPT,
    TASK_PLANNING_PROMPT,
    WEB_ACTION_MAPPING_PROMPT
)
from agent.web_agent import WebAgent
from tasks.executor import TaskExecutor, TaskQueue, Task
from storage.sqlite import SQLiteStorage

console = Console()

class ConversationMemory:
    """Simple conversation memory"""
    def __init__(self, max_messages: int = 10):
        self.messages: List[Message] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_context(self) -> List[Message]:
        return [Message(role="system", content=WEB_ASSISTANT_SYSTEM_PROMPT)] + self.messages

class WebAssistant:
    """Main assistant orchestrator that ties everything together"""
    
    def __init__(self):
        # Initialize configuration
        if not config.validate():
            raise ValueError("Invalid configuration. Please check your .env file")
        
        # Initialize LLM
        self.llm = self._init_llm()
        
        # Initialize components
        self.agent = WebAgent(llm=self.llm)
        self.executor = TaskExecutor()
        self.task_queue = TaskQueue(num_workers=config.execution.max_concurrent_tasks)
        self.memory = ConversationMemory()
        self.storage = SQLiteStorage(db_path=config.storage.db_path)
    
    def _init_llm(self):
        """Initialize LLM client based on configuration"""
        if config.llm.default_provider == "openai":
            return OpenAIClient()
        elif config.llm.default_provider == "anthropic":
            return AnthropicClient()
        else:
            raise ValueError(f"Unknown LLM provider: {config.llm.default_provider}")
    
    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request and return formatted results"""
        try:
            # Add user message to memory
            self.memory.add_message("user", user_input)
            
            # Step 1: Understand intent and create plan
            plan = await self._create_plan(user_input)
            
            # Step 2: Convert plan to executable tasks
            tasks = await self._plan_to_tasks(plan)
            
            # Step 3: Execute tasks
            results = await self._execute_tasks(tasks)
            
            # Step 4: Format and save results
            formatted_results = await self._format_results(results, user_input)
            
            # Add assistant response to memory
            self.memory.add_message("assistant", formatted_results.get('summary', ''))
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return {"error": error_msg}
    
    async def _create_plan(self, user_input: str) -> Dict[str, Any]:
        """Use LLM to create execution plan"""
        # Get conversation context
        messages = self.memory.get_context()
        
        # Add planning prompt
        planning_prompt = TASK_PLANNING_PROMPT.format(user_request=user_input)
        messages.append(Message(role="user", content=planning_prompt))
        
        # Get plan from LLM
        response = await self.llm.generate(
            messages=messages,
            temperature=0.3  # Lower temperature for more focused planning
        )
        
        # Parse plan (in real implementation, use structured output)
        plan = self._parse_plan(response.content)
        return plan
    
    async def _plan_to_tasks(self, plan: Dict[str, Any]) -> List[Task]:
        """Convert plan to executable tasks"""
        tasks = []
        
        for i, step in enumerate(plan.get('steps', [])):
            # Map step to action
            action = await self._map_to_action(step['description'])
            
            task = Task(
                id=f"task_{i+1}",
                action=action['action'],
                parameters=action['parameters'],
                priority=step.get('priority', 1)
            )
            tasks.append(task)
        
        return tasks
    
    async def _map_to_action(self, instruction: str) -> Dict[str, Any]:
        """Map natural language instruction to browser action"""
        prompt = WEB_ACTION_MAPPING_PROMPT.format(instruction=instruction)
        
        response = await self.llm.generate(
            messages=[
                Message(role="system", content="You are a helpful assistant that maps instructions to actions."),
                Message(role="user", content=prompt)
            ],
            temperature=0.1
        )
        
        # Parse action (simplified - use JSON mode in production)
        return self._parse_action(response.content)
    
    async def _execute_tasks(self, tasks: List[Task]) -> List[Any]:
        """Execute tasks using the task queue"""
        if len(tasks) == 1:
            # Single task - execute directly
            result = await self.executor.execute_task(tasks[0])
            return [result]
        else:
            # Multiple tasks - use queue for parallel execution
            return await self.task_queue.process_all(tasks)
    
    async def _format_results(self, results: List[Any], original_request: str) -> Dict[str, Any]:
        """Format results for display"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # Create summary
        summary = f"Completed {len(successful)} tasks successfully"
        if failed:
            summary += f", {len(failed)} failed"
        
        # Format based on request type
        if "compare" in original_request.lower():
            return self._format_comparison(results)
        elif "table" in original_request.lower():
            return self._format_table(results)
        elif "screenshot" in original_request.lower():
            return self._format_screenshots(results)
        else:
            return self._format_general(results)
    
    def _format_comparison(self, results: List[Any]) -> Dict[str, Any]:
        """Format comparison results as a table"""
        table = Table(title="Comparison Results")
        # Add columns based on data
        # ... (implementation details)
        return {"table": table, "summary": "Comparison completed"}
    
    def _format_screenshots(self, results: List[Any]) -> Dict[str, Any]:
        """Format screenshot results"""
        files = []
        for result in results:
            if result.success and 'path' in result.result:
                files.append(str(result.result['path']))
        
        return {
            "files": files,
            "summary": f"Saved {len(files)} screenshots"
        }
    
    def _format_table(self, results: List[Any]) -> Dict[str, Any]:
        """Format results as a table"""
        if not results or not results[0].success:
            return {"text": "No data to display", "summary": "No results"}
        
        # Extract data from results
        data = results[0].result
        if isinstance(data, dict) and 'table' in data:
            return {"table": data['table'], "summary": "Table created"}
        
        # Create a simple table from data
        table = Table(title="Results")
        
        # Simplified table creation - in production, analyze data structure
        if isinstance(data, list) and data:
            # Add columns from first item
            if isinstance(data[0], dict):
                for key in data[0].keys():
                    table.add_column(key.title(), style="cyan")
                
                # Add rows
                for item in data:
                    table.add_row(*[str(item.get(k, "")) for k in data[0].keys()])
        
        return {"table": table, "summary": f"Table with {len(data)} rows"}
    
    def _format_general(self, results: List[Any]) -> Dict[str, Any]:
        """General result formatting"""
        output = []
        for result in results:
            if result.success:
                output.append(result.result)
        
        return {
            "text": "\n".join(str(o) for o in output),
            "summary": f"Completed {len(output)} tasks"
        }
    
    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse LLM plan response (simplified)"""
        # In production, use structured output or JSON mode
        steps = []
        lines = plan_text.strip().split('\n')
        
        for line in lines:
            if line.strip() and any(line.startswith(str(i)) for i in range(1, 10)):
                steps.append({
                    'description': line.strip(),
                    'priority': 1
                })
        
        return {'steps': steps}
    
    def _parse_action(self, action_text: str) -> Dict[str, Any]:
        """Parse LLM action response (simplified)"""
        # In production, use structured output
        # This is a simplified parser
        action_text = action_text.lower()
        
        if 'navigate(' in action_text:
            # Extract URL
            import re
            url_match = re.search(r'https?://[^\s\)]+', action_text)
            url = url_match.group(0) if url_match else 'https://example.com'
            return {'action': 'navigate', 'parameters': {'url': url}}
        elif 'search(' in action_text:
            # Extract query
            import re
            query_match = re.search(r'query["\s:=]+([^"]+)"', action_text)
            query = query_match.group(1) if query_match else 'web search'
            return {'action': 'search', 'parameters': {'query': query}}
        elif 'screenshot(' in action_text:
            # Extract URL
            import re
            url_match = re.search(r'https?://[^\s\)]+', action_text)
            url = url_match.group(0) if url_match else None
            return {'action': 'screenshot', 'parameters': {'url': url, 'full_page': 'full' in action_text}}
        elif 'scrape(' in action_text:
            # Extract URL and mode
            import re
            url_match = re.search(r'https?://[^\s\)]+', action_text)
            url = url_match.group(0) if url_match else 'https://example.com'
            mode = 'full_site' if 'entire' in action_text or 'full' in action_text else 'single'
            return {'action': 'scrape', 'parameters': {'url': url, 'mode': mode}}
        else:
            # Default to search
            return {'action': 'search', 'parameters': {'query': action_text}}
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.executor.cleanup()
        await self.storage.close()