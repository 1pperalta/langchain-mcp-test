"""Exchange rate utilities for fetching real-time USD/COP rates."""
import requests
from datetime import datetime, timedelta
from typing import Optional


class ExchangeRateCache:
    """Cache for exchange rates to avoid excessive API calls."""
    
    def __init__(self, cache_duration_hours: int = 1):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self._cached_rate: Optional[float] = None
        self._cache_timestamp: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if cached rate is still valid."""
        if self._cached_rate is None or self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self.cache_duration
    
    def get(self) -> Optional[float]:
        """Get cached rate if valid."""
        if self.is_valid():
            return self._cached_rate
        return None
    
    def set(self, rate: float) -> None:
        """Cache a new rate."""
        self._cached_rate = rate
        self._cache_timestamp = datetime.now()


_cache = ExchangeRateCache()


def get_usd_cop_rate(use_cache: bool = True) -> float:
    """
    Fetch current USD to COP exchange rate.
    
    Uses exchangerate-api.com free tier (1500 requests/month).
    Falls back to default rate (4000) if API fails.
    
    Args:
        use_cache: If True, returns cached rate if available (default: True)
    
    Returns:
        Exchange rate as float (e.g., 4000.0 means 1 USD = 4000 COP)
    """
    DEFAULT_RATE = 4000.0
    
    if use_cache:
        cached_rate = _cache.get()
        if cached_rate is not None:
            return cached_rate
    
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('result') == 'success':
            rates = data.get('rates', {})
            cop_rate = rates.get('COP')
            
            if cop_rate:
                _cache.set(cop_rate)
                return cop_rate
        
        print(f"Warning: Could not fetch exchange rate, using default: {DEFAULT_RATE}")
        return DEFAULT_RATE
    
    except requests.exceptions.RequestException as e:
        print(f"Warning: Exchange rate API error ({e}), using default: {DEFAULT_RATE}")
        return DEFAULT_RATE
    except Exception as e:
        print(f"Warning: Unexpected error fetching exchange rate ({e}), using default: {DEFAULT_RATE}")
        return DEFAULT_RATE


def get_exchange_rates(base: str = "COP", use_cache: bool = True) -> dict[str, float]:
    """
    Get exchange rates for portfolio calculations.
    
    Args:
        base: Base currency (default: "COP")
        use_cache: Whether to use cached rates
    
    Returns:
        Dictionary with currency codes and rates relative to base currency
    """
    usd_cop_rate = get_usd_cop_rate(use_cache=use_cache)
    
    return {
        'COP': 1.0,
        'USD': usd_cop_rate,
    }
