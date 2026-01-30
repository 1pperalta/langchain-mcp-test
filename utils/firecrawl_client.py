"""Firecrawl integration for web scraping trusted financial sources."""
from typing import Optional
from firecrawl import Firecrawl
from config import config


TRUSTED_SOURCES = {
    'colombian_finance': [
        'larepublica.co',
        'portafolio.co',
        'eltiempo.com'
    ],
    'global_markets': [
        'bloomberg.com',
        'reuters.com',
        'finance.yahoo.com'
    ],
    'etf_research': [
        'finance.yahoo.com',
        'morningstar.com',
        'seekingalpha.com'
    ]
}


def is_trusted_source(url: str) -> bool:
    """Check if URL is from a trusted source."""
    for category in TRUSTED_SOURCES.values():
        for domain in category:
            if domain in url:
                return True
    return False


def scrape_url(url: str) -> Optional[dict]:
    """
    Scrape content from a URL using Firecrawl.
    
    Args:
        url: URL to scrape
    
    Returns:
        Dictionary with markdown content and metadata or None if failed
    """
    if not config.FIRECRAWL_API_KEY:
        print("Warning: Firecrawl API key not configured")
        return None
    
    if not is_trusted_source(url):
        print(f"Warning: {url} is not a trusted source")
        return None
    
    try:
        app = Firecrawl(api_key=config.FIRECRAWL_API_KEY)
        
        result = app.scrape(url, formats=['markdown'])
        
        return {
            'url': url,
            'title': result.metadata.title if result.metadata else 'Unknown',
            'content': result.markdown or '',
            'description': result.metadata.description if result.metadata else '',
            'source_url': result.metadata.url if result.metadata else url
        }
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def get_colombian_market_summary() -> str:
    """
    Get Colombian market summary from Portafolio.co.
    
    Returns:
        Market summary with key indicators
    """
    url = "https://www.portafolio.co/economia"
    result = scrape_url(url)
    
    if not result:
        return "Failed to fetch Colombian market data."
    
    content = result['content']
    
    output = f"Colombian Market Summary (Source: Portafolio.co)\n\n"
    
    if 'TRM' in content or 'Dólar' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines[:50]):
            if any(indicator in line for indicator in ['TRM', 'Dólar', 'ICOLCAP', 'Euro', 'Tasa de interés']):
                output += f"{line}\n"
                if i+1 < len(lines):
                    output += f"{lines[i+1]}\n"
    
    output += f"\n\nFull content available at: {result['url']}"
    
    return output


def scrape_financial_article(url: str) -> str:
    """
    Scrape a specific financial article.
    
    Args:
        url: Article URL
    
    Returns:
        Article content
    """
    result = scrape_url(url)
    
    if not result:
        return f"Failed to scrape {url}. Ensure it's from a trusted source."
    
    output = f"Article: {result['title']}\n"
    output += f"Source: {result['source_url']}\n"
    output += f"Description: {result['description']}\n\n"
    output += "Content:\n"
    output += result['content'][:3000]
    
    if len(result['content']) > 3000:
        output += f"\n\n... (truncated, full article has {len(result['content'])} characters)"
    
    return output