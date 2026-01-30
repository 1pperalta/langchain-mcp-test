"""Test Firecrawl integration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from utils.firecrawl_client import scrape_url


def test_firecrawl():
    print("Testing Firecrawl integration...\n")
    
    if not config.FIRECRAWL_API_KEY:
        print("ERROR: FIRECRAWL_API_KEY not configured in .env")
        return
    
    print("API key configured\n")
    
    # Test with a trusted Colombian source
    test_url = "https://www.portafolio.co/economia"
    
    print(f"Scraping: {test_url}\n")
    result = scrape_url(test_url)
    
    if result:
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
        print(f"Content length: {len(result['content'])} characters")
        print(f"\nFirst 500 chars:\n{result['content'][:500]}...")
        print("\nTest successful!")
    else:
        print("Test failed")


if __name__ == "__main__":
    test_firecrawl()