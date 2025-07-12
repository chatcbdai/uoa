# tasks/queue.py - Simple asyncio Queue-based task queue
import asyncio
from typing import List, Optional, Callable
from asyncio import Queue
import logging
from datetime import datetime
from .executor import Task, TaskResult, TaskExecutor

logger = logging.getLogger(__name__)

class TaskQueue:
    """Simple task queue using asyncio.Queue"""
    
    def __init__(self, num_workers: int = 3):
        self.queue: Queue = asyncio.Queue()
        self.num_workers = num_workers
        self.workers: List[asyncio.Task] = []
        self.executor = TaskExecutor()
        self.results: List[TaskResult] = []
        self._running = False
    
    async def add_task(self, task: Task):
        """Add a task to the queue"""
        await self.queue.put(task)
        logger.info(f"Task {task.id} added to queue")
    
    async def add_tasks(self, tasks: List[Task]):
        """Add multiple tasks to the queue"""
        for task in tasks:
            await self.queue.put(task)
        logger.info(f"Added {len(tasks)} tasks to queue")
    
    async def worker(self, name: str):
        """Worker coroutine that processes tasks from the queue"""
        logger.info(f"Worker {name} started")
        
        while self._running:
            try:
                # Wait for a task with timeout to check running status
                task = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                logger.info(f"Worker {name} processing task {task.id}")
                
                # Execute the task
                result = await self.executor.execute_task(task)
                
                # Store result
                self.results.append(result)
                
                # Mark task as done
                self.queue.task_done()
                
                logger.info(
                    f"Worker {name} completed task {task.id} "
                    f"(success: {result.success})"
                )
                
            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                logger.error(f"Worker {name} error: {str(e)}")
    
    async def start(self):
        """Start the task queue workers"""
        self._running = True
        
        # Create worker tasks
        for i in range(self.num_workers):
            worker_task = asyncio.create_task(
                self.worker(f"Worker-{i}")
            )
            self.workers.append(worker_task)
        
        logger.info(f"Started {self.num_workers} workers")
    
    async def stop(self):
        """Stop all workers and wait for queue to be empty"""
        # Wait for queue to be processed
        await self.queue.join()
        
        # Stop workers
        self._running = False
        
        # Wait for all workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        logger.info("All workers stopped")
    
    async def process_all(self, tasks: List[Task]) -> List[TaskResult]:
        """Process all tasks and return results"""
        # Clear previous results
        self.results = []
        
        # Start workers
        await self.start()
        
        # Add all tasks
        await self.add_tasks(tasks)
        
        # Wait for completion
        await self.queue.join()
        
        # Stop workers
        await self.stop()
        
        return self.results
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        completed = len([r for r in self.results if r.success])
        failed = len([r for r in self.results if not r.success])
        
        return {
            'queued': self.queue.qsize(),
            'completed': completed,
            'failed': failed,
            'total_processed': len(self.results)
        }