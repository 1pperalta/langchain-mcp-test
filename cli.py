"""Command-line interface for portfolio agent."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import argparse
from agent.agent import PortfolioAgent
from agent.usage_tracker import UsageTracker
from config import config


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("  Colombian Portfolio Aggregator - AI Assistant")
    print("="*60 + "\n")


def print_budget_status(tracker: UsageTracker):
    """Print current budget status."""
    status = tracker.get_budget_status()
    
    print(f"\nBudget Status: {status['status']}")
    print(f"  Total: ${status['total_spent']:.4f} / ${status['total_limit']:.2f}")
    print(f"  Remaining: ${status['total_remaining']:.4f} ({100 - status['total_percent']:.1f}%)")
    print(f"  Today: ${status['daily_spent']:.4f} / ${status['daily_limit']:.2f}")
    print()


def print_usage_history(tracker: UsageTracker, days: int = 7):
    """Print usage history."""
    history = tracker.get_usage_history(days=days)
    
    if not history:
        print("No usage history found.\n")
        return
    
    print(f"\nUsage History (Last {days} days):\n")
    print(f"{'Date':<20} {'Model':<25} {'Tokens':<15} {'Cost':<10} {'Type':<15}")
    print("-" * 90)
    
    for record in history[:20]:
        date_str = record.timestamp[:19].replace('T', ' ')
        tokens = f"{record.input_tokens}->{record.output_tokens}"
        cost_str = f"${record.cost:.4f}"
        model_short = record.model.split('/')[-1][:23]
        
        print(f"{date_str:<20} {model_short:<25} {tokens:<15} {cost_str:<10} {record.query_type:<15}")
    
    if len(history) > 20:
        print(f"\n... and {len(history) - 20} more records")
    
    print()


def interactive_mode(agent: PortfolioAgent):
    """Run interactive chat mode."""
    print_banner()
    print("Interactive Mode - Ask questions about your portfolio")
    print("Commands: 'exit' or 'quit' to exit, 'status' for budget, 'history' for usage")
    print("\nExamples:")
    print("  - Show me my portfolio")
    print("  - What's my allocation by platform?")
    print("  - How much do I have in Lulo?")
    print("  - Show my USD positions")
    print()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye.\n")
                break
            
            if user_input.lower() == 'status':
                print_budget_status(agent.tracker)
                continue
            
            if user_input.lower() == 'history':
                print_usage_history(agent.tracker)
                continue
            
            print("\nAssistant: ", end="", flush=True)
            
            response = agent.query(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye.\n")
            break
        except ValueError as e:
            print(f"\nError: {e}\n")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}\n")


def single_query_mode(agent: PortfolioAgent, question: str):
    """Run single query and exit."""
    print_banner()
    
    try:
        print(f"Question: {question}\n")
        print("Assistant: ", end="", flush=True)
        
        response = agent.query(question)
        print(response)
        print()
        
    except ValueError as e:
        print(f"Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}\n")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Colombian Portfolio Aggregator - AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s -q "Show my portfolio"             # Single question
  %(prog)s --status                           # Show budget status
  %(prog)s --history                          # Show usage history
  %(prog)s --history --days 30                # Show 30-day history
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Ask a single question and exit'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show budget status and exit'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='Show usage history and exit'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days for history (default: 7)'
    )
    
    args = parser.parse_args()
    
    try:
        if not config.validate_google_credentials():
            print("Error: Google credentials not configured!")
            print("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file\n")
            sys.exit(1)
        
        if not config.validate_sheet_id():
            print("Error: Sheet ID not configured!")
            print("Please set PORTFOLIO_SHEET_ID in .env file\n")
            sys.exit(1)
        
        if not config.OPENROUTER_API_KEY:
            print("Error: OpenRouter API key not configured!")
            print("Please set OPENROUTER_API_KEY in .env file\n")
            sys.exit(1)
        
        tracker = UsageTracker(
            budget_limit=config.BUDGET_LIMIT,
            daily_limit=config.DAILY_LIMIT
        )
        
        if args.status:
            print_banner()
            print_budget_status(tracker)
            return
        
        if args.history:
            print_banner()
            print_usage_history(tracker, days=args.days)
            return
        
        agent = PortfolioAgent(tracker=tracker)
        
        if args.query:
            single_query_mode(agent, args.query)
        else:
            interactive_mode(agent)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()