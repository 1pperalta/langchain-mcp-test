# Colombian Portfolio Aggregator

AI-powered portfolio management tool that reads and analyzes investment data from Google Sheets across multiple Colombian platforms (Lulo, DollarApp, Trii, etc.).

## Current Status: MVP (Phase 1)

The MVP successfully reads portfolio data from Google Sheets and provides portfolio analysis capabilities.

## Features

- Read portfolio positions from Google Sheets
- Support for multiple platforms (Lulo, DollarApp, Trii, etc.)
- Multi-currency support (COP, USD)
- Automatic Colombian number format handling (commas in thousands)
- Portfolio value calculations and aggregations
- Allocation analysis by platform and currency
- Secure OAuth authentication with Google

## Architecture

### Tech Stack

- **Python 3.11+**
- **Pydantic** - Data validation and modeling
- **Google Sheets API** - Data source
- **Google OAuth 2.0** - Secure authentication

### Project Structure

```
langgraph-mcp-test/
├── models/
│   └── portfolio.py          # Pydantic models for Position and Portfolio
├── mcp_servers/
│   └── portfolio_sheets/
│       ├── sheets_client.py  # Google Sheets API client
│       └── __init__.py
├── config.py                 # Configuration management
├── test_sheets_client.py     # Test script
├── .env                      # Environment variables (not in git)
├── .cursorrules              # Project coding standards
└── requirements.txt          # Python dependencies
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
- UV package manager (recommended) or pip
- Google Cloud Project with Sheets API enabled
- OAuth 2.0 credentials (Desktop application type)

### Installation

1. Clone the repository:
```bash
cd "/path/to/langgraph-mcp-test"
```

2. Create virtual environment with UV:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_client_secret_here
PORTFOLIO_SHEET_ID=1abcdefghijklmnopqrstuvwxyz123456789
```

### Google Cloud Setup

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com
   - Create a new project

2. **Enable Google Sheets API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: **Desktop app**
   - Download the credentials JSON
   - Copy `client_id` and `client_secret` to your `.env` file

4. **Configure OAuth Consent Screen**:
   - Go to "OAuth consent screen"
   - Set to "Testing" mode
   - Add yourself as a test user (your email)

### Google Sheet Format

Your Google Sheet should have these columns:

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

### Running the Test

```bash
# Activate virtual environment
source .venv/bin/activate

# Run test script
python test_sheets_client.py
```

### First Run (OAuth Authentication)

The first time you run the script:
1. A browser window will open
2. Sign in with your Google account
3. Authorize the application
4. The authentication token is saved locally (`token.json`)
5. Future runs won't require re-authentication

### Example Output

```
Configuration OK
Sheet ID: 1abc...xyz

Successfully read X positions

Positions:
  - Platform1: Asset Name 1
    Value: XX,XXX.XX COP
  - Platform2: Asset Name 2
    Value: XXX,XXX.XX COP
  - Platform3: Asset Name 3
    Value: XX.XX USD

Portfolio Summary:
  Total positions: X
  Platforms: Platform1, Platform2, Platform3
  Currencies: COP, USD
  
  COP positions: $XXX,XXX.XX
  USD positions: $XXX.XX
  Total value (COP): $X,XXX,XXX.XX

Allocation by platform:
  Platform1: XX.XX%
  Platform2: XX.XX%
  Platform3: XX.XX%

Allocation by currency:
  COP: XX.XX%
  USD: XX.XX%
```

### Using in Code

```python
from mcp_servers.portfolio_sheets.sheets_client import SheetsClient

# Initialize client
client = SheetsClient()

# Read positions
positions = client.read_positions()

# Or read complete portfolio
portfolio = client.read_portfolio()

# Get total value in COP
total = portfolio.total_value()

# Get allocation by platform
allocation = portfolio.allocation_by_platform()
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client Secret | Yes |
| `PORTFOLIO_SHEET_ID` | Google Sheet ID (from URL) | Yes |

### Exchange Rates

Default exchange rate (hardcoded in `config.py`):
- USD to COP: 4000

Can be customized by passing `exchange_rates` dict to `portfolio.total_value()`.

## Development

### Project Principles

This project follows strict coding standards defined in `.cursorrules`:

- **SOLID principles** for clean architecture
- **No hardcoded values** - use environment variables
- **Type hints** required for all functions
- **Minimal comments** - code should be self-documenting
- **Pydantic validation** for data integrity

### Adding New Features

Current architecture supports easy extension:

1. **New data sources**: Implement additional sheet formats in `sheets_client.py`
2. **New calculations**: Add methods to `Portfolio` class in `models/portfolio.py`
3. **New platforms**: Automatically supported when added to Google Sheet

## Roadmap

### Completed (MVP - Phase 1)
- [x] Google Sheets integration with OAuth
- [x] Pydantic data models
- [x] Colombian number format support
- [x] Multi-platform aggregation
- [x] Multi-currency support
- [x] Portfolio calculations (total, allocations)
- [x] Test script

### Planned Features

**Phase 2: MCP Server**
- [ ] FastMCP server implementation
- [ ] MCP tools for portfolio operations
- [ ] Direct Python integration (no separate process)

**Phase 3: CLI Interface**
- [ ] Command-based CLI (no AI)
- [ ] Interactive portfolio queries
- [ ] Report generation

**Phase 4: AI Integration**
- [ ] LangChain agent setup
- [ ] OpenRouter integration
- [ ] Natural language queries
- [ ] Investment insights

**Phase 5: Advanced Features**
- [ ] Real-time market data integration
- [ ] Colombian tax calculations
- [ ] Performance tracking over time
- [ ] Portfolio rebalancing suggestions
- [ ] CSV import/export

## Troubleshooting

### OAuth Errors

**Error: "invalid_client"**
- Ensure OAuth client type is "Desktop app"
- Verify CLIENT_ID and CLIENT_SECRET are correct
- Check that you're added as a test user in OAuth consent screen

**Error: "Google Sheets API has not been used"**
- Enable Google Sheets API in Google Cloud Console
- Wait 1-2 minutes for activation to propagate

### Data Reading Issues

**No positions loaded**
- Check Google Sheet tab name (should match code expectation)
- Verify sheet has data in columns A-D
- Ensure numbers are in correct format

**Numbers not parsing**
- Code supports: `60,000`, `60000`, `60,000.00`
- Avoid currency symbols in the value column

## Security

- OAuth tokens stored locally in `token.json` (gitignored)
- Never commit `.env` file with credentials
- Read-only access to Google Sheets (can be upgraded if needed)
- All sensitive data excluded from version control

## License

Personal project - Not for commercial use.

## Author

Built as a learning project for LangChain, MCP, and portfolio management.

## Support

For issues or questions, check:
1. `.cursorrules` - Project coding standards
2. `test_sheets_client.py` - Example usage
3. Error messages usually indicate the exact problem
