"""
agent.py
--------
AI Brain (Gemini)
The agent is the central orchestrator of the system. Each session it:
  1. Collects live prices, historical data, macro indicators, and sector returns
  2. Builds a JSON payload combining all data sources per ticker
  3. Sends the payload to Gemini to interpret context
  4. Runs the Calculator Tool on each ticker
  5. Passes Calculator output to the Alert Tool with user-defined thresholds
  6. Assembles the full session summary and sends it to the File Writer
"""

import json
import time
import sys
import os
from datetime import datetime
from google import genai

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

from config import Config
from yahoo_finance import get_live_prices, get_historical_prices, get_sector_etf_return
from fred_api import get_macro_indicators
from calculator import run_calculations
from alert import evaluate_alert, format_alert_message
from file_writer import write_report

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def ask_gemini(payload: dict) -> str:
    try:
        prompt = (
            "You are a stock market assistant. Analyse this stock data in 2-3 sentences, "
            "focusing on whether the price movement is significant given the macro and sector context. "
            "Do not repeat raw numbers — focus on interpretation only.\n\n"
            f"{json.dumps(payload)}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini] WARNING: API call failed for {payload.get('ticker')}: {e}")
        return "Gemini analysis unavailable for this session."


def build_payload(ticker, live_data, history, macro, sector_return, sector_etf):
    """Merge all data sources into a single JSON payload for one ticker."""
    return {
        "ticker": ticker,
        "current_price": live_data.get("current_price"),
        "previous_close": live_data.get("previous_close"),
        "volume": live_data.get("volume"),
        "sector": live_data.get("sector", "Unknown"),
        "sector_etf": sector_etf,
        "sector_return_pct": sector_return,
        "historical_closes_30d": history,
        "macro": macro,
        "timestamp": live_data.get("timestamp"),
    }


def run_session(single_run: bool = False) -> None:
    """Run a full monitoring session."""
    print(f"\n{'='*60}")
    print(f" Stock Monitoring Agent — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Watchlist: {', '.join(Config.WATCHLIST)}")
    print(f"{'='*60}\n")

    while True:
        session_summary = []
        alerts_fired = []

        print("[Agent] Fetching macro indicators...")
        macro = get_macro_indicators(Config.FRED_API_KEY, Config.FRED_INDICATORS)
        print(f"[Agent] Macro: {macro}\n")

        print("[Agent] Fetching live prices...")
        live_prices = get_live_prices(Config.WATCHLIST)

        print("[Agent] Fetching 30-day historical prices...")
        historical = get_historical_prices(Config.WATCHLIST, days=30)

        for ticker in Config.WATCHLIST:
            print(f"\n--- Processing {ticker} ---")
            live_data = live_prices.get(ticker)
            if not live_data:
                print(f"[Agent] Skipping {ticker} — no live data available.")
                continue

            history = historical.get(ticker, [])
            sector = live_data.get("sector", "Unknown")
            sector_etf = Config.SECTOR_ETF_MAP.get(sector, "SPY")
            sector_return = get_sector_etf_return(sector_etf)

            payload = build_payload(ticker, live_data, history, macro, sector_return, sector_etf)
            gemini_analysis = ask_gemini(payload)
            print(f"[Gemini] {gemini_analysis}")

            calcs = run_calculations(live_data, history)
            if calcs.get("pct_change") is not None and calcs.get("sma_deviation") is not None:
                print(f"[Calculator] SMA(20): {calcs['sma_20']} | "
                      f"Change: {calcs['pct_change']:+.2f}% | "
                      f"SMA Dev: {calcs['sma_deviation']:+.2f}%")

            alert = evaluate_alert(
                ticker=ticker,
                current_price=live_data["current_price"],
                calculations=calcs,
                sector_return=sector_return,
                alert_threshold=Config.ALERT_THRESHOLD,
                sma_deviation_threshold=Config.SMA_DEVIATION_THRESHOLD,
            )

            if alert:
                print(format_alert_message(alert))
                alerts_fired.append(alert)

            session_summary.append({
                "timestamp": live_data.get("timestamp"),
                "ticker": ticker,
                "current_price": live_data.get("current_price"),
                "previous_close": live_data.get("previous_close"),
                "sma_20": calcs.get("sma_20"),
                "pct_change": calcs.get("pct_change"),
                "sma_deviation": calcs.get("sma_deviation"),
                "sector": sector,
                "sector_etf": sector_etf,
                "sector_return": sector_return,
                "federal_funds_rate": macro.get("federal_funds_rate"),
                "cpi": macro.get("cpi"),
                "treasury_10y": macro.get("treasury_10y"),
                "alert_triggered": bool(alert),
                "alert_type": alert["alert_type"] if alert else "",
                "severity": alert["severity"] if alert else "",
                "sector_context": alert["sector_context"] if alert else "",
                "gemini_analysis": gemini_analysis,
            })

        write_report(session_summary, Config.OUTPUT_DIR)
        print(f"\n[Agent] Session complete. Alerts fired: {len(alerts_fired)}")

        if single_run:
            break

        print(f"\n[Agent] Next poll in {Config.POLL_INTERVAL} seconds...\n")
        time.sleep(Config.POLL_INTERVAL)


if __name__ == "__main__":
    run_session(single_run=False)
