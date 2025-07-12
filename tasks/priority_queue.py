# tasks/priority_queue.py - Priority queue implementation
import asyncio
import heapq
import logging
from typing import List, Tuple
from datetime import datetime
from .queue import TaskQueue
from .executor import Task

logger = logging.getLogger(__name__)

class PriorityTaskQueue(TaskQueue):
    """Priority-based task queue using asyncio.PriorityQueue"""
    
    def __init__(self, num_workers: int = 3):
        super().__init__(num_workers)
        # Replace regular queue with priority queue
        self.queue = asyncio.PriorityQueue()
        self._task_counter = 0
    
    async def add_task(self, task: Task):
        """Add a task with priority to the queue"""
        # Use negative priority for max-heap behavior (higher priority first)
        # Add counter to ensure FIFO for same priority
        self._task_counter += 1
        priority_item = (-task.priority, self._task_counter, task)
        await self.queue.put(priority_item)
        logger.info(f"Task {task.id} added with priority {task.priority}")
    
    async def worker(self, name: str):
        """Worker that processes tasks by priority"""
        logger.info(f"Priority worker {name} started")
        
        while self._running:
            try:
                # Get highest priority task
                priority, counter, task = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                logger.info(
                    f"Worker {name} processing priority {task.priority} "
                    f"task {task.id}"
                )
                
                # Execute the task
                result = await self.executor.execute_task(task)
                
                # Store result
                self.results.append(result)
                
                # Mark task as done
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Priority worker {name} error: {str(e)}")