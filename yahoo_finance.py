"""
tools/yahoo_finance.py
----------------------
Tool 1 — Yahoo Finance API
"""

import yfinance as yf
from datetime import datetime, timedelta


def get_live_prices(tickers: list) -> dict:
    results = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            volume = info.get("volume") or info.get("regularMarketVolume")
            sector = info.get("sector", "Unknown")

            if current_price is None:
                raise ValueError(f"No price data returned for {ticker}")

            results[ticker] = {
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(previous_close), 2) if previous_close else None,
                "volume": int(volume) if volume else None,
                "sector": sector,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            print(f"[Yahoo Finance] WARNING: Could not fetch data for {ticker}: {e}")
            results[ticker] = None
    return results


def get_historical_prices(tickers: list, days: int = 30) -> dict:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    results = {}

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"),
                             end=end_date.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            if df.empty:
                raise ValueError(f"Empty history for {ticker}")

            # Handle both single and multi-level column DataFrames
            if hasattr(df.columns, 'levels'):
                close_col = [c for c in df.columns if 'Close' in str(c)]
                if close_col:
                    closing_prices = [round(float(p), 2) for p in df[close_col[0]].dropna().values]
                else:
                    raise ValueError("No Close column found")
            else:
                closing_prices = [round(float(p), 2) for p in df["Close"].dropna().values]

            results[ticker] = closing_prices
        except Exception as e:
            print(f"[Yahoo Finance] WARNING: Could not fetch history for {ticker}: {e}")
            results[ticker] = []

    return results


def get_sector_etf_return(sector_etf: str):
    try:
        stock = yf.Ticker(sector_etf)
        info = stock.info
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        previous = info.get("previousClose") or info.get("regularMarketPreviousClose")
        if current and previous:
            return round(((float(current) - float(previous)) / float(previous)) * 100, 2)
    except Exception as e:
        print(f"[Yahoo Finance] WARNING: Could not fetch sector ETF {sector_etf}: {e}")
    return None
