"""
watchlist_manager.py
--------------------
Manages the user's personal watchlist. Allows the user to:
- View their current watchlist
- Add stocks manually by ticker symbol
- Browse and add trending/popular stocks
- Browse stocks by sector and see how they are performing
- Remove stocks from the watchlist
- Save changes to the .env file so they persist across sessions
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

from dotenv import load_dotenv, set_key
from config import Config
from trending_stocks import get_trending_with_performance
from sector_viewer import run_sector_viewer

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_watchlist() -> list:
    load_dotenv(ENV_FILE)
    raw = os.environ.get("WATCHLIST", "")
    return [t.strip().upper() for t in raw.split(",") if t.strip()]


def save_watchlist(tickers: list):
    unique = list(dict.fromkeys(tickers))
    set_key(ENV_FILE, "WATCHLIST", ",".join(unique))
    print(f"\n✅ Watchlist saved: {', '.join(unique)}")


def display_watchlist(watchlist: list):
    print("\n📋 Your current watchlist:")
    if not watchlist:
        print("   (empty)")
    else:
        for i, ticker in enumerate(watchlist, 1):
            print(f"   {i}. {ticker}")


def add_stocks_manually(watchlist: list) -> list:
    print("\nEnter stock tickers to add, separated by commas (e.g. AAPL, TSLA, NVDA):")
    raw = input("Add tickers: ").strip()
    if not raw:
        print("No tickers entered.")
        return watchlist
    new_tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
    added = []
    for ticker in new_tickers:
        if ticker not in watchlist:
            watchlist.append(ticker)
            added.append(ticker)
    if added:
        print(f"✅ Added: {', '.join(added)}")
    else:
        print("Those tickers are already in your watchlist.")
    return watchlist


def add_from_trending(watchlist: list) -> list:
    print("\n🔥 Fetching trending stocks... (this may take a moment)\n")
    trending = get_trending_with_performance()
    if not trending:
        print("Could not fetch trending stocks right now.")
        return watchlist

    print(f"{'#':<4} {'Ticker':<8} {'Company':<30} {'Sector':<20} {'Price':>10} {'Change':>8}")
    print("-" * 85)
    for i, stock in enumerate(trending, 1):
        arrow = "▲" if stock["pct_change"] >= 0 else "▼"
        print(f"{i:<4} {stock['ticker']:<8} {stock['company'][:28]:<30} "
              f"{stock['sector'][:18]:<20} "
              f"${stock['price']:>9.2f} "
              f"{arrow}{abs(stock['pct_change']):>6.2f}%")

    print("\nEnter the numbers of the stocks to add (e.g. 1, 3, 5) or 'all':")
    choice = input("Your choice: ").strip().lower()
    if choice == "all":
        selected = [s["ticker"] for s in trending]
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
            selected = [trending[i]["ticker"] for i in indices if 0 <= i < len(trending)]
        except Exception:
            print("Invalid input.")
            return watchlist

    added = []
    for ticker in selected:
        if ticker not in watchlist:
            watchlist.append(ticker)
            added.append(ticker)
    if added:
        print(f"✅ Added: {', '.join(added)}")
    return watchlist


def remove_stocks(watchlist: list) -> list:
    display_watchlist(watchlist)
    print("\nEnter the numbers or ticker names to remove (e.g. 1, 3 or AAPL, TSLA):")
    choice = input("Remove: ").strip()
    if not choice:
        return watchlist
    to_remove = []
    for part in choice.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(watchlist):
                to_remove.append(watchlist[idx])
        elif part.upper() in watchlist:
            to_remove.append(part.upper())
    for ticker in to_remove:
        watchlist.remove(ticker)
    if to_remove:
        print(f"✅ Removed: {', '.join(to_remove)}")
    return watchlist


def run_watchlist_manager():
    print("\n" + "="*60)
    print(" Stock Monitoring Agent — Watchlist Manager")
    print("="*60)

    watchlist = load_watchlist()

    while True:
        display_watchlist(watchlist)
        print("\nWhat would you like to do?")
        print("  1. Add stocks manually (enter ticker symbols)")
        print("  2. Browse and add trending/popular stocks")
        print("  3. Browse stocks by sector")
        print("  4. Remove stocks from watchlist")
        print("  5. Save and exit")
        print("  6. Exit without saving")

        choice = input("\nChoice (1-6): ").strip()

        if choice == "1":
            watchlist = add_stocks_manually(watchlist)
        elif choice == "2":
            watchlist = add_from_trending(watchlist)
        elif choice == "3":
            watchlist = run_sector_viewer(watchlist)
        elif choice == "4":
            watchlist = remove_stocks(watchlist)
        elif choice == "5":
            save_watchlist(watchlist)
            print("Run 'python main.py --once' to monitor your updated watchlist.")
            break
        elif choice == "6":
            print("Exiting without saving.")
            break
        else:
            print("Invalid choice, please enter 1-6.")


if __name__ == "__main__":
    run_watchlist_manager()
