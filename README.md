# Colombian Portfolio Aggregator

AI-powered portfolio management system that reads and analyzes investment data from Google Sheets across multiple Colombian platforms (Lulo, DollarApp, Trii, etc.) using LangChain and OpenRouter.

## Overview

This project provides an intelligent assistant for managing and analyzing personal investment portfolios across multiple Colombian platforms. It combines Google Sheets for data storage, real-time exchange rates, and AI-powered analysis through LangChain agents.

## Features

### Core Functionality
- Read portfolio positions from Google Sheets
- Support for multiple platforms (Lulo, DollarApp, Trii, etc.)
- Multi-currency support (COP, USD)
- Real-time USD/COP exchange rate integration
- Automatic Colombian number format handling (commas in thousands)
- Secure OAuth authentication with Google

### AI Agent Capabilities
- Natural language portfolio queries
- Intelligent tool selection using ReAct pattern
- Portfolio summary and analysis
- Allocation breakdown by platform, currency, and asset type
- Position filtering and search
- Real-time ETF price tracking with yfinance
- Daily performance monitoring
- Budget tracking and cost management

### Web Scraping with Firecrawl
- Colombian market analysis from Portafolio.co
- Financial article research from trusted sources
- Supported sources:
  - Colombian: larepublica.co, portafolio.co, eltiempo.com
  - Global: bloomberg.com, reuters.com, finance.yahoo.com
  - ETF Research: morningstar.com, seekingalpha.com

### Budget Management
- Configurable spending limits (total and daily)
- Automatic usage tracking in JSON format
- Real-time cost monitoring
- Warning alerts at 50%, 80%, and 95% usage
- Detailed usage history and analytics

## Architecture

### Tech Stack

- **Python 3.11+**
- **uv** - Fast Python package manager
- **LangChain** - Agent orchestration with `create_react_agent` and `AgentExecutor`
- **OpenRouter** - LLM API access (supports multiple models)
- **Pydantic** - Data validation and modeling
- **Google Sheets API** - Data source
- **Google OAuth 2.0** - Secure authentication
- **yfinance** - Real-time market data (free, no API key)
- **Firecrawl** - Web scraping for financial news and market data

### Project Structure

```
langchain-mcp-test/
├── models/
│   └── portfolio.py              # Pydantic models for Position and Portfolio
├── mcp_servers/
│   └── portfolio_sheets/
│       ├── sheets_client.py      # Google Sheets API client
│       └── __init__.py
├── agent/
│   ├── llm_client.py            # LangChain + OpenRouter setup
│   ├── tools.py                  # Portfolio analysis tools
│   ├── agent.py                  # Main agent orchestrator
│   └── usage_tracker.py          # Budget tracking system
├── utils/
│   ├── exchange_rates.py         # Real-time exchange rate utilities
│   ├── market_data.py            # ETF price tracking with yfinance
│   ├── firecrawl_client.py       # Web scraping for financial sources
│   ├── mcp_integration.py        # External MCP integration (placeholder)
│   └── __init__.py
├── test/
│   ├── test_models.py            # Model tests
│   ├── test_sheets_client.py     # Google Sheets integration tests
│   ├── test_agent.py             # Agent functionality tests
│   └── test_market_data.py       # ETF price integration tests
├── cli.py                        # Command-line interface
├── config.py                     # Configuration management
├── .env                          # Environment variables (not in git)
├── usage.json                    # API usage tracking (not in git)
└── requirements.txt              # Python dependencies
```

### Agent Architecture

```
User Question (CLI)
    ↓
PortfolioAgent (ReAct Pattern with create_react_agent + AgentExecutor)
    ↓
LLM Decision (OpenRouter - gpt-3.5-turbo)
    ↓
Tool Selection:
    - get_portfolio_summary      → Google Sheets data
    - get_positions              → Google Sheets data
    - get_allocation_by_platform → Google Sheets data
    - get_allocation_by_currency → Google Sheets data
    - get_allocation_by_asset_type → Google Sheets data
    - get_etf_prices             → yfinance API
    - get_market_analysis        → Firecrawl (portafolio.co)
    - research_article           → Firecrawl (trusted sources)
    - research_market            → Web search (placeholder)
    ↓
Tool Execution → Data Sources
    ↓
LLM Analysis & Response
    ↓
Usage Tracking (JSON)
```

### Data Model

**Position** - Represents a single investment:
- `symbol`: Asset name (e.g., "Acciones Dinamico")
- `platform`: Platform name (e.g., "Lulo", "Trii", "Dolar App")
- `currency`: Currency code ("COP" or "USD")
- `value`: Total position value in original currency
- `asset_type`: Type of asset (optional, defaults to "fund")

**Portfolio** - Collection of positions with analysis methods:
- `positions`: List of Position objects
- Methods for total value, allocations, filtering

## Setup

### Prerequisites

- Python 3.11 or higher
- Google Cloud account with Sheets API enabled
- OpenRouter API account
- Firecrawl API key (optional, for market analysis)

### 1. Clone and Install Dependencies

```bash
# Navigate to project directory
cd "/path/to/langchain-mcp-test"

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv
uv sync

# Or with pip (alternative)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Sheets API**
4. Create OAuth 2.0 credentials:
   - Application type: **Desktop app**
   - Download credentials JSON
5. Configure OAuth consent screen:
   - Add your email as test user
   - Set scopes: `../auth/spreadsheets.readonly`

### 3. OpenRouter Setup

1. Go to [OpenRouter](https://openrouter.ai/)
2. Create an account
3. Add credits ($3-5 recommended for personal use)
4. Generate API key from [API Keys page](https://openrouter.ai/keys)
5. Keep Auto Top-Up disabled for budget control

### 4. Firecrawl Setup (Optional)

1. Go to [Firecrawl](https://firecrawl.dev/)
2. Create an account
3. Generate API key
4. Add to your `.env` file

### 5. Environment Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# Google Sheet ID (from sheet URL)
PORTFOLIO_SHEET_ID=your_sheet_id_here

# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
LLM_MODEL=openai/gpt-3.5-turbo

# Budget Limits
BUDGET_LIMIT=5.0
DAILY_LIMIT=0.25

# Firecrawl (for web scraping - optional)
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 6. Google Sheet Format

Your Google Sheet should have these columns in order (A-D):

| A: Activo | B: Plataforma | C: Moneda | D: Valor Original |
|-----------|---------------|-----------|-------------------|
| Asset Name 1 | Platform1 | COP | 100,000 |
| Asset Name 2 | Platform2 | COP | 500,000 |
| Asset Name 3 | Platform3 | USD | 150.50 |

**Important:**
- Column A: Asset name/symbol
- Column B: Platform name
- Column C: Currency (COP or USD)
- Column D: Total value (can include comma thousand separators)
- Additional columns (E, F, G, etc.) are ignored

## Usage

### Interactive Mode (Recommended)

Start a conversational session with the agent:

```bash
uv run cli.py
# Or with activated venv:
python cli.py
```

### Example Questions

**Portfolio queries:**
- "Show me my portfolio"
- "What's my allocation by platform?"
- "How much do I have in Lulo?"
- "Show my USD positions"
- "What's my currency exposure?"

**Market data:**
- "How are my ETFs performing today?"
- "What's the current price of my ETFs?"

**Market analysis (requires Firecrawl):**
- "Give me a market analysis"
- "What's the current Colombian market situation?"

**Article research (requires Firecrawl):**
- "Analyze this article: https://www.portafolio.co/economia/..."

### CLI Options

```bash
# Interactive mode
uv run cli.py

# Single question
uv run cli.py -q "Show my portfolio"

# Check budget status
uv run cli.py --status

# View usage history
uv run cli.py --history
uv run cli.py --history --days 30
```

## Available Tools

| Tool | Description | Data Source |
|------|-------------|-------------|
| `get_portfolio_summary` | Overall portfolio summary | Google Sheets |
| `get_positions` | List positions (optional filter by platform) | Google Sheets |
| `get_allocation_by_platform` | Allocation % by platform | Google Sheets |
| `get_allocation_by_currency` | Allocation % by currency | Google Sheets |
| `get_allocation_by_asset_type` | Allocation % by asset type | Google Sheets |
| `get_etf_prices` | Real-time ETF prices and P&L | yfinance |
| `get_market_analysis` | Colombian market indicators | Firecrawl |
| `research_article` | Scrape financial articles | Firecrawl |
| `research_market` | Market research (placeholder) | - |

## License

MIT License
