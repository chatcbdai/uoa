<div align="center">

<!-- Animated Typing SVG Header -->
<a href="https://github.com/chatcbdai/uoa">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=2800&pause=2000&color=00D9FF&center=true&vCenter=true&width=940&lines=🤖+UOA:+Undetectable+Online+Assistant;🛡️+Bypass+Any+Bot+Detection+System;🌐+AI-Powered+Web+Automation+Suite;🚀+Built+for+the+Modern+Web" alt="Typing SVG" />
</a>

<br/>
<br/>

<!-- Elite Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/github/stars/chatcbdai/uoa?style=for-the-badge&color=yellow" alt="Stars" />
  <img src="https://img.shields.io/github/forks/chatcbdai/uoa?style=for-the-badge&color=blue" alt="Forks" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Maintained-Yes-green?style=for-the-badge" alt="Maintained" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Playwright-Ready-45ba4b?style=flat-square&logo=playwright&logoColor=white" alt="Playwright" />
  <img src="https://img.shields.io/badge/AI-Powered-FF6B6B?style=flat-square&logo=openai&logoColor=white" alt="AI Powered" />
  <img src="https://img.shields.io/badge/Anti--Detection-Always_On-4ECDC4?style=flat-square&logo=shield&logoColor=white" alt="Anti-Detection" />
  <img src="https://img.shields.io/badge/Social_Media-Automated-1DA1F2?style=flat-square&logo=twitter&logoColor=white" alt="Social Media" />
  <img src="https://img.shields.io/badge/Web_Scraping-Advanced-FF6B35?style=flat-square&logo=firefox&logoColor=white" alt="Web Scraping" />
</p>

<!-- Quick Navigation -->
<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-anti-detection-system">Anti-Detection</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

<div align="center">
  <h3>🎯 The Ultimate Web Automation Toolkit That Can't Be Detected</h3>
  <p>
    <em>Bypass Cloudflare, reCAPTCHA, and any bot detection system while automating the web with AI</em>
  </p>
</div>

---

## 🌟 Why UOA?

<table>
<tr>
<td width="33%" align="center">
  <img src="https://img.icons8.com/fluency/96/000000/invisible.png" alt="Undetectable"/>
  <br/><br/>
  <b>🛡️ Truly Undetectable</b>
  <br/>
  <sub>7 advanced bypass scripts applied to EVERY web request automatically</sub>
</td>
<td width="33%" align="center">
  <img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" alt="AI Powered"/>
  <br/><br/>
  <b>🤖 AI-Powered Intelligence</b>
  <br/>
  <sub>Natural language commands with GPT-4 and Claude integration</sub>
</td>
<td width="33%" align="center">
  <img src="https://img.icons8.com/fluency/96/000000/api.png" alt="All-in-One"/>
  <br/><br/>
  <b>🚀 All-in-One Solution</b>
  <br/>
  <sub>Web scraping, automation, and social media in a single toolkit</sub>
</td>
</tr>
</table>

## ✨ Features

<details open>
<summary><b>🛡️ Anti-Detection Arsenal</b></summary>

- **Always-On Protection**: Anti-detection is enabled by default for ALL operations
- **7 Bypass Scripts**: Applied automatically to every browser instance:
  - `webdriver_fully.js` - Hides automation detection
  - `navigator_plugins.js` - Spoofs browser plugins
  - `playwright_fingerprint.js` - Fixes Playwright-specific fingerprints
  - `notification_permission.js` - Normalizes permissions
  - `pdf_viewer.js` - Adds PDF viewer support
  - `screen_props.js` - Sets realistic screen dimensions
  - `window_chrome.js` - Adds Chrome object for Chromium browsers
- **Human-like Behavior**: Natural typing, mouse movements, and randomized delays
- **Browser Launch Arguments**: Disables automation flags and suspicious features
- **Dynamic Fingerprinting**: Realistic browser profiles that change per session

</details>

<details>
<summary><b>🤖 AI-Powered Automation</b></summary>

- **Natural Language Commands**: Just describe what you want to do
- **Multi-LLM Support**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Intelligent Task Planning**: AI breaks down complex tasks automatically
- **Dynamic Element Detection**: AI finds elements even when selectors change
- **Context-Aware Actions**: Understands page content and adapts behavior

</details>

<details>
<summary><b>🌐 Web Capabilities</b></summary>

- **Universal Scraping**: Extract data from any website, even with heavy JavaScript
- **Social Media Automation**: Post to Instagram, Twitter, Facebook, LinkedIn
- **Search Engine Automation**: Google, Bing, DuckDuckGo searches
- **Form Automation**: Fill and submit complex forms
- **File Downloads**: Handle downloads with progress tracking
- **Screenshot Capture**: Full page or element-specific screenshots

</details>

<details>
<summary><b>🚀 Developer Experience</b></summary>

- **Simple API**: One-line commands for complex operations
- **Async/Await Support**: Modern Python async patterns
- **Type Hints**: Full type annotations for better IDE support
- **Comprehensive Logging**: Debug mode for troubleshooting
- **Extensible Architecture**: Easy to add new capabilities
- **Storage Options**: SQLite, PostgreSQL, MongoDB support

</details>

## 🏗️ Architecture

The UOA system is built with a modular, layered architecture that ensures anti-detection is applied consistently across all operations:

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (CLI / API / Assistant)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Request Processing                        │
│              (Natural Language → Actions)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Browser Factory                          │
│            (ALWAYS applies anti-detection)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Browser Engine Layer                        │
│  ┌──────────────┬──────────────┬─────────────┬───────────┐ │
│  │StealthBrowser│PlaywrightBrowser│CamoufoxBrowser│StaticBrowser│ │
│  │   (Primary)  │  (Adapter)    │  (Firefox)  │  (HTTP)   │ │
│  └──────────────┴──────────────┴─────────────┴───────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Anti-Detection Manager                         │
│         (Centralized bypass script injection)               │
│                 ↓ ↓ ↓ ↓ ↓ ↓ ↓                              │
│     [7 Bypass Scripts Applied Before ANY Web Access]       │
└─────────────────────────────────────────────────────────────┘
```

### Key Components:

1. **Browser Factory** (`browser/factory.py`)
   - Central point for all browser creation
   - Anti-detection enabled by default (`anti_detection=True`)
   - Logs warnings if anti-detection is disabled

2. **Anti-Detection Manager** (`browser/core/anti_detection_manager.py`)
   - Loads and manages all 7 bypass scripts
   - Applies scripts to every browser page
   - Provides consistent browser launch arguments
   - Single source of truth for anti-detection

3. **Browser Engines** (`browser/engines/`)
   - **StealthBrowser**: Primary implementation with full anti-detection
   - **PlaywrightBrowser**: Adapter that adds bypass scripts to Playwright
   - **CamoufoxBrowser**: Firefox-based with built-in stealth features
   - **StaticBrowser**: HTTP client with stealth headers only

4. **Bypass Scripts** (`anti_detection/bypasses/`)
   - Canonical location for all anti-detection JavaScript
   - Applied in specific order for maximum effectiveness
   - Tested against major bot detection services

## 🛡️ Anti-Detection System

### How It Works

1. **Automatic Application**: Every browser instance gets anti-detection by default
2. **Centralized Management**: All bypass scripts managed in one location
3. **Consistent Application**: Same protection regardless of entry point
4. **Fail-Safe Design**: Must explicitly disable to remove protection

### Protection Layers

```
User Request
    ↓
BrowserFactory.create() [anti_detection=True by default]
    ↓
AntiDetectionManager.ensure_anti_detection()
    ↓
Apply all 7 bypass scripts
    ↓
Apply browser launch arguments
    ↓
Set realistic browser profile
    ↓
Ready for web access
```

### Verification

The system logs anti-detection status for every browser creation:
- ✅ `"Creating X browser with anti-detection ENABLED"`
- ⚠️ `"Creating X browser with anti-detection DISABLED - NOT RECOMMENDED"`

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/chatcbdai/uoa.git
cd uoa

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## 💻 Quick Start

### Command Line Interface

```bash
# Start the interactive CLI
python main.py

# Example commands:
> Search for the best Python web scraping libraries
> Scrape product details from https://example.com
> Post "Hello World!" to Twitter
> Take a screenshot of https://github.com
```

### Python API

```python
from api import scrape, search, post_to_social

# Scrape a website (anti-detection automatically applied)
data = await scrape("https://example.com")

# Search Google (anti-detection automatically applied)
results = await search("Python web automation")

# Post to social media (anti-detection automatically applied)
await post_to_social(
    content="Hello from UOA!",
    platforms=["twitter", "linkedin"]
)
```

### Direct Browser Usage

```python
from browser import BrowserFactory

# Create a browser (anti-detection enabled by default)
browser = BrowserFactory.create(engine="stealth")
await browser.initialize()

# Navigate to a website (all 7 bypass scripts already applied)
await browser.navigate("https://example.com")

# Interact naturally
await browser.click("button.submit")
await browser.type_text("input[name='search']", "Python automation")

# Clean up
await browser.close()
```

## 📚 Documentation

### Browser Engines

| Engine | JavaScript | Anti-Detection | Use Case |
|--------|-----------|----------------|----------|
| StealthBrowser | ✅ Full | ✅ All 7 scripts | Primary choice for automation |
| PlaywrightBrowser | ✅ Full | ✅ All 7 scripts | When you need Playwright features |
| CamoufoxBrowser | ✅ Full | ⚠️ Firefox built-in | Firefox-specific sites |
| StaticBrowser | ❌ None | ⚠️ Headers only | Simple HTTP requests |

### Configuration

Create a `config.json` file to customize behavior:

```json
{
  "browser": {
    "default_engine": "stealth",
    "headless": true,
    "anti_detection": true
  },
  "llm": {
    "default_provider": "openai",
    "model": "gpt-4"
  }
}
```

### Environment Variables

```bash
# Required for AI features
OPENAI_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key

# Optional
BROWSER_HEADLESS=false
BROWSER_ENGINE=stealth
```

## 🧪 Testing

```bash
# Run anti-detection tests
python tests/test_anti_detection_system.py

# Run all tests
pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas We Need Help

- Additional bypass scripts for emerging detection methods
- Support for more social media platforms
- Performance optimizations
- Documentation improvements
- Bug reports and fixes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate automation purposes only. Users are responsible for compliance with websites' terms of service and applicable laws. Always respect robots.txt and rate limits.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [Camoufox](https://github.com/camoufox/camoufox) for Firefox stealth
- Anti-detection research community
- All our contributors

---

<div align="center">
  <p>
    <strong>Built with ❤️ by the UOA Team</strong>
  </p>
  <p>
    <a href="https://github.com/chatcbdai/uoa/issues">Report Bug</a> •
    <a href="https://github.com/chatcbdai/uoa/issues">Request Feature</a> •
    <a href="https://github.com/chatcbdai/uoa/discussions">Discussions</a>
  </p>
</div>