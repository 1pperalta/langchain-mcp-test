"""Test script for market data integration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.tools import PortfolioTools
from config import config  # This triggers .env loading

from agent.tools import PortfolioTools


def test_etf_prices():
    """Test ETF price fetching using real portfolio data."""
    
    print("Testing ETF Price Integration...\n")
    
    print("1. Initializing portfolio tools...")
    tools = PortfolioTools()
    print("Tools initialized\n")
    
    print("2. Fetching ETF prices from real portfolio...")
    print("   (This reads your Google Sheets and fetches live market data)\n")
    
    try:
        result = tools.get_etf_prices("")
        
        print("=" * 60)
        print("ETF PRICE RESULTS:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_etf_prices()