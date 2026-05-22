"""
config.py
---------
Loads environment variables and exposes typed configuration values
to the rest of the system. All sensitive credentials are read from
the .env file so nothing appears in the source code.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    FRED_API_KEY: str = os.environ.get("FRED_API_KEY", "")
    WATCHLIST: list = os.environ.get("WATCHLIST", "AAPL,TSLA,MSFT").split(",")
    ALERT_THRESHOLD: float = float(os.environ.get("ALERT_THRESHOLD", 5.0))
    SMA_DEVIATION_THRESHOLD: float = float(os.environ.get("SMA_DEVIATION_THRESHOLD", 3.0))
    POLL_INTERVAL: int = int(os.environ.get("POLL_INTERVAL", 300))
    OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "output")

    SECTOR_ETF_MAP: dict = {
        "Technology": "XLK",
        "Financials": "XLF",
        "Energy": "XLE",
        "Healthcare": "XLV",
        "Consumer Cyclical": "XLY",
        "Consumer Defensive": "XLP",
        "Industrials": "XLI",
        "Basic Materials": "XLB",
        "Real Estate": "XLRE",
        "Utilities": "XLU",
        "Communication Services": "XLC",
    }

    FRED_INDICATORS: dict = {
        "federal_funds_rate": "FEDFUNDS",
        "cpi": "CPIAUCSL",
        "treasury_10y": "DGS10",
    }
