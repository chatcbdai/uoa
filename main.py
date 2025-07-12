#!/usr/bin/env python3
# main.py - Simple yet powerful CLI interface using rich and prompt_toolkit
import sys
import os
# Add parent directory to path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

console = Console()

class WebAssistantCLI:
    def __init__(self):
        self.console = console
        self.session = PromptSession(
            history=FileHistory('.assistant_history'),
            completer=WordCompleter([
                'help', 'exit', 'search', 'scrape', 'screenshot',
                'navigate', 'extract', 'compare', 'monitor',
                'post', 'publish', 'share',  # Social media actions
                'instagram', 'twitter', 'facebook', 'linkedin',  # Platforms
                'social', 'media'  # Keywords
            ])
        )
        self.assistant = None  # Will be initialized with WebAssistant
        
    async def run(self):
        """Main CLI loop"""
        self.console.print("[bold green]🤖 AI Web Assistant Ready![/bold green]")
        self.console.print("Type 'help' for commands or describe what you need.\n")
        
        while True:
            try:
                # Get user input with auto-completion
                user_input = await self.session.prompt_async('> ')
                
                if user_input.lower() in ['exit', 'quit']:
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                    
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # Process the request with progress indicator
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Processing request...", total=None)
                    
                    # Initialize assistant if not already done
                    if not self.assistant:
                        from assistant import WebAssistant
                        self.assistant = WebAssistant()
                    
                    # Process request
                    result = await self.assistant.process_request(user_input)
                    
                    progress.stop()
                    
                # Display results
                self.display_results(result)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
    
    def show_help(self):
        """Display help information"""
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        
        commands = [
            ("search", "Search the web for information"),
            ("scrape", "Extract content from websites"),
            ("screenshot", "Take screenshots of web pages"),
            ("navigate", "Go to a specific website"),
            ("extract", "Extract specific data from pages"),
            ("compare", "Compare information across sites"),
            ("monitor", "Monitor websites for changes"),
            ("post/publish", "Post to social media platforms"),
            ("help", "Show this help message"),
            ("exit", "Exit the assistant")
        ]
        
        for cmd, desc in commands:
            table.add_row(cmd, desc)
            
        self.console.print(table)
        self.console.print("\n[italic]Or just describe what you need in natural language![/italic]")
        
        # Add social media examples
        self.console.print("\n[bold]Social Media Examples:[/bold]")
        self.console.print("  • post to instagram")
        self.console.print("  • publish on twitter")
        self.console.print("  • share on facebook")
        self.console.print("  • post on linkedin")
    
    def display_results(self, result):
        """Display results in a formatted way"""
        if isinstance(result, dict):
            if 'table' in result:
                # Display as table
                self.console.print(result['table'])
            elif 'text' in result:
                # Display as formatted text
                self.console.print(result['text'])
            elif 'files' in result:
                # Display saved files
                self.console.print("[green]✅ Task completed! Files saved:[/green]")
                for file in result['files']:
                    self.console.print(f"  • {file}")
        else:
            # Simple text result
            self.console.print(result)

# Entry point
if __name__ == "__main__":
    cli = WebAssistantCLI()
    asyncio.run(cli.run())