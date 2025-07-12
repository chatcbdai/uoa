# tasks/executor.py - Task execution with async patterns and error handling
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging
from config import config
from browser import BrowserFactory
from scrapers import UnifiedScraper

logger = logging.getLogger(__name__)

@dataclass
class Task:
    id: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 1
    retry_count: int = 0

@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0
    timestamp: datetime = None

class TaskExecutor:
    """Executes planned tasks using asyncio TaskGroup and semaphore patterns"""
    
    def __init__(self):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.execution.max_concurrent_tasks)
        self.browser_pool = []
        self.scrapers = {}
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a single task with retry logic"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Acquire semaphore for concurrency control
            async with self.semaphore:
                # Get or create browser instance
                browser = await self._get_browser()
                
                # Execute the task action
                result = await self._execute_action(browser, task)
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Task {task.id} failed: {str(e)}")
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                task_id=task.id,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time,
                timestamp=datetime.now()
            )
    
    async def execute_parallel(self, tasks: List[Task]) -> List[TaskResult]:
        """Execute multiple tasks in parallel using TaskGroup (Python 3.11+)"""
        results = []
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda x: x.priority, reverse=True)
        
        # For Python 3.11+, use TaskGroup
        try:
            async with asyncio.TaskGroup() as tg:
                # Create tasks with proper error handling
                task_futures = []
                for task in sorted_tasks:
                    future = tg.create_task(self.execute_task(task))
                    task_futures.append(future)
            
            # Collect results
            for future in task_futures:
                results.append(future.result())
                
        except AttributeError:
            # Fallback for Python < 3.11
            task_futures = []
            for task in sorted_tasks:
                future = asyncio.create_task(self.execute_task(task))
                task_futures.append(future)
            
            # Gather results
            results = await asyncio.gather(*task_futures, return_exceptions=False)
        
        return results
    
    async def execute_pipeline(self, tasks: List[Task]) -> TaskResult:
        """Execute tasks in a pipeline where each output feeds the next input"""
        previous_result = None
        
        for task in tasks:
            # Add previous result to task parameters if available
            if previous_result:
                task.parameters['previous_result'] = previous_result
            
            result = await self.execute_task(task)
            
            if not result.success:
                # Pipeline failed, return error
                return result
            
            previous_result = result.result
        
        # Return final result
        return TaskResult(
            task_id=f"pipeline_{tasks[-1].id}",
            success=True,
            result=previous_result,
            timestamp=datetime.now()
        )
    
    async def _get_browser(self):
        """Get browser from pool or create new one"""
        if not self.browser_pool:
            # Create StealthBrowser instance
            from browser import StealthBrowser
            browser = StealthBrowser(
                headless=self.config.browser.headless,
                viewport_width=self.config.browser.viewport_width,
                viewport_height=self.config.browser.viewport_height
            )
            await browser.initialize()
            self.browser_pool.append(browser)
        
        return self.browser_pool[0]
    
    async def _execute_action(self, browser, task: Task) -> Any:
        """Execute specific browser action"""
        action_map = {
            'navigate': browser.navigate,
            'search': browser.search,
            'click': browser.click,
            'fill_form': browser.fill_form,
            'screenshot': browser.screenshot,
            'scrape': self._scrape_with_browser,
            'extract_data': self._extract_data,
            'extract': self._extract_data,
            'compare': self._compare_sites,
            'monitor': self._monitor_site,
            'download': self._download_file,
            # Social media actions
            'post_instagram': self._post_to_instagram,
            'post_twitter': self._post_to_twitter,
            'post_facebook': self._post_to_facebook,
            'post_linkedin': self._post_to_linkedin,
            'post_social': self._post_to_social_media
        }
        
        action_func = action_map.get(task.action)
        if not action_func:
            raise ValueError(f"Unknown action: {task.action}")
        
        # Execute with parameters
        if task.action == 'scrape':
            return await action_func(browser, **task.parameters)
        else:
            return await action_func(**task.parameters)
    
    async def _scrape_with_browser(self, browser, **kwargs):
        """Use UnifiedScraper for scraping tasks"""
        # Get or create scraper for this browser type
        engine = self.config.browser.default_engine
        if engine not in self.scrapers:
            self.scrapers[engine] = UnifiedScraper(
                engine=engine,
                anti_detection=self.config.browser.anti_detection,
                headless=self.config.browser.headless,
                rate_limit=self.config.execution.rate_limit
            )
        
        scraper = self.scrapers[engine]
        
        try:
            return await scraper.scrape(**kwargs)
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            raise
    
    async def _extract_data(self, **kwargs):
        """Extract structured data from a page"""
        browser = await self._get_browser()
        url = kwargs.get('url')
        selectors = kwargs.get('selectors', {})
        multiple = kwargs.get('multiple', False)
        
        # Navigate to URL if provided
        if url:
            await browser.navigate(url)
        
        # Extract data using selectors
        results = {}
        for name, selector in selectors.items():
            try:
                if multiple:
                    elements = await browser.page.query_selector_all(selector)
                    results[name] = []
                    for elem in elements:
                        text = await elem.text_content()
                        results[name].append(text.strip() if text else "")
                else:
                    element = await browser.page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        results[name] = text.strip() if text else ""
                    else:
                        results[name] = None
            except Exception as e:
                logger.warning(f"Failed to extract {name}: {str(e)}")
                results[name] = None
        
        return results
    
    async def _compare_sites(self, **kwargs):
        """Compare information across multiple sites"""
        urls = kwargs.get('urls', [])
        criteria = kwargs.get('criteria', [])
        output_format = kwargs.get('output_format', 'table')
        
        comparison_data = []
        
        for url in urls:
            site_data = {'url': url}
            
            # Scrape each site
            try:
                result = await self._scrape_with_browser(None, url=url, mode='single')
                
                # Extract criteria from scraped content
                # This is simplified - in production, use NLP or structured extraction
                content = result.get('content', '')
                for criterion in criteria:
                    # Simple keyword search
                    if criterion.lower() in content.lower():
                        site_data[criterion] = "Found"
                    else:
                        site_data[criterion] = "Not found"
                        
            except Exception as e:
                logger.error(f"Failed to compare {url}: {str(e)}")
                for criterion in criteria:
                    site_data[criterion] = "Error"
            
            comparison_data.append(site_data)
        
        # Format output
        if output_format == 'table':
            return self._format_comparison_table(comparison_data, criteria)
        else:
            return comparison_data
    
    async def _monitor_site(self, **kwargs):
        """Monitor a website for changes"""
        url = kwargs.get('url')
        selector = kwargs.get('selector')
        interval = kwargs.get('interval', 300)  # 5 minutes default
        duration = kwargs.get('duration', 3600)  # 1 hour default
        
        start_time = asyncio.get_event_loop().time()
        changes = []
        previous_content = None
        
        while asyncio.get_event_loop().time() - start_time < duration:
            try:
                # Get current content
                if selector:
                    browser = await self._get_browser()
                    await browser.navigate(url)
                    element = await browser.page.query_selector(selector)
                    current_content = await element.text_content() if element else None
                else:
                    result = await self._scrape_with_browser(None, url=url, mode='single')
                    current_content = result.get('content', '')
                
                # Check for changes
                if previous_content and current_content != previous_content:
                    changes.append({
                        'timestamp': datetime.now(),
                        'old_content': previous_content[:100] + "...",
                        'new_content': current_content[:100] + "...",
                        'full_content': current_content
                    })
                
                previous_content = current_content
                
                # Wait for next check
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
        
        return {
            'url': url,
            'total_checks': int((asyncio.get_event_loop().time() - start_time) / interval),
            'changes_detected': len(changes),
            'changes': changes
        }
    
    async def _download_file(self, **kwargs):
        """Download a file from URL"""
        url = kwargs.get('url')
        filename = kwargs.get('filename')
        directory = kwargs.get('directory', self.config.storage.data_dir)
        
        browser = await self._get_browser()
        
        # Set download behavior
        download_path = directory / (filename or url.split('/')[-1])
        
        # Navigate and trigger download
        # This is simplified - real implementation would handle various download scenarios
        await browser.navigate(url)
        
        return {
            'url': url,
            'path': str(download_path),
            'status': 'completed'
        }
    
    def _format_comparison_table(self, data: List[Dict], criteria: List[str]) -> Dict[str, Any]:
        """Format comparison data as a table"""
        from rich.table import Table
        
        table = Table(title="Website Comparison")
        
        # Add columns
        table.add_column("Website", style="cyan")
        for criterion in criteria:
            table.add_column(criterion, style="white")
        
        # Add rows
        for site_data in data:
            row = [site_data['url']]
            for criterion in criteria:
                row.append(site_data.get(criterion, "N/A"))
            table.add_row(*row)
        
        return {
            'table': table,
            'data': data
        }
    
    async def _post_to_social_media(self, **kwargs):
        """Post to social media platforms"""
        from social_media import SocialMediaOrchestrator
        
        # Get platforms from kwargs
        platforms = kwargs.get('platforms', [])
        if isinstance(platforms, str):
            platforms = [platforms]
        
        # Create orchestrator
        storage_path = Path.cwd() / "storage" / "social_media"
        orchestrator = SocialMediaOrchestrator(storage_path, self.llm)
        
        # Post content
        return await orchestrator.post_to_platforms(
            platforms=platforms,
            content=kwargs.get('content'),
            use_csv=kwargs.get('use_csv', False)
        )

    async def _post_to_instagram(self, **kwargs):
        """Post to Instagram"""
        kwargs['platforms'] = ['instagram']
        return await self._post_to_social_media(**kwargs)

    async def _post_to_twitter(self, **kwargs):
        """Post to Twitter"""
        kwargs['platforms'] = ['twitter']
        return await self._post_to_social_media(**kwargs)

    async def _post_to_facebook(self, **kwargs):
        """Post to Facebook"""
        kwargs['platforms'] = ['facebook']
        return await self._post_to_social_media(**kwargs)

    async def _post_to_linkedin(self, **kwargs):
        """Post to LinkedIn"""
        kwargs['platforms'] = ['linkedin']
        return await self._post_to_social_media(**kwargs)
    
    async def cleanup(self):
        """Cleanup resources"""
        # Close all browsers
        for browser in self.browser_pool:
            try:
                await browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
        
        # Cleanup scrapers
        for scraper in self.scrapers.values():
            try:
                await scraper.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up scraper: {str(e)}")
        
        self.browser_pool.clear()
        self.scrapers.clear()