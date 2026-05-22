"""
tools/file_writer.py
--------------------
Tool 7 — File Writer
Saves a timestamped CSV report at the end of each session. Receives
the full analysis summary from the agent (one row per ticker) and the
list of alert objects from the Alert Tool. Both are written to the same
file so every session is fully auditable in one place.
"""

import csv
import os
from datetime import datetime


FIELDNAMES = [
    "timestamp",
    "ticker",
    "current_price",
    "previous_close",
    "sma_20",
    "pct_change",
    "sma_deviation",
    "sector",
    "sector_etf",
    "sector_return",
    "federal_funds_rate",
    "cpi",
    "treasury_10y",
    "alert_triggered",
    "alert_type",
    "severity",
    "sector_context",
]


def write_report(session_summary: list, output_dir: str = "output") -> str:
    """
    Write the session summary to a timestamped CSV file.

    `session_summary` is a list of row dicts, one per ticker, assembled
    by the agent. Each dict contains the ticker's price data, calculator
    output, macro indicators, and alert result for the session.

    Returns the path of the file written.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"report_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in session_summary:
            writer.writerow(row)

    print(f"[File Writer] Report saved: {filepath}")
    return filepath
