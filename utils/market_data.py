"""Market data utilities using yfinance."""
import yfinance as yf
from typing import Optional


def get_etf_price(ticker: str) -> Optional[dict]:
    """
    Get current price and info for an ETF.
    
    Args:
        ticker: ETF ticker symbol (e.g., 'STOXX50E', 'DIA')
    
    Returns:
        Dictionary with price info or None if failed
    """
    try:
        etf = yf.Ticker(ticker)
        info = etf.info
        
        current_price = info.get('regularMarketPrice') or info.get('currentPrice')
        previous_close = info.get('previousClose')
        
        if not current_price:
            return None
        
        change = current_price - previous_close if previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'previous_close': previous_close,
            'change': change,
            'change_percent': change_percent,
            'currency': info.get('currency', 'USD'),
            'name': info.get('longName', ticker)
        }
    
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def get_multiple_etf_prices(tickers: list[str]) -> dict[str, dict]:
    """
    Get prices for multiple ETFs.
    
    Args:
        tickers: List of ticker symbols
    
    Returns:
        Dictionary mapping ticker to price info
    """
    results = {}
    for ticker in tickers:
        price_data = get_etf_price(ticker)
        if price_data:
            results[ticker] = price_data
    
    return results


def calculate_position_pnl(
    purchase_price: float,
    current_price: float,
    quantity: float,
    currency: str = "USD"
) -> dict:
    """
    Calculate P&L for a position.
    
    Args:
        purchase_price: Price paid per unit
        current_price: Current market price
        quantity: Number of units
        currency: Currency of the position
    
    Returns:
        Dictionary with P&L calculations
    """
    cost_basis = purchase_price * quantity
    current_value = current_price * quantity
    unrealized_pnl = current_value - cost_basis
    pnl_percent = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
    
    return {
        'cost_basis': cost_basis,
        'current_value': current_value,
        'unrealized_pnl': unrealized_pnl,
        'pnl_percent': pnl_percent,
        'currency': currency
    }