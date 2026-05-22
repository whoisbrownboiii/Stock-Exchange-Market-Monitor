"""
tools/trending_stocks.py
------------------------
Fetches the most popular and trending stocks on the market.
Uses yfinance to pull data for well-known indices and trending tickers
so the user does not have to manually find popular stocks.
"""

import yfinance as yf


# Most actively traded and watched stocks across major sectors
TOP_STOCKS = {
    "Technology":     ["AAPL", "MSFT", "NVDA", "GOOGL", "META"],
    "Electric Vehicles": ["TSLA", "RIVN", "LCID"],
    "Finance":        ["JPM", "BAC", "GS"],
    "E-Commerce":     ["AMZN", "SHOP"],
    "Healthcare":     ["JNJ", "PFE", "UNH"],
    "Energy":         ["XOM", "CVX"],
    "Entertainment":  ["NFLX", "DIS"],
}


def get_trending_tickers() -> list:
    """
    Return a flat list of the most popular and trending stock tickers
    across major market sectors.
    """
    tickers = []
    for sector_tickers in TOP_STOCKS.values():
        tickers.extend(sector_tickers)
    return tickers


def get_trending_with_performance() -> list:
    """
    Fetch live performance data for all trending stocks and return them
    sorted by percentage change so the user can see which are moving most.

    Returns a list of dicts:
    [
      {"ticker": "NVDA", "sector": "Technology", "price": 875.40, "pct_change": 3.2},
      ...
    ]
    """
    results = []
    all_tickers = get_trending_tickers()

    for ticker in all_tickers:
        try:
            info = yf.Ticker(ticker).info
            current = info.get("currentPrice") or info.get("regularMarketPrice")
            previous = info.get("previousClose") or info.get("regularMarketPreviousClose")
            if current and previous:
                pct_change = round(((float(current) - float(previous)) / float(previous)) * 100, 2)
                results.append({
                    "ticker": ticker,
                    "sector": info.get("sector", "Unknown"),
                    "price": round(float(current), 2),
                    "pct_change": pct_change,
                    "company": info.get("shortName", ticker),
                })
        except Exception as e:
            print(f"[Trending] WARNING: Could not fetch {ticker}: {e}")

    # Sort by absolute percentage change — biggest movers first
    results.sort(key=lambda x: abs(x.get("pct_change", 0)), reverse=True)
    return results
