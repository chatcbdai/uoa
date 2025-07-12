# AI Web Assistant - Undetectable Toolkit

An AI-powered terminal assistant that leverages the undetectable web browsing toolkit to perform complex web automation tasks through natural language commands.

## Features

- 🤖 **Natural Language Interface**: Describe what you need in plain English
- 🌐 **Undetectable Web Browsing**: Built on top of advanced anti-detection technology
- 🔍 **Intelligent Task Planning**: AI breaks down complex tasks into executable steps
- ⚡ **Parallel Execution**: Process multiple tasks concurrently for efficiency
- 📊 **Rich Terminal Output**: Beautiful tables, progress indicators, and formatted results
- 🧠 **Context Memory**: Maintains conversation history for better understanding

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI or Anthropic API key:
```
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here
```

### 3. Run the Assistant

```bash
python main.py
```

## Example Commands

```
> Search for Python web scraping libraries and create a comparison table
> Take a screenshot of amazon.com homepage
> Extract all email addresses from example.com/contact
> Compare iPhone 15 prices on Amazon, BestBuy, and Apple.com
> Scrape the entire Python documentation and save as markdown
> Monitor the price of this product and alert me when it drops
```

## Architecture

```
├── main.py              # CLI entry point
├── assistant.py         # Main orchestrator
├── config.py           # Configuration management
├── llm/                # LLM integration
│   ├── base.py        # Abstract LLM interface
│   ├── openai_client.py
│   └── anthropic_client.py
├── agent/              # AI agent logic
│   ├── web_agent.py   # Main agent
│   ├── planner.py     # Task planning
│   └── actions.py     # Action mapping
├── tasks/              # Task execution
│   ├── executor.py    # Task executor
│   └── queue.py       # Task queue
└── examples/           # Example commands
```

## Configuration

See `.env.example` for all available configuration options:

- **LLM Settings**: Choose between OpenAI and Anthropic, configure models and parameters
- **Browser Settings**: Configure headless mode, viewport size, anti-detection features
- **Execution Settings**: Set concurrency limits, timeouts, retry policies
- **Storage Settings**: Configure data directories and database paths

## Capabilities

- **Web Navigation**: Navigate to any URL, handle redirects, manage sessions
- **Content Extraction**: Scrape web pages, extract specific data, convert formats
- **Form Interaction**: Fill forms, click buttons, interact with page elements
- **Search Operations**: Search Google, Bing, DuckDuckGo and extract results
- **Screenshots**: Capture full-page or element-specific screenshots
- **Data Comparison**: Compare information across multiple websites
- **Monitoring**: Track changes on websites over time

## Development

This assistant is built on top of the existing undetectable toolkit components:
- StealthBrowser for anti-detection
- UnifiedScraper for content extraction
- SQLiteStorage for data persistence

## License

See the main project license.