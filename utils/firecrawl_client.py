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
        
        # Use scrape() not scrape_url()
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