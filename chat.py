"""
chat.py
-------
Interactive AI chat mode.
Loads live stock data and allows the user to ask Gemini questions
about their portfolio in plain English.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

from google import genai

client = genai.Client(api_key=Config.GEMINI_API_KEY)
from config import Config
from yahoo_finance import get_live_prices, get_historical_prices, get_sector_etf_return
from fred_api import get_macro_indicators
from calculator import run_calculations
from alert import evaluate_alert

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def fetch_live_context() -> list:
    """Fetch fresh live data for all watchlist stocks."""
    print("[Chat] Fetching latest stock data...")
    macro = get_macro_indicators(Config.FRED_API_KEY, Config.FRED_INDICATORS)
    live_prices = get_live_prices(Config.WATCHLIST)
    historical = get_historical_prices(Config.WATCHLIST, days=30)

    summaries = []
    for ticker in Config.WATCHLIST:
        live_data = live_prices.get(ticker)
        if not live_data:
            continue
        history = historical.get(ticker, [])
        sector = live_data.get("sector", "Unknown")
        sector_etf = Config.SECTOR_ETF_MAP.get(sector, "SPY")
        sector_return = get_sector_etf_return(sector_etf)
        calcs = run_calculations(live_data, history)
        alert = evaluate_alert(
            ticker=ticker,
            current_price=live_data["current_price"],
            calculations=calcs,
            sector_return=sector_return,
            alert_threshold=Config.ALERT_THRESHOLD,
            sma_deviation_threshold=Config.SMA_DEVIATION_THRESHOLD,
        )
        summaries.append({
            "ticker": ticker,
            "current_price": live_data.get("current_price"),
            "previous_close": live_data.get("previous_close"),
            "sector": sector,
            "sector_return": sector_return,
            "sma_20": calcs.get("sma_20"),
            "pct_change": calcs.get("pct_change"),
            "sma_deviation": calcs.get("sma_deviation"),
            "alert_triggered": bool(alert),
            "alert_type": alert["alert_type"] if alert else None,
            "severity": alert["severity"] if alert else None,
            "macro": macro,
        })
    return summaries


def build_system_prompt(stock_context: list) -> str:
    return (
        "You are a stock market assistant helping a user understand their watchlist. "
        "You have access to the following real-time stock data:\n\n"
        f"{json.dumps(stock_context, indent=2)}\n\n"
        "Use this data to answer the user's questions. When asked which stocks are good "
        "or bad, base your answer on pct_change, sma_deviation, alert status, sector_return, "
        "and macro indicators. Always note that this is not financial advice."
    )


def run_chat():
    print("\n" + "="*60)
    print(" Stock Monitoring Agent — AI Chat")
    print(" Type 'quit' to exit | Type 'refresh' to update stock data")
    print("="*60 + "\n")

    stock_context = fetch_live_context()
    if not stock_context:
        print("[Chat] No stock data available. Check your watchlist configuration.")
        return

    print(f"[Chat] Loaded data for: {', '.join([s['ticker'] for s in stock_context])}")
    print("\nExample questions:")
    print("  - Which stocks are performing well today?")
    print("  - Which stocks should I be worried about?")
    print("  - Is AAPL a good buy right now?")
    print("  - What does the macro environment mean for my portfolio?\n")

    system_prompt = build_system_prompt(stock_context)
    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Chat] Goodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("[Chat] Goodbye.")
            break
        if user_input.lower() == "refresh":
            print("[Chat] Refreshing stock data...")
            stock_context = fetch_live_context()
            system_prompt = build_system_prompt(stock_context)
            conversation_history = []
            print(f"[Chat] Refreshed: {', '.join([s['ticker'] for s in stock_context])}\n")
            continue

        try:
            chat = model.start_chat(history=conversation_history)
            response = chat.send_message(f"{system_prompt}\n\nUser question: {user_input}")
            reply = response.text.strip()
        except Exception as e:
            reply = f"Sorry, I could not get a response: {e}"

        conversation_history.append({"role": "user", "parts": [user_input]})
        conversation_history.append({"role": "model", "parts": [reply]})
        print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    run_chat()
