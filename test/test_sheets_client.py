"""Test script for Google Sheets client."""
from config import config
from mcp_servers.portfolio_sheets.sheets_client import SheetsClient


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
        total_cop = portfolio.total_value()
        
        print(f"\n  COP positions: ${cop_total:,.2f}")
        print(f"  USD positions: ${usd_total:,.2f}")
        print(f"  Total value (COP): ${total_cop:,.2f}")
        
        print("\nAllocation by platform:")
        for platform, percentage in portfolio.allocation_by_platform().items():
            print(f"  {platform}: {percentage:.2f}%")
        
        print("\nAllocation by currency:")
        for currency, percentage in portfolio.allocation_by_currency().items():
            print(f"  {currency}: {percentage:.2f}%")
        
        print("\nAll tests passed!")
    
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    test_sheets_client()
