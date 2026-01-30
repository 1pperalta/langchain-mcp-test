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

    def get_etf_prices(self, _: str = "") -> str:
        """
        Get current market prices for ETFs in the portfolio.
        Use this when user asks about current prices, P&L, or market performance.
        """
        from utils.market_data import get_multiple_etf_prices
        
        portfolio = self._get_portfolio()
        
        # Common ETF ticker mappings
        ticker_mapping = {
        'euro stoxx 50': 'FEZ',        # Correct: iShares Euro Stoxx 50
        'dow jones': 'DIA',
        'etf euro stoxx 50': 'FEZ',    
        'etf dow jones us': 'DIA',
        }
        
        # Find ETFs in portfolio
        etf_positions = [
            pos for pos in portfolio.positions 
            if 'etf' in pos.symbol.lower() or pos.asset_type == 'etf'
        ]
        
        if not etf_positions:
            return "No ETF positions found in portfolio."
        
        # Map positions to tickers
        tickers_to_fetch = []
        position_ticker_map = {}
        
        for pos in etf_positions:
            symbol_lower = pos.symbol.lower()
            ticker = ticker_mapping.get(symbol_lower)
            
            if ticker:
                tickers_to_fetch.append(ticker)
                position_ticker_map[ticker] = pos
        
        if not tickers_to_fetch:
            return "Could not identify ticker symbols for ETFs. Available ETFs: " + \
                   ", ".join([pos.symbol for pos in etf_positions])
        
        # Fetch prices
        prices = get_multiple_etf_prices(tickers_to_fetch)
        
        if not prices:
            return "Failed to fetch ETF prices. Market may be closed or tickers incorrect."
        
        result = "Current ETF Prices:\n\n"
        
        for ticker, price_data in prices.items():
            pos = position_ticker_map.get(ticker)
            
            result += f"{price_data['name']} ({ticker}):\n"
            result += f"  Current Price: ${price_data['current_price']:.2f} {price_data['currency']}\n"
            result += f"  Change: ${price_data['change']:.2f} ({price_data['change_percent']:.2f}%)\n"
            
            if pos and pos.quantity and pos.average_price:
                from utils.market_data import calculate_position_pnl
                pnl = calculate_position_pnl(
                    pos.average_price,
                    price_data['current_price'],
                    pos.quantity,
                    pos.currency
                )
                result += f"  Your Position: {pos.quantity:.2f} shares\n"
                result += f"  Cost Basis: ${pnl['cost_basis']:.2f}\n"
                result += f"  Current Value: ${pnl['current_value']:.2f}\n"
                result += f"  P&L: ${pnl['unrealized_pnl']:.2f} ({pnl['pnl_percent']:.2f}%)\n"
            
            result += "\n"
        
        return result    
    
    def get_market_analysis(self, focus: str = "colombian") -> str:
        """
        Get current market analysis and indicators from trusted financial sources.
        Use when user asks about market conditions, economic outlook, or investment climate.
        
        Args:
            focus: Market focus - "colombian" for Colombian market data
        
        Returns:
            Market summary with key indicators
        """
        from utils.firecrawl_client import get_colombian_market_summary
        
        if focus.lower() == "colombian" or not focus:
            return get_colombian_market_summary()
        else:
            return f"Market analysis for '{focus}' not yet implemented. Currently supports: 'colombian'"
        
    def research_article(self, url: str) -> str:
        """
        Scrape and analyze a financial article from trusted sources.
        Use when user provides a specific article URL to analyze.
        
        Args:
            url: Article URL from trusted source (La República, Portafolio, Bloomberg, etc.)
        
        Returns:
            Article content and analysis
        """
        from utils.firecrawl_client import scrape_financial_article
        
        if not url or not url.startswith('http'):
            return "Please provide a valid article URL from a trusted source (larepublica.co, portafolio.co, bloomberg.com, etc.)"
        
        return scrape_financial_article(url)
    
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
    def research_market(self, query: str) -> str:
        """
        Research market information, news, or investment topics using web search.
        
        Args:
            query: What to research (e.g., "Colombian investment platforms comparison")
        
        Returns:
            Research results and insights
        """
        if not query:
            return "Please provide a research query."
        
        # For now, provide guidance on what this would do
        research_topics = {
            'colombian platforms': 'Lulo vs Trii vs DollarApp comparison, fees, rates',
            'usd cop': 'USD/COP exchange rate trends and forecasts',
            'etf performance': 'Euro Stoxx 50 and Dow Jones recent performance',
            'market news': 'Latest Colombian investment market news',
        }
        
        result = f"Market Research: {query}\n\n"
        result += "This tool would search for:\n"
        
        # Suggest relevant searches
        for topic, description in research_topics.items():
            if topic in query.lower():
                result += f"- {description}\n"
        
        result += "\nNote: Web search MCP integration pending. "
        result += "Manual implementation needed through Cursor's MCP system."
        
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
        Tool(
            name="get_etf_prices",
            func=portfolio_tools.get_etf_prices,
            description="Get current market prices for ETFs in portfolio. Shows real-time prices, daily changes, and P&L if purchase data available. Use when user asks about ETF performance, current values, or profit/loss."
        ),
        Tool(
            name="get_market_analysis",
            func=portfolio_tools.get_market_analysis,
            description="Get current market analysis and indicators from trusted financial sources. Use when user asks about market conditions, economic outlook, or investment climate. Input: market focus (optional, e.g., 'colombian') or empty string for general market analysis."
        ),
        Tool(
            name="research_article",
            func=portfolio_tools.research_article,
            description="Scrape and analyze a financial article from trusted sources. Use when user provides a specific article URL to analyze. Input: article URL from trusted source (larepublica.co, portafolio.co, bloomberg.com, etc.)"
        ),
        Tool(
            name="research_market",
            func=portfolio_tools.research_market,
            description="Research market information, news, or investment topics using web search. Use when user asks about market trends, investment opportunities, or specific topics."
        ),
    ]


    