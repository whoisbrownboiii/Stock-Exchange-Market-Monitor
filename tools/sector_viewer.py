"""
tools/sector_viewer.py
----------------------
Allows the user to browse stocks by sector and see how they are
performing. Shows price, percentage change, and a simple performance
rating for each stock in the selected sector.
"""

import yfinance as yf


SECTORS = {
    "1": {
        "name": "Technology",
        "etf": "XLK",
        "tickers": ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMD", "INTC", "CRM", "ORCL"]
    },
    "2": {
        "name": "Finance",
        "etf": "XLF",
        "tickers": ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "AXP"]
    },
    "3": {
        "name": "Healthcare",
        "etf": "XLV",
        "tickers": ["JNJ", "PFE", "UNH", "MRK", "ABBV", "LLY", "TMO", "ABT"]
    },
    "4": {
        "name": "Energy",
        "etf": "XLE",
        "tickers": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX"]
    },
    "5": {
        "name": "Electric Vehicles",
        "etf": "XLY",
        "tickers": ["TSLA", "RIVN", "LCID", "NIO", "XPEV", "F", "GM"]
    },
    "6": {
        "name": "E-Commerce & Retail",
        "etf": "XLY",
        "tickers": ["AMZN", "SHOP", "BABA", "EBAY", "ETSY", "WMT", "TGT"]
    },
    "7": {
        "name": "Entertainment & Media",
        "etf": "XLC",
        "tickers": ["NFLX", "DIS", "PARA", "WBD", "SPOT", "ROKU"]
    },
    "8": {
        "name": "Real Estate",
        "etf": "XLRE",
        "tickers": ["AMT", "PLD", "CCI", "EQIX", "SPG", "O"]
    },
    "9": {
        "name": "Consumer Goods",
        "etf": "XLP",
        "tickers": ["PG", "KO", "PEP", "COST", "MCD", "SBUX", "NKE"]
    },
    "10": {
        "name": "Industrials",
        "etf": "XLI",
        "tickers": ["BA", "CAT", "GE", "HON", "LMT", "RTX", "UPS"]
    },
}


def get_performance_rating(pct_change: float) -> str:
    """Convert a percentage change into a simple performance label."""
    if pct_change >= 3:
        return "🚀 Strong Buy"
    elif pct_change >= 1:
        return "📈 Performing Well"
    elif pct_change >= -1:
        return "➡️  Neutral"
    elif pct_change >= -3:
        return "📉 Underperforming"
    else:
        return "🔴 Heavy Drop"


def fetch_sector_etf_return(etf: str) -> float | None:
    """Fetch today's return for the sector ETF benchmark."""
    try:
        info = yf.Ticker(etf).info
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        previous = info.get("previousClose") or info.get("regularMarketPreviousClose")
        if current and previous:
            return round(((float(current) - float(previous)) / float(previous)) * 100, 2)
    except Exception:
        pass
    return None


def fetch_sector_stocks(tickers: list) -> list:
    """
    Fetch live performance data for a list of tickers.
    Returns a list of dicts sorted by percentage change (best performers first).
    """
    results = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            current = info.get("currentPrice") or info.get("regularMarketPrice")
            previous = info.get("previousClose") or info.get("regularMarketPreviousClose")
            market_cap = info.get("marketCap")
            volume = info.get("volume")
            company = info.get("shortName", ticker)

            if current and previous:
                pct_change = round(((float(current) - float(previous)) / float(previous)) * 100, 2)
                results.append({
                    "ticker": ticker,
                    "company": company,
                    "price": round(float(current), 2),
                    "previous_close": round(float(previous), 2),
                    "pct_change": pct_change,
                    "market_cap": market_cap,
                    "volume": volume,
                    "rating": get_performance_rating(pct_change),
                })
        except Exception as e:
            print(f"  [Warning] Could not fetch {ticker}: {e}")

    results.sort(key=lambda x: x["pct_change"], reverse=True)
    return results


def display_sector_menu():
    """Display the sector selection menu."""
    print("\n📊 Available Sectors:")
    print("-" * 40)
    for key, sector in SECTORS.items():
        print(f"  {key:>2}. {sector['name']}")
    print("-" * 40)


def display_sector_performance(sector_key: str) -> list:
    """
    Fetch and display full performance data for a selected sector.
    Returns the list of stocks so the user can add them to their watchlist.
    """
    sector = SECTORS.get(sector_key)
    if not sector:
        print("Invalid sector selection.")
        return []

    print(f"\n⏳ Fetching {sector['name']} sector data...\n")

    # Fetch sector ETF benchmark
    etf_return = fetch_sector_etf_return(sector["etf"])
    etf_label = f"{etf_return:+.2f}%" if etf_return is not None else "N/A"

    print(f"{'='*75}")
    print(f"  📂 Sector: {sector['name']}")
    print(f"  📊 Sector ETF ({sector['etf']}) today: {etf_label}")
    print(f"{'='*75}")
    print(f"{'#':<4} {'Ticker':<7} {'Company':<28} {'Price':>10} {'Change':>8}  {'Rating'}")
    print(f"{'-'*75}")

    stocks = fetch_sector_stocks(sector["tickers"])

    for i, stock in enumerate(stocks, 1):
        arrow = "▲" if stock["pct_change"] >= 0 else "▼"
        print(f"{i:<4} {stock['ticker']:<7} {stock['company'][:26]:<28} "
              f"${stock['price']:>9.2f} "
              f"{arrow}{abs(stock['pct_change']):>6.2f}%  "
              f"{stock['rating']}")

    print(f"{'='*75}")

    # Summary
    gainers = [s for s in stocks if s["pct_change"] > 0]
    losers = [s for s in stocks if s["pct_change"] < 0]
    print(f"\n  ✅ Gainers: {len(gainers)}   ❌ Losers: {len(losers)}")

    if stocks:
        best = stocks[0]
        worst = stocks[-1]
        print(f"  🏆 Best performer:  {best['ticker']} ({best['pct_change']:+.2f}%)")
        print(f"  📉 Worst performer: {worst['ticker']} ({worst['pct_change']:+.2f}%)")

    return stocks


def run_sector_viewer(watchlist: list = None) -> list:
    """
    Main sector viewer loop. Lets the user browse sectors and optionally
    add stocks to their watchlist. Returns the updated watchlist.
    """
    if watchlist is None:
        watchlist = []

    while True:
        display_sector_menu()
        print("  0. Back to main menu")
        choice = input("\nSelect a sector (0-10): ").strip()

        if choice == "0":
            break

        if choice not in SECTORS:
            print("Invalid choice, please enter a number between 0 and 10.")
            continue

        stocks = display_sector_performance(choice)

        if stocks and watchlist is not None:
            print("\nWould you like to add any of these stocks to your watchlist?")
            print("Enter numbers (e.g. 1, 3) or 'all' for all, or press Enter to skip:")
            add_choice = input("Add to watchlist: ").strip().lower()

            if add_choice == "all":
                selected = [s["ticker"] for s in stocks]
            elif add_choice:
                try:
                    indices = [int(x.strip()) - 1 for x in add_choice.split(",") if x.strip().isdigit()]
                    selected = [stocks[i]["ticker"] for i in indices if 0 <= i < len(stocks)]
                except Exception:
                    selected = []
            else:
                selected = []

            added = []
            for ticker in selected:
                if ticker not in watchlist:
                    watchlist.append(ticker)
                    added.append(ticker)
            if added:
                print(f"✅ Added to watchlist: {', '.join(added)}")

        print("\nView another sector? (press Enter to continue or '0' to go back)")
        again = input().strip()
        if again == "0":
            break

    return watchlist
