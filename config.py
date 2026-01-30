"""Configuration management for the portfolio application."""
import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / '.env'

load_dotenv(ENV_FILE)


class Config:
    """Application configuration."""
    
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    PORTFOLIO_SHEET_ID: str = os.getenv('PORTFOLIO_SHEET_ID', '')
    # Add after line 18 (after PORTFOLIO_SHEET_ID)
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'openai/gpt-3.5-turbo')
    FIRECRAWL_API_KEY: str = os.getenv('FIRECRAWL_API_KEY', '')
    BUDGET_LIMIT: float = float(os.getenv('BUDGET_LIMIT', '5.0'))
    DAILY_LIMIT: float = float(os.getenv('DAILY_LIMIT', '0.25'))
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'openai/gpt-3.5-turbo')
    
    @classmethod
    def validate_google_credentials(cls) -> bool:
        """Check if Google credentials are configured."""
        return bool(cls.GOOGLE_CLIENT_ID and cls.GOOGLE_CLIENT_SECRET)
    
    @classmethod
    def validate_sheet_id(cls) -> bool:
        """Check if sheet ID is configured."""
        return bool(cls.PORTFOLIO_SHEET_ID)
    
    @classmethod
    def validate_llm_config(cls) -> bool:
        """Check if LLM configuration is complete."""
        return bool(cls.OPENROUTER_API_KEY)
    
    @classmethod
    def get_exchange_rates(cls, use_cache: bool = True) -> dict[str, float]:
        """
        Get current exchange rates.
        
        Args:
            use_cache: If True, uses cached rate (refreshes hourly)
        
        Returns:
            Dictionary with exchange rates (COP base)
        """
        from utils.exchange_rates import get_exchange_rates
        return get_exchange_rates(use_cache=use_cache)
        
    @classmethod
    def validate_firecrawl_config(cls) -> bool:
        """Check if Firecrawl API key is configured."""
        return bool(cls.FIRECRAWL_API_KEY)


config = Config()
