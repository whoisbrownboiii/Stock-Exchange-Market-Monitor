"""
tools/fred_api.py
-----------------
Tool 6 — FRED Macroeconomic Data API
Fetches the most recently published values for three macroeconomic
indicators: federal funds rate, CPI, and 10-year Treasury yield.
Called once per session before the main analysis loop begins.
"""

import requests


FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def get_macro_indicators(api_key: str, indicators: dict) -> dict:
    """
    Fetch the latest value for each FRED indicator code.

    `indicators` is a dict of {friendly_name: fred_series_id}, e.g.:
    {
      "federal_funds_rate": "FEDFUNDS",
      "cpi": "CPIAUCSL",
      "treasury_10y": "DGS10"
    }

    Returns:
    {
      "federal_funds_rate": 5.33,
      "cpi": 314.18,
      "treasury_10y": 4.21
    }

    If a request fails, the indicator is set to None and execution continues.
    """
    results = {}

    for name, series_id in indicators.items():
        try:
            params = {
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            }
            response = requests.get(FRED_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            observations = data.get("observations", [])
            if observations:
                value = observations[0].get("value", ".")
                results[name] = float(value) if value != "." else None
            else:
                results[name] = None
        except Exception as e:
            print(f"[FRED] WARNING: Could not fetch {name} ({series_id}): {e}")
            results[name] = None

    return results
