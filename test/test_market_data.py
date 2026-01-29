# Create test/test_market_data.py
from utils.market_data import get_etf_price, get_multiple_etf_prices

# Test single ETF
price = get_etf_price('DIA')
print(f"Dow Jones ETF: ${price['current_price']}")

# Test multiple
prices = get_multiple_etf_prices(['DIA', 'STOXX50E'])
for ticker, data in prices.items():
    print(f"{ticker}: ${data['current_price']} ({data['change_percent']:.2f}%)")