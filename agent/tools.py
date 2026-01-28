"""LangChain tools for portfolio operations."""
from typing import Optional
from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from mcp_servers.portfolio_sheets.sheets_client import SheetsClient


class PortfolioTools:
    """Collection of portfolio analysis tools."""
    
    def __init__(self):
        self.client = SheetsClient()
        self._portfolio_cache = None
        self._cache_time = None
    
    def _get_portfolio(self):
        """Get portfolio with simple caching (5 min)."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        if self._portfolio_cache is None or \
           self._cache_time is None or \
           now - self._cache_time > timedelta(minutes=5):
            self._portfolio_cache = self.client.read_portfolio()
            self._cache_time = now
        
        return self._portfolio_cache
    
    def get_portfolio_summary(self, _: str = "") -> str:
        """
        Get overall portfolio summary including total value, number of positions, platforms, and currencies.
        Use this when user asks general questions about their portfolio.
        """
        portfolio = self._get_portfolio()
        
        total_cop = portfolio.total_value(use_live_rates=True)
        cop_total = portfolio.total_value_by_currency('COP')
        usd_total = portfolio.total_value_by_currency('USD')
        
        from utils.exchange_rates import get_usd_cop_rate
        exchange_rate = get_usd_cop_rate()
        
        summary = f"""Portfolio Summary:
- Total Positions: {portfolio.total_positions}
- Total Value: ${total_cop:,.2f} COP
- Platforms: {', '.join(portfolio.platforms)}
- Currencies: {', '.join(portfolio.currencies)}

By Currency:
- COP: ${cop_total:,.2f}
- USD: ${usd_total:,.2f} (${usd_total * exchange_rate:,.2f} COP at rate {exchange_rate:,.2f})

Current Exchange Rate: 1 USD = {exchange_rate:,.2f} COP
"""
        return summary
    
    def get_positions(self, platform: str = "") -> str:
        """
        Get list of all positions, optionally filtered by platform.
        Args:
            platform: Optional platform name to filter (e.g., 'Lulo', 'Trii', 'Dolar App')
        """
        portfolio = self._get_portfolio()
        
        if platform:
            positions = portfolio.get_positions_by_platform(platform)
            if not positions:
                return f"No positions found for platform: {platform}"
        else:
            positions = portfolio.positions
        
        result = f"Positions ({len(positions)}):\n\n"
        for pos in positions:
            result += f"- {pos.symbol} ({pos.platform})\n"
            result += f"  Value: ${pos.value:,.2f} {pos.currency}\n"
            result += f"  Type: {pos.asset_type}\n\n"
        
        return result
    
    def get_allocation_by_platform(self, _: str = "") -> str:
        """
        Get portfolio allocation breakdown by platform (percentage per platform).
        Shows how your investments are distributed across different platforms.
        """
        portfolio = self._get_portfolio()
        allocations = portfolio.allocation_by_platform(use_live_rates=True)
        
        result = "Allocation by Platform:\n\n"
        for platform, percentage in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
            result += f"- {platform}: {percentage:.2f}%\n"
        
        return result
    
    def get_allocation_by_currency(self, _: str = "") -> str:
        """
        Get portfolio allocation breakdown by currency (percentage in COP vs USD).
        Shows currency exposure in your portfolio.
        """
        portfolio = self._get_portfolio()
        allocations = portfolio.allocation_by_currency(use_live_rates=True)
        
        result = "Allocation by Currency:\n\n"
        for currency, percentage in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
            result += f"- {currency}: {percentage:.2f}%\n"
        
        return result
    
    def get_allocation_by_asset_type(self, _: str = "") -> str:
        """
        Get portfolio allocation breakdown by asset type (stocks, ETFs, funds, cash).
        Shows diversification across different asset classes.
        """
        portfolio = self._get_portfolio()
        allocations = portfolio.allocation_by_asset_type(use_live_rates=True)
        
        result = "Allocation by Asset Type:\n\n"
        for asset_type, percentage in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
            result += f"- {asset_type}: {percentage:.2f}%\n"
        
        return result


def create_portfolio_tools() -> list[Tool]:
    """Create LangChain tools for portfolio operations."""
    portfolio_tools = PortfolioTools()
    
    return [
        Tool(
            name="get_portfolio_summary",
            func=portfolio_tools.get_portfolio_summary,
            description="Get overall portfolio summary including total value, positions count, platforms, and currencies. Use this for general portfolio questions."
        ),
        Tool(
            name="get_positions",
            func=portfolio_tools.get_positions,
            description="Get list of all positions, optionally filtered by platform. Input: platform name (optional, e.g., 'Lulo', 'Trii', 'Dolar App') or empty string for all positions."
        ),
        Tool(
            name="get_allocation_by_platform",
            func=portfolio_tools.get_allocation_by_platform,
            description="Get portfolio allocation breakdown by platform showing percentage per platform. Use this when user asks about distribution across platforms."
        ),
        Tool(
            name="get_allocation_by_currency",
            func=portfolio_tools.get_allocation_by_currency,
            description="Get portfolio allocation breakdown by currency (COP vs USD). Use this when user asks about currency exposure."
        ),
        Tool(
            name="get_allocation_by_asset_type",
            func=portfolio_tools.get_allocation_by_asset_type,
            description="Get portfolio allocation breakdown by asset type (stocks, ETFs, funds, cash). Use this when user asks about diversification."
        ),
    ]