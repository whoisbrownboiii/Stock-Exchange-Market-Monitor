"""
stock_chat.py
-------------
AI-powered stock search chat.
The user can ask about any stock on the market in plain English.
Automatically fetches live prices and stats before sending to AI.
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

from google import genai
from config import Config
import yfinance as yf

client = genai.Client(api_key=Config.GEMINI_API_KEY)

# Known company name to ticker mappings so users can type company names
COMPANY_TO_TICKER = {
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", "alphabet": "GOOGL",
    "amazon": "AMZN", "tesla": "TSLA", "nvidia": "NVDA", "meta": "META",
    "facebook": "META", "netflix": "NFLX", "disney": "DIS", "uber": "UBER",
    "airbnb": "ABNB", "spotify": "SPOT", "twitter": "X", "snap": "SNAP",
    "paypal": "PYPL", "shopify": "SHOP", "salesforce": "CRM", "oracle": "ORCL",
    "intel": "INTC", "amd": "AMD", "qualcomm": "QCOM", "samsung": "SSNLF",
    "sony": "SONY", "toyota": "TM", "volkswagen": "VWAGY", "bmw": "BMWYY",
    "jpmorgan": "JPM", "goldman": "GS", "morgan stanley": "MS", "visa": "V",
    "mastercard": "MA", "berkshire": "BRK-B", "johnson": "JNJ", "pfizer": "PFE",
    "moderna": "MRNA", "exxon": "XOM", "chevron": "CVX", "boeing": "BA",
    "ford": "F", "gm": "GM", "general motors": "GM", "rivian": "RIVN",
    "lucid": "LCID", "nio": "NIO", "coinbase": "COIN", "robinhood": "HOOD",
}

# Words that look like tickers but are not
EXCLUDE_WORDS = {
    "I", "A", "AN", "THE", "IS", "IT", "IN", "ON", "AT", "BE", "DO", "GO",
    "ME", "MY", "OR", "IF", "UP", "SO", "NO", "AI", "AND", "FOR", "ARE",
    "NOT", "HOW", "WHY", "WHO", "CAN", "DID", "HAS", "HAD", "ITS", "NOW",
    "BUY", "SELL", "GOOD", "BAD", "GET", "SET", "NEW", "OLD", "BIG", "TOP",
    "STOCK", "PRICE", "MARKET", "TODAY", "WHAT", "TELL", "SHOW", "GIVE",
    "ABOUT", "SHARE", "FUND", "RATE", "HIGH", "LOW", "DOWN", "RISE", "FALL",
    "BEST", "MOST", "MUCH", "MANY", "MORE", "SOME", "THAN", "THIS", "THAT",
    "WITH", "FROM", "WILL", "BEEN", "HAVE", "THEY", "THEM", "THEIR", "JUST",
}


def extract_tickers(message: str) -> list:
    """
    Intelligently extract ticker symbols or company names from user message.
    Handles both ticker symbols (AAPL) and company names (Apple, Amazon).
    """
    found = []

    # First check for known company names
    lower = message.lower()
    for company, ticker in COMPANY_TO_TICKER.items():
        if company in lower and ticker not in found:
            found.append(ticker)

    # Then look for explicit ticker symbols (ALL CAPS, 1-5 letters)
    words = message.split()
    for word in words:
        clean = word.strip(".,?!()$#@")
        if (re.match(r'^[A-Z]{1,5}$', clean) and
                clean not in EXCLUDE_WORDS and
                clean not in found):
            found.append(clean)

    return found[:3]  # max 3 tickers per query


def fetch_stock_data(ticker: str) -> dict | None:
    """Fetch live price and stats for any ticker symbol."""
    try:
        info = yf.Ticker(ticker.upper()).info
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        previous = info.get("previousClose") or info.get("regularMarketPreviousClose")
        if not current:
            return None
        pct_change = round(((float(current) - float(previous)) / float(previous)) * 100, 2) if previous else None
        return {
            "ticker": info.get("symbol", ticker.upper()),
            "company": info.get("longName") or info.get("shortName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "current_price": round(float(current), 2),
            "previous_close": round(float(previous), 2) if previous else None,
            "pct_change": pct_change,
            "open": info.get("open") or info.get("regularMarketOpen"),
            "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
            "week_52_high": info.get("fiftyTwoWeekHigh"),
            "week_52_low": info.get("fiftyTwoWeekLow"),
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
        }
    except Exception:
        return None


def format_market_cap(value) -> str:
    if not value:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def display_stock_prices(stock_data: dict):
    """Print a live price card for each stock found."""
    for ticker, s in stock_data.items():
        arrow = "▲" if (s["pct_change"] or 0) >= 0 else "▼"
        pct = f"{arrow}{abs(s['pct_change']):.2f}%" if s["pct_change"] is not None else "N/A"
        print(f"\n  {'─'*50}")
        print(f"  📊 {s['ticker']} — {s['company']}")
        print(f"  {'─'*50}")
        print(f"  💰 Current Price:  ${s['current_price']:.2f}")
        if s['previous_close']: print(f"  📉 Previous Close: ${s['previous_close']:.2f}")
        print(f"  📈 Today's Change: {pct}")
        if s.get("open"):         print(f"  🔓 Open:           ${s['open']:.2f}")
        if s.get("day_high"):     print(f"  ⬆️  Day High:        ${s['day_high']:.2f}")
        if s.get("day_low"):      print(f"  ⬇️  Day Low:         ${s['day_low']:.2f}")
        if s.get("week_52_high"): print(f"  📅 52-Week High:   ${s['week_52_high']:.2f}")
        if s.get("week_52_low"):  print(f"  📅 52-Week Low:    ${s['week_52_low']:.2f}")
        print(f"  🏢 Market Cap:     {format_market_cap(s['market_cap'])}")
        if s.get("volume"):       print(f"  📦 Volume:         {s['volume']:,}")
        if s.get("pe_ratio"):     print(f"  📐 P/E Ratio:      {s['pe_ratio']:.2f}")
        print(f"  {'─'*50}")


def run_stock_search_chat():
    """Chat interface for searching and asking about any stock."""
    print("\n" + "="*60)
    print("  🔍 AI Stock Search — Ask About Any Stock")
    print("="*60)
    print("  Ask about any stock by name or ticker symbol.")
    print("  Type 'back' to return to the main menu.\n")
    print("  Examples:")
    print("  - What is the stock price of Amazon?")
    print("  - How is Apple performing today?")
    print("  - Tell me about NVIDIA")
    print("  - Is Tesla a good buy right now?")
    print("  - Compare Google and Microsoft\n")

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nReturning to menu.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("back", "exit", "quit"):
            print("Returning to main menu.")
            break

        # Extract tickers and fetch live data
        tickers = extract_tickers(user_input)
        stock_data = {}
        if tickers:
            print(f"\n⏳ Fetching live data for: {', '.join(tickers)}...")
            for ticker in tickers:
                data = fetch_stock_data(ticker)
                if data:
                    stock_data[ticker] = data

        # Show price card
        if stock_data:
            display_stock_prices(stock_data)
            data_context = f"\n\nLive market data already shown to user:\n{json.dumps(stock_data, indent=2)}"
        else:
            data_context = "\n\nNo stock data found — answer from general knowledge."

        # Build conversation history context
        history_text = "\n".join([
            f"{h['role']}: {h['parts'][0]}"
            for h in conversation_history[-6:]
        ])

        prompt = (
            "You are a knowledgeable stock market assistant. "
            "Live price data has already been displayed to the user — do not repeat the numbers. "
            "Focus on interpretation, context, trends, and insight. "
            "Keep answers clear and concise. "
            "Always note this is not financial advice."
            + data_context
            + (f"\n\nPrevious conversation:\n{history_text}" if history_text else "")
            + f"\n\nUser: {user_input}"
        )

        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt
            )
            reply = response.text.strip()
        except Exception as e:
            reply = f"Sorry, I could not get a response right now: {e}"

        conversation_history.append({"role": "user", "parts": [user_input]})
        conversation_history.append({"role": "model", "parts": [reply]})
        print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    run_stock_search_chat()