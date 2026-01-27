"""Quick test script for Pydantic models."""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.portfolio import Position, Portfolio


def test_models():
    """Test basic model functionality."""
    
    print("Testing Position model...")
    pos1 = Position(
        platform="Lulo",
        symbol="ECOPETROL",
        asset_type="stock",
        quantity=100,
        average_price=2500,
        currency="COP",
        purchase_date=date(2024, 1, 15)
    )
    print(f"Position created: {pos1.symbol} - Total value: ${pos1.total_value:,.0f} {pos1.currency}")
    
    pos2 = Position(
        platform="DollarApp",
        symbol="VOO",
        asset_type="etf",
        quantity=10,
        average_price=450,
        currency="USD",
        purchase_date=date(2024, 2, 1)
    )
    print(f"Position created: {pos2.symbol} - Total value: ${pos2.total_value:,.0f} {pos2.currency}")
    
    print("\nTesting Portfolio model...")
    portfolio = Portfolio(positions=[pos1, pos2])
    
    print(f"Total positions: {portfolio.total_positions}")
    print(f"Platforms: {portfolio.platforms}")
    print(f"Currencies: {portfolio.currencies}")
    print(f"Total value (COP): ${portfolio.total_value():,.0f}")
    print(f"Total value (USD only): ${portfolio.total_value_by_currency('USD'):,.0f}")
    print(f"Total value (COP only): ${portfolio.total_value_by_currency('COP'):,.0f}")
    
    print("\nAllocation by platform:")
    for platform, percentage in portfolio.allocation_by_platform().items():
        print(f"  {platform}: {percentage:.2f}%")
    
    print("\nAllocation by currency:")
    for currency, percentage in portfolio.allocation_by_currency().items():
        print(f"  {currency}: {percentage:.2f}%")
    
    print("\nAllocation by asset type:")
    for asset_type, percentage in portfolio.allocation_by_asset_type().items():
        print(f"  {asset_type}: {percentage:.2f}%")
    
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    test_models()
