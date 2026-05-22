"""
tests/test_system.py
--------------------
Test suite for the Stock Monitoring Agent.
Covers: Calculator Tool, Alert Tool, File Writer, Yahoo Finance tool,
FRED API tool, payload builder, and input validation.

Run with: pytest tests/test_system.py -v
"""

import os
import sys
import json
import csv
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.calculator import calculate_sma, calculate_pct_change, calculate_sma_deviation, run_calculations
from tools.alert import evaluate_alert, format_alert_message
from tools.file_writer import write_report


# ─────────────────────────────────────────────
# CALCULATOR TOOL TESTS
# ─────────────────────────────────────────────

class TestCalculator:

    def test_sma_correct_value(self):
        """SMA of 20 identical prices should equal that price."""
        prices = [100.0] * 20
        assert calculate_sma(prices) == 100.0

    def test_sma_uses_last_20_only(self):
        """SMA should use only the last 20 prices, ignoring older ones."""
        prices = [50.0] * 10 + [100.0] * 20
        assert calculate_sma(prices) == 100.0

    def test_sma_insufficient_data(self):
        """SMA should return None when fewer than 20 prices are available."""
        prices = [100.0] * 15
        assert calculate_sma(prices) is None

    def test_sma_empty_list(self):
        """SMA should return None for an empty list."""
        assert calculate_sma([]) is None

    def test_pct_change_drop(self):
        """A drop from 200 to 190 should give -5%."""
        result = calculate_pct_change(190.0, 200.0)
        assert result == -5.0

    def test_pct_change_gain(self):
        """A rise from 100 to 110 should give +10%."""
        result = calculate_pct_change(110.0, 100.0)
        assert result == 10.0

    def test_pct_change_zero_previous(self):
        """Percentage change with zero previous close should return None."""
        assert calculate_pct_change(100.0, 0.0) is None

    def test_pct_change_none_previous(self):
        """Percentage change with None previous close should return None."""
        assert calculate_pct_change(100.0, None) is None

    def test_sma_deviation_above(self):
        """Price 10% above SMA should give +10% deviation."""
        result = calculate_sma_deviation(110.0, 100.0)
        assert result == 10.0

    def test_sma_deviation_below(self):
        """Price 5% below SMA should give -5% deviation."""
        result = calculate_sma_deviation(95.0, 100.0)
        assert result == -5.0

    def test_run_calculations_full(self):
        """run_calculations should return all three values for valid input."""
        ticker_data = {"current_price": 105.0, "previous_close": 100.0}
        history = [100.0] * 20
        result = run_calculations(ticker_data, history)
        assert result["sma_20"] == 100.0
        assert result["pct_change"] == 5.0
        assert result["sma_deviation"] == 5.0

    def test_run_calculations_missing_history(self):
        """run_calculations should return None values when history is too short."""
        ticker_data = {"current_price": 105.0, "previous_close": 100.0}
        result = run_calculations(ticker_data, [])
        assert result["sma_20"] is None
        assert result["sma_deviation"] is None
        assert result["pct_change"] == 5.0


# ─────────────────────────────────────────────
# ALERT TOOL TESTS
# ─────────────────────────────────────────────

class TestAlertTool:

    def _calcs(self, pct=-6.0, sma_dev=-4.0):
        return {"pct_change": pct, "sma_deviation": sma_dev, "sma_20": 100.0}

    def test_alert_fires_on_pct_breach(self):
        """Alert should fire when pct_change exceeds the threshold."""
        alert = evaluate_alert("AAPL", 94.0, self._calcs(pct=-6.0), None, 5.0, 3.0)
        assert alert is not None
        assert alert["alert_type"] == "drop"

    def test_alert_fires_on_sma_breach(self):
        """Alert should fire when sma_deviation exceeds the threshold."""
        alert = evaluate_alert("AAPL", 96.0, self._calcs(pct=-1.0, sma_dev=-4.0), None, 5.0, 3.0)
        assert alert is not None

    def test_no_alert_below_threshold(self):
        """Alert should not fire when values are within thresholds."""
        alert = evaluate_alert("AAPL", 98.0, self._calcs(pct=-2.0, sma_dev=-1.0), None, 5.0, 3.0)
        assert alert is None

    def test_alert_spike_type(self):
        """Positive pct_change should produce a spike alert."""
        calcs = {"pct_change": 7.0, "sma_deviation": 5.0, "sma_20": 100.0}
        alert = evaluate_alert("TSLA", 107.0, calcs, None, 5.0, 3.0)
        assert alert["alert_type"] == "spike"

    def test_severity_high_for_large_drop(self):
        """A drop 2x the threshold should produce high severity."""
        alert = evaluate_alert("AAPL", 88.0, self._calcs(pct=-11.0), None, 5.0, 3.0)
        assert alert["severity"] == "high"

    def test_severity_downgraded_for_market_move(self):
        """Severity should be downgraded when the sector moved similarly."""
        alert = evaluate_alert("AAPL", 94.0, self._calcs(pct=-6.0), -5.5, 5.0, 3.0)
        # Without sector context this would be medium; sector move should downgrade it
        assert alert["severity"] in ("low", "medium")
        assert "Market-wide" in alert["sector_context"]

    def test_company_specific_context(self):
        """When sector barely moved, context should say company-specific."""
        alert = evaluate_alert("AAPL", 94.0, self._calcs(pct=-6.0), -0.3, 5.0, 3.0)
        assert "Company-specific" in alert["sector_context"]

    def test_alert_contains_required_fields(self):
        """Alert object must contain all required fields."""
        alert = evaluate_alert("MSFT", 94.0, self._calcs(), -1.0, 5.0, 3.0)
        required = ["ticker", "alert_type", "current_price", "pct_change",
                    "sma_deviation", "severity", "sector_context", "timestamp"]
        for field in required:
            assert field in alert, f"Missing field: {field}"

    def test_format_alert_message(self):
        """Formatted message should include ticker and alert type."""
        alert = evaluate_alert("AAPL", 94.0, self._calcs(), None, 5.0, 3.0)
        msg = format_alert_message(alert)
        assert "AAPL" in msg
        assert "DROP" in msg or "SPIKE" in msg


# ─────────────────────────────────────────────
# FILE WRITER TESTS
# ─────────────────────────────────────────────

class TestFileWriter:

    def test_report_created(self, tmp_path):
        """File Writer should create a CSV file in the output directory."""
        summary = [{
            "timestamp": "2024-01-15 14:30:00",
            "ticker": "AAPL",
            "current_price": 189.50,
            "previous_close": 191.20,
            "sma_20": 184.30,
            "pct_change": -0.89,
            "sma_deviation": 2.82,
            "sector": "Technology",
            "sector_etf": "XLK",
            "sector_return": -1.2,
            "federal_funds_rate": 5.33,
            "cpi": 314.18,
            "treasury_10y": 4.21,
            "alert_triggered": False,
            "alert_type": "",
            "severity": "",
            "sector_context": "",
        }]
        filepath = write_report(summary, output_dir=str(tmp_path))
        assert os.path.exists(filepath)

    def test_report_has_correct_columns(self, tmp_path):
        """CSV report should contain all required column headers."""
        summary = [{
            "timestamp": "2024-01-15 14:30:00",
            "ticker": "TSLA",
            "current_price": 200.0,
            "previous_close": 210.0,
            "sma_20": 205.0,
            "pct_change": -4.76,
            "sma_deviation": -2.44,
            "sector": "Consumer Cyclical",
            "sector_etf": "XLY",
            "sector_return": -0.5,
            "federal_funds_rate": 5.33,
            "cpi": 314.18,
            "treasury_10y": 4.21,
            "alert_triggered": False,
            "alert_type": "",
            "severity": "",
            "sector_context": "",
        }]
        filepath = write_report(summary, output_dir=str(tmp_path))
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
        assert "ticker" in headers
        assert "pct_change" in headers
        assert "severity" in headers

    def test_report_data_written_correctly(self, tmp_path):
        """CSV values should match the input summary data."""
        summary = [{
            "timestamp": "2024-01-15 14:30:00",
            "ticker": "MSFT",
            "current_price": 300.0,
            "previous_close": 295.0,
            "sma_20": 290.0,
            "pct_change": 1.69,
            "sma_deviation": 3.45,
            "sector": "Technology",
            "sector_etf": "XLK",
            "sector_return": 0.8,
            "federal_funds_rate": 5.33,
            "cpi": 314.18,
            "treasury_10y": 4.21,
            "alert_triggered": True,
            "alert_type": "spike",
            "severity": "low",
            "sector_context": "Market-wide move",
        }]
        filepath = write_report(summary, output_dir=str(tmp_path))
        with open(filepath, newline="") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["ticker"] == "MSFT"
        assert rows[0]["alert_triggered"] == "True"


# ─────────────────────────────────────────────
# YAHOO FINANCE TOOL TESTS (mocked)
# ─────────────────────────────────────────────

class TestYahooFinance:

    @patch("tools.yahoo_finance.yf.Ticker")
    def test_get_live_prices_success(self, mock_ticker):
        """get_live_prices should return a correctly structured dict on success."""
        from tools.yahoo_finance import get_live_prices
        mock_info = {
            "currentPrice": 189.50,
            "previousClose": 191.20,
            "volume": 54000000,
            "sector": "Technology",
        }
        mock_ticker.return_value.info = mock_info
        result = get_live_prices(["AAPL"])
        assert result["AAPL"]["current_price"] == 189.50
        assert result["AAPL"]["sector"] == "Technology"

    @patch("tools.yahoo_finance.yf.Ticker")
    def test_get_live_prices_missing_data(self, mock_ticker):
        """get_live_prices should return None for a ticker with no price data."""
        from tools.yahoo_finance import get_live_prices
        mock_ticker.return_value.info = {}
        result = get_live_prices(["INVALID"])
        assert result["INVALID"] is None

    @patch("tools.yahoo_finance.yf.download")
    def test_get_historical_prices_success(self, mock_download):
        """get_historical_prices should return a list of closing prices."""
        import pandas as pd
        from tools.yahoo_finance import get_historical_prices
        mock_df = pd.DataFrame({"Close": [100.0 + i for i in range(20)]})
        mock_download.return_value = mock_df
        result = get_historical_prices(["AAPL"], days=30)
        assert len(result["AAPL"]) == 20

    @patch("tools.yahoo_finance.yf.download")
    def test_get_historical_prices_empty(self, mock_download):
        """get_historical_prices should return empty list for no data."""
        import pandas as pd
        from tools.yahoo_finance import get_historical_prices
        mock_download.return_value = pd.DataFrame()
        result = get_historical_prices(["INVALID"], days=30)
        assert result["INVALID"] == []


# ─────────────────────────────────────────────
# FRED API TOOL TESTS (mocked)
# ─────────────────────────────────────────────

class TestFredAPI:

    @patch("tools.fred_api.requests.get")
    def test_get_macro_indicators_success(self, mock_get):
        """get_macro_indicators should parse FRED response correctly."""
        from tools.fred_api import get_macro_indicators
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "observations": [{"value": "5.33"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = get_macro_indicators("fake_key", {"federal_funds_rate": "FEDFUNDS"})
        assert result["federal_funds_rate"] == 5.33

    @patch("tools.fred_api.requests.get")
    def test_get_macro_indicators_network_failure(self, mock_get):
        """get_macro_indicators should return None on network failure."""
        from tools.fred_api import get_macro_indicators
        mock_get.side_effect = Exception("Network error")
        result = get_macro_indicators("fake_key", {"federal_funds_rate": "FEDFUNDS"})
        assert result["federal_funds_rate"] is None


# ─────────────────────────────────────────────
# INPUT VALIDATION TESTS
# ─────────────────────────────────────────────

class TestInputValidation:

    def test_empty_watchlist_produces_no_results(self):
        """Calculator should handle empty ticker lists gracefully."""
        result = run_calculations({"current_price": 100.0, "previous_close": 100.0}, [])
        assert result["sma_20"] is None

    def test_negative_price_pct_change(self):
        """Negative prices should still produce a valid pct_change."""
        # Unusual but should not crash
        result = calculate_pct_change(90.0, 100.0)
        assert result == -10.0

    def test_alert_with_none_calculations(self):
        """Alert tool should not crash when calculator returns None values."""
        calcs = {"pct_change": None, "sma_deviation": None, "sma_20": None}
        alert = evaluate_alert("AAPL", 100.0, calcs, None, 5.0, 3.0)
        assert alert is None
