"""Test script for Google Sheets client with real-time exchange rates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from mcp_servers.portfolio_sheets.sheets_client import SheetsClient
from utils.exchange_rates import get_usd_cop_rate


def test_sheets_client():
    """Test Google Sheets client functionality."""
    
    print("Checking configuration...")
    if not config.validate_google_credentials():
        print("ERROR: Google credentials not configured!")
        print("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file")
        return
    
    if not config.validate_sheet_id():
        print("ERROR: Sheet ID not configured!")
        print("Please set PORTFOLIO_SHEET_ID in .env file")
        return
    
    print("Configuration OK")
    print(f"Sheet ID: {config.PORTFOLIO_SHEET_ID}")
    
    print("\nFetching current USD/COP exchange rate...")
    exchange_rate = get_usd_cop_rate()
    print(f"Current rate: 1 USD = {exchange_rate:,.2f} COP")
    
    print("\nInitializing Sheets client...")
    client = SheetsClient()
    
    print("\nReading positions from Google Sheets...")
    print("(This will open a browser for OAuth if this is the first time)")
    
    try:
        positions = client.read_positions()
        print(f"\nSuccessfully read {len(positions)} positions")
        
        if positions:
            print("\nPositions:")
            for pos in positions:
                print(f"  - {pos.platform}: {pos.symbol}")
                print(f"    Value: {pos.value:,.2f} {pos.currency}")
        
        print("\nReading full portfolio...")
        portfolio = client.read_portfolio()
        
        print(f"\nPortfolio Summary:")
        print(f"  Total positions: {portfolio.total_positions}")
        print(f"  Platforms: {', '.join(portfolio.platforms)}")
        print(f"  Currencies: {', '.join(portfolio.currencies)}")
        
        cop_total = portfolio.total_value_by_currency('COP')
        usd_total = portfolio.total_value_by_currency('USD')
        total_cop = portfolio.total_value(use_live_rates=True)
        
        print(f"\n  COP positions: ${cop_total:,.2f}")
        print(f"  USD positions: ${usd_total:,.2f} (${usd_total * exchange_rate:,.2f} COP)")
        print(f"  Total value (COP): ${total_cop:,.2f}")
        
        print("\nAllocation by platform (using live exchange rate):")
        for platform, percentage in portfolio.allocation_by_platform(use_live_rates=True).items():
            print(f"  {platform}: {percentage:.2f}%")
        
        print("\nAllocation by currency (using live exchange rate):")
        for currency, percentage in portfolio.allocation_by_currency(use_live_rates=True).items():
            print(f"  {currency}: {percentage:.2f}%")
        
        print("\nAll tests passed!")
    
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    test_sheets_client()
