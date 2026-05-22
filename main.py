"""
main.py
-------
Entry point for the Stock Monitoring Agent.
Starts with a greeting and interactive menu.
"""

import sys
import os
from stock_chat import run_stock_search_chat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))


def print_menu():
    print("\n" + "="*60)
    print("   📈  STOCK MONITORING AGENT")
    print("="*60)
    print("  What would you like to do?\n")
    print("  1. Monitor my stocks & save a report")
    print("  2. Search & ask AI about any stock")
    print("  3. Browse stocks by sector")
    print("  4. View trending & popular stocks")
    print("  5. Manage my watchlist (add/remove stocks)")
    print("  6. Chat with AI about my portfolio")
    print("  7. Exit")
    print("="*60)


def main():
    from dotenv import load_dotenv, set_key
    load_dotenv()
    watchlist = os.environ.get("WATCHLIST", "").split(",")
    watchlist = [t.strip().upper() for t in watchlist if t.strip()]
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    # Greeting — shown once at startup
    print("\n" + "="*60)
    print("   👋  Welcome to the Stock Monitoring Agent!")
    print("="*60)
    print("  Hello! I am your personal AI-powered stock assistant.")
    print("  I can help you monitor stocks, search the market,")
    print("  browse sectors, view trending stocks, and chat with")
    print("  AI about your portfolio.")
    print("\n  Let's get started!")
    print("="*60)
    input("\n  Press Enter to continue...")

    while True:
        print_menu()
        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            print("\nRun once or continuously?")
            print("  1. Run once and save report")
            print("  2. Run continuously every 5 minutes")
            sub = input("Choice (1-2): ").strip()
            from agent import run_session
            run_session(single_run=(sub == "1"))

        elif choice == "2":
            from stock_chat import run_stock_search_chat
            run_stock_search_chat()

        elif choice == "3":
            from tools.sector_viewer import run_sector_viewer
            updated = run_sector_viewer(watchlist)
            if updated != watchlist:
                watchlist = updated
                set_key(env_file, "WATCHLIST", ",".join(watchlist))
                print(f"✅ Watchlist saved: {', '.join(watchlist)}")

        elif choice == "4":
            from tools.trending_stocks import get_trending_with_performance
            print("\n🔥 Fetching trending stocks... (this may take a moment)\n")
            trending = get_trending_with_performance()
            if trending:
                print(f"{'#':<4} {'Ticker':<8} {'Company':<30} {'Sector':<20} {'Price':>10} {'Change':>8}")
                print("-" * 85)
                for i, stock in enumerate(trending, 1):
                    arrow = "▲" if stock["pct_change"] >= 0 else "▼"
                    print(f"{i:<4} {stock['ticker']:<8} {stock['company'][:28]:<30} "
                          f"{stock['sector'][:18]:<20} "
                          f"${stock['price']:>9.2f} "
                          f"{arrow}{abs(stock['pct_change']):>6.2f}%")
                print("\nWould you like to add any to your watchlist?")
                print("Enter numbers (e.g. 1, 3) or 'all' or press Enter to skip:")
                add_choice = input("Add: ").strip().lower()
                if add_choice == "all":
                    selected = [s["ticker"] for s in trending]
                elif add_choice:
                    try:
                        indices = [int(x.strip()) - 1 for x in add_choice.split(",") if x.strip().isdigit()]
                        selected = [trending[i]["ticker"] for i in indices if 0 <= i < len(trending)]
                    except Exception:
                        selected = []
                else:
                    selected = []
                added = [t for t in selected if t not in watchlist]
                watchlist.extend(added)
                if added:
                    set_key(env_file, "WATCHLIST", ",".join(watchlist))
                    print(f"✅ Added: {', '.join(added)}")
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            from watchlist_manager import run_watchlist_manager
            run_watchlist_manager()

        elif choice == "6":
            from chat import run_chat
            run_chat()

        elif choice == "7":
            print("\nGoodbye! 👋\n")
            break

        else:
            print("\nInvalid choice. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()