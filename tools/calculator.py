"""
tools/calculator.py
-------------------
Tool 5 — Calculator Tool
Performs all numeric computations for the agent. Receives the current
live price and 30-day historical closing price array from Yahoo Finance
and returns three values: the 20-day SMA, the percentage change from
the previous close, and the deviation of the current price from the SMA.
"""


def calculate_sma(prices: list, period: int = 20) -> float | None:
    """
    Compute the simple moving average over the last `period` closing prices.
    Returns None if there are not enough data points.
    """
    if len(prices) < period:
        return None
    return round(sum(prices[-period:]) / period, 2)


def calculate_pct_change(current_price: float, previous_close: float) -> float | None:
    """
    Compute the percentage change between the current price and the
    previous closing price.
    Returns None if previous_close is zero or missing.
    """
    if not previous_close:
        return None
    return round(((current_price - previous_close) / previous_close) * 100, 2)


def calculate_sma_deviation(current_price: float, sma: float) -> float | None:
    """
    Compute how far the current price deviates from the 20-day SMA,
    expressed as a percentage.
    Returns None if SMA is zero or missing.
    """
    if not sma:
        return None
    return round(((current_price - sma) / sma) * 100, 2)


def run_calculations(ticker_data: dict, historical_prices: list) -> dict:
    """
    Run all three calculations for a single ticker.

    `ticker_data` is the live price dict for one ticker from Yahoo Finance:
    {
      "current_price": 189.50,
      "previous_close": 191.20,
      ...
    }

    `historical_prices` is a list of daily closing prices (oldest first)
    from the Yahoo Finance 30-day history endpoint.

    Returns a `calculations` dict:
    {
      "sma_20": 184.30,
      "pct_change": -0.89,
      "sma_deviation": 2.82
    }
    """
    current_price = ticker_data.get("current_price")
    previous_close = ticker_data.get("previous_close")

    sma = calculate_sma(historical_prices)
    pct_change = calculate_pct_change(current_price, previous_close)
    sma_deviation = calculate_sma_deviation(current_price, sma) if sma else None

    return {
        "sma_20": sma,
        "pct_change": pct_change,
        "sma_deviation": sma_deviation,
    }
