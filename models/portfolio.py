"""Pydantic models for portfolio data validation and structure."""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Position(BaseModel):
    """Represents a single investment position."""
    
    platform: str = Field(..., min_length=1, description="Investment platform name")
    symbol: str = Field(..., min_length=1, description="Asset symbol or ticker")
    asset_type: Literal["stock", "etf", "fund", "cash"] = Field(
        ..., 
        description="Type of asset"
    )
    quantity: float = Field(..., gt=0, description="Number of units held")
    average_price: float = Field(..., gt=0, description="Average purchase price per unit")
    currency: Literal["COP", "USD"] = Field(..., description="Currency of the position")
    purchase_date: date = Field(..., description="Date of purchase")
    
    @field_validator('quantity', 'average_price')
    @classmethod
    def validate_positive_values(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Value must be positive')
        return v
    
    @field_validator('platform', 'symbol')
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Value cannot be empty or whitespace')
        return v.strip()
    
    @property
    def total_value(self) -> float:
        """Calculate total value of this position."""
        return self.quantity * self.average_price
    
    def to_currency(self, exchange_rate: float = 1.0) -> float:
        """Convert position value to another currency."""
        return self.total_value * exchange_rate


class Portfolio(BaseModel):
    """Represents a complete investment portfolio."""
    
    positions: list[Position] = Field(default_factory=list, description="List of positions")
    
    @property
    def total_positions(self) -> int:
        """Total number of positions."""
        return len(self.positions)
    
    @property
    def platforms(self) -> set[str]:
        """Unique platforms in portfolio."""
        return {pos.platform for pos in self.positions}
    
    @property
    def currencies(self) -> set[str]:
        """Unique currencies in portfolio."""
        return {pos.currency for pos in self.positions}
    
    def total_value_by_currency(self, currency: str) -> float:
        """Calculate total value for a specific currency."""
        return sum(
            pos.total_value 
            for pos in self.positions 
            if pos.currency == currency
        )
    
    def total_value(self, exchange_rates: dict[str, float] | None = None) -> float:
        """
        Calculate total portfolio value in COP.
        
        Args:
            exchange_rates: Optional dict mapping currency codes to COP exchange rates
                          e.g., {"USD": 4000.0} means 1 USD = 4000 COP
        
        Returns:
            Total value in COP
        """
        if exchange_rates is None:
            exchange_rates = {"COP": 1.0, "USD": 4000.0}
        
        total = 0.0
        for pos in self.positions:
            rate = exchange_rates.get(pos.currency, 1.0)
            total += pos.total_value * rate
        
        return total
    
    def allocation_by_platform(self) -> dict[str, float]:
        """Calculate percentage allocation by platform."""
        if not self.positions:
            return {}
        
        total = self.total_value()
        platform_values = {}
        
        for pos in self.positions:
            rate = 4000.0 if pos.currency == "USD" else 1.0
            value = pos.total_value * rate
            platform_values[pos.platform] = platform_values.get(pos.platform, 0.0) + value
        
        return {
            platform: (value / total) * 100 
            for platform, value in platform_values.items()
        }
    
    def allocation_by_currency(self) -> dict[str, float]:
        """Calculate percentage allocation by currency."""
        if not self.positions:
            return {}
        
        total = self.total_value()
        currency_values = {}
        
        for pos in self.positions:
            rate = 4000.0 if pos.currency == "USD" else 1.0
            value = pos.total_value * rate
            currency_values[pos.currency] = currency_values.get(pos.currency, 0.0) + value
        
        return {
            currency: (value / total) * 100 
            for currency, value in currency_values.items()
        }
    
    def allocation_by_asset_type(self) -> dict[str, float]:
        """Calculate percentage allocation by asset type."""
        if not self.positions:
            return {}
        
        total = self.total_value()
        type_values = {}
        
        for pos in self.positions:
            rate = 4000.0 if pos.currency == "USD" else 1.0
            value = pos.total_value * rate
            type_values[pos.asset_type] = type_values.get(pos.asset_type, 0.0) + value
        
        return {
            asset_type: (value / total) * 100 
            for asset_type, value in type_values.items()
        }
    
    def get_positions_by_platform(self, platform: str) -> list[Position]:
        """Get all positions for a specific platform."""
        return [pos for pos in self.positions if pos.platform == platform]
    
    def get_positions_by_symbol(self, symbol: str) -> list[Position]:
        """Get all positions for a specific symbol."""
        return [pos for pos in self.positions if pos.symbol.upper() == symbol.upper()]
