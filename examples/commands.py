# examples/commands.py - Example commands for the AI Web Assistant

EXAMPLE_COMMANDS = {
    "basic_search": {
        "command": "Search for Python tutorials and save the top 5 results",
        "description": "Performs a web search and saves results",
        "expected_actions": ["search", "save"]
    },
    
    "price_comparison": {
        "command": "Compare iPhone 15 prices on Amazon, BestBuy, and Apple.com",
        "description": "Compares product prices across multiple websites",
        "expected_actions": ["navigate", "extract_data", "compare"]
    },
    
    "form_automation": {
        "command": "Fill out the contact form on example.com with my information",
        "description": "Automates form filling on a website",
        "expected_actions": ["navigate", "fill_form", "submit"]
    },
    
    "data_extraction": {
        "command": "Extract all product names and prices from shop.example.com",
        "description": "Extracts structured data from a website",
        "expected_actions": ["navigate", "extract_data"]
    },
    
    "monitoring": {
        "command": "Check if example.com is down and notify me",
        "description": "Monitors website availability",
        "expected_actions": ["navigate", "monitor"]
    },
    
    "documentation_scraping": {
        "command": "Scrape the entire Python documentation and save as markdown",
        "description": "Downloads and converts documentation to markdown",
        "expected_actions": ["scrape", "convert", "save"]
    },
    
    "social_media": {
        "command": "Take screenshots of my Twitter timeline",
        "description": "Captures screenshots of social media pages",
        "expected_actions": ["navigate", "screenshot"]
    },
    
    "research": {
        "command": "Research recent news about AI and create a summary report",
        "description": "Performs research and creates a report",
        "expected_actions": ["search", "scrape", "analyze", "report"]
    },
    
    "multi_page_scraping": {
        "command": "Scrape all blog posts from example-blog.com including pagination",
        "description": "Scrapes content across multiple pages",
        "expected_actions": ["navigate", "scrape", "paginate"]
    },
    
    "login_and_extract": {
        "command": "Login to my-account.com and download my invoice history",
        "description": "Logs into a website and downloads documents",
        "expected_actions": ["navigate", "fill_form", "click", "download"]
    },
    
    "table_extraction": {
        "command": "Extract the pricing table from pricing.example.com and save as CSV",
        "description": "Extracts tables and converts to CSV format",
        "expected_actions": ["navigate", "extract_data", "convert", "save"]
    },
    
    "image_download": {
        "command": "Download all images from gallery.example.com",
        "description": "Downloads multiple images from a website",
        "expected_actions": ["navigate", "extract", "download"]
    },
    
    "news_aggregation": {
        "command": "Get the top headlines from CNN, BBC, and Reuters",
        "description": "Aggregates news from multiple sources",
        "expected_actions": ["navigate", "extract", "aggregate"]
    },
    
    "product_monitoring": {
        "command": "Monitor the price of this product on Amazon and alert me when it drops below $50",
        "description": "Monitors product prices for changes",
        "expected_actions": ["navigate", "extract", "monitor", "alert"]
    },
    
    "pdf_generation": {
        "command": "Convert this blog post to PDF and save it",
        "description": "Converts web content to PDF",
        "expected_actions": ["navigate", "convert", "save"]
    }
}

# Demo script to show example usage
def demonstrate_examples():
    """Show example commands and their usage"""
    print("AI Web Assistant - Example Commands\n")
    print("=" * 60)
    
    for name, details in EXAMPLE_COMMANDS.items():
        print(f"\n{name.upper().replace('_', ' ')}:")
        print(f"Command: {details['command']}")
        print(f"Description: {details['description']}")
        print(f"Expected actions: {', '.join(details['expected_actions'])}")
        print("-" * 40)

# Function to get a random example
def get_random_example():
    """Get a random example command"""
    import random
    name = random.choice(list(EXAMPLE_COMMANDS.keys()))
    return EXAMPLE_COMMANDS[name]['command']

# Function to get examples by action type
def get_examples_by_action(action: str):
    """Get all examples that use a specific action"""
    examples = []
    for name, details in EXAMPLE_COMMANDS.items():
        if action in details['expected_actions']:
            examples.append({
                'name': name,
                'command': details['command']
            })
    return examples

if __name__ == "__main__":
    demonstrate_examples()