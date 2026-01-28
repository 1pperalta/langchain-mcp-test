"""Test script for portfolio agent."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.agent import PortfolioAgent
from agent.usage_tracker import UsageTracker
from config import config


def test_agent():
    """Test the portfolio agent with a simple query."""
    
    print("Testing Portfolio Agent...\n")
    
    print("1. Checking configuration...")
    if not config.validate_google_credentials():
        print("❌ Google credentials not configured!")
        return
    
    if not config.validate_sheet_id():
        print("❌ Sheet ID not configured!")
        return
    
    if not config.OPENROUTER_API_KEY:
        print("❌ OpenRouter API key not configured!")
        return
    
    print("✓ Configuration OK\n")
    
    print("2. Initializing agent...")
    tracker = UsageTracker(
        budget_limit=config.BUDGET_LIMIT,
        daily_limit=config.DAILY_LIMIT
    )
    agent = PortfolioAgent(tracker=tracker)
    print("✓ Agent initialized\n")
    
    print("3. Testing simple query...")
    print("   Question: 'Show me a summary of my portfolio'\n")
    
    try:
        response = agent.query("Show me a summary of my portfolio", query_type="test")
        
        print("=" * 60)
        print("RESPONSE:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        print("\n4. Checking budget status...")
        status = tracker.get_budget_status()
        print(f"   Total spent: ${status['total_spent']:.4f}")
        print(f"   Remaining: ${status['total_remaining']:.4f}")
        print(f"   Status: {status['status']}")
        
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    test_agent()