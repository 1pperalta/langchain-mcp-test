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
- Budget tracking and cost management

### Budget Management
- Configurable spending limits (total and daily)
- Automatic usage tracking in JSON format
- Real-time cost monitoring
- Warning alerts at 50%, 80%, and 95% usage
- Detailed usage history and analytics

## Architecture

### Tech Stack

- **Python 3.11+**
- **LangChain** - Agent orchestration and tool management
- **OpenRouter** - LLM API access (supports multiple models)
- **Pydantic** - Data validation and modeling
- **Google Sheets API** - Data source
- **Google OAuth 2.0** - Secure authentication

### Project Structure

```
langgraph-mcp-test/
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
│   └── __init__.py
├── test/
│   ├── test_models.py            # Model tests
│   ├── test_sheets_client.py     # Google Sheets integration tests
│   └── test_agent.py             # Agent functionality tests
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
PortfolioAgent (ReAct Pattern)
    ↓
LLM Decision (OpenRouter - gpt-3.5-turbo)
    ↓
Tool Selection:
    - get_portfolio_summary
    - get_positions
    - get_allocation_by_platform
    - get_allocation_by_currency
    - get_allocation_by_asset_type
    ↓
Tool Execution → Data from Google Sheets
    ↓
LLM Analysis & Response
    ↓
Usage Tracking (JSON)
```

### Data Model

**Position** - Represents a single investment:
- `symbol`: Asset name (e.g., "Acciones Dinámico")
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

### 1. Clone and Install Dependencies

```bash
# Navigate to project directory
cd "/path/to/langgraph-mcp-test"

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
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

### 4. Environment Configuration

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
```

### 5. Google Sheet Format

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
python cli.py
```

**Example session:**
```
==============================================================
  Colombian Portfolio Aggregator - AI Assistant
==============================================================

Interactive Mode - Ask questions about your portfolio
Commands: 'exit' or 'quit' to exit, 'status' for budget, 'history' for usage

You: Show me my portfolio

Assistant: Your portfolio has 7 positions with a total value of $969,813.84 COP.
You're invested across 3 platforms: Trii (27.26%), Lulo (48.63%), and Dolar App (24.11%).

You: What's my allocation by currency?
