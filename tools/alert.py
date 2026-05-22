"""
tools/alert.py
--------------
Tool 6 — Alert Tool
Evaluates whether a stock's computed values breach user-defined thresholds.
Receives the ticker data, calculator output, sector ETF return, and
threshold settings from the agent. Fires only when a threshold is crossed.
Severity is adjusted downward when the sector index moved by a similar amount,
indicating a market-wide move rather than a company-specific event.
"""


def evaluate_alert(
    ticker: str,
    current_price: float,
    calculations: dict,
    sector_return: float | None,
    alert_threshold: float,
    sma_deviation_threshold: float,
) -> dict | None:
    """
    Evaluate whether an alert should be fired for a given ticker.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol.
    current_price : float
        The current live price from Yahoo Finance.
    calculations : dict
        Output from the Calculator Tool containing sma_20, pct_change,
        and sma_deviation.
    sector_return : float | None
        Today's percentage return for the ticker's sector ETF.
        Used to determine whether a move is company-specific or market-wide.
    alert_threshold : float
        The absolute percentage change that triggers an alert (e.g. 5.0).
    sma_deviation_threshold : float
        The SMA deviation percentage that triggers an alert (e.g. 3.0).

    Returns
    -------
    dict | None
        An alert object if a threshold is breached, otherwise None.
        {
          "ticker": "AAPL",
          "alert_type": "drop",
          "current_price": 189.50,
          "pct_change": -6.2,
          "sma_deviation": -4.1,
          "sector_return": -1.2,
          "severity": "high",
          "sector_context": "Company-specific move (sector down -1.2%)",
          "timestamp": "2024-01-15 14:30:00"
        }
    """
    from datetime import datetime

    pct_change = calculations.get("pct_change")
    sma_deviation = calculations.get("sma_deviation")

    # Determine if any threshold is breached
    pct_breach = pct_change is not None and abs(pct_change) >= alert_threshold
    sma_breach = sma_deviation is not None and abs(sma_deviation) >= sma_deviation_threshold

    if not pct_breach and not sma_breach:
        return None

    # Determine alert type
    alert_type = "drop" if (pct_change or 0) < 0 else "spike"

    # Determine severity
    # Base severity on magnitude of breach
    magnitude = abs(pct_change) if pct_change is not None else 0
    if magnitude >= alert_threshold * 2:
        severity = "high"
    elif magnitude >= alert_threshold * 1.2:
        severity = "medium"
    else:
        severity = "low"

    # Downgrade severity if sector moved similarly (market-wide move)
    sector_context = "No sector data available"
    if sector_return is not None:
        if abs(sector_return) >= abs((pct_change or 0)) * 0.5:
            # Sector moved at least half as much — likely market-wide
            if severity == "high":
                severity = "medium"
            elif severity == "medium":
                severity = "low"
            sector_context = f"Market-wide move (sector ETF: {sector_return:+.1f}%)"
        else:
            sector_context = f"Company-specific move (sector ETF: {sector_return:+.1f}%)"

    return {
        "ticker": ticker,
        "alert_type": alert_type,
        "current_price": current_price,
        "pct_change": pct_change,
        "sma_20": calculations.get("sma_20"),
        "sma_deviation": sma_deviation,
        "sector_return": sector_return,
        "severity": severity,
        "sector_context": sector_context,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def format_alert_message(alert: dict) -> str:
    """
    Format an alert object into a human-readable string for console output.
    """
    return (
        f"[ALERT] {alert['ticker']} — {alert['alert_type'].upper()} | "
        f"Price: ${alert['current_price']:.2f} | "
        f"Change: {alert['pct_change']:+.1f}% | "
        f"SMA Deviation: {alert['sma_deviation']:+.1f}% | "
        f"Severity: {alert['severity'].upper()} | "
        f"Context: {alert['sector_context']}"
    )
