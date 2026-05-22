# Stock Monitoring Agent

A Python system that monitors live stock prices, computes moving averages,
evaluates alerts against user-defined thresholds, and saves timestamped
session reports. Gemini AI provides contextual interpretation of each price
move against macroeconomic indicators and sector ETF returns.

---

## Project Structure

```
stock_agent/
├── main.py                      # Entry point
├── agent.py                     # Gemini AI orchestrator — runs the full session loop
├── config.py                    # Loads environment variables and configuration
├── chat.py                      # Interactive AI chat mode
├── watchlist_manager.py         # Add and manage stocks on your watchlist
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Files excluded from version control
├── tools/
│   ├── yahoo_finance.py         # Tool 1 — live prices and historical data
│   ├── fred_api.py              # Tool 2 — macroeconomic indicators (FRED)
│   ├── calculator.py            # Tool 3 — SMA, pct change, SMA deviation
│   ├── alert.py                 # Tool 4 — threshold evaluation and severity
│   ├── file_writer.py           # Tool 5 — CSV report writer
│   ├── sector_viewer.py         # Tool 6 — browse stocks by sector
│   └── trending_stocks.py      # Tool 7 — popular and trending stocks
├── tests/
│   └── test_system.py           # Full test suite (33 tests)
└── output/                      # Session reports saved here (auto-created)
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the template and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
GEMINI_API_KEY=your_gemini_api_key
FRED_API_KEY=your_fred_api_key
WATCHLIST=AAPL,TSLA,MSFT,GOOGL
ALERT_THRESHOLD=5.0
SMA_DEVIATION_THRESHOLD=3.0
POLL_INTERVAL=300
OUTPUT_DIR=output
```

- **GEMINI_API_KEY** — from https://aistudio.google.com/app/apikey
- **FRED_API_KEY** — free key from https://fred.stlouisfed.org/docs/api/api_key.html
- **WATCHLIST** — comma-separated ticker symbols
- **ALERT_THRESHOLD** — percentage price change that triggers an alert (default 5.0)
- **SMA_DEVIATION_THRESHOLD** — percentage deviation from SMA that triggers an alert (default 3.0)
- **POLL_INTERVAL** — seconds between polling cycles (default 300 = 5 minutes)

---

## Running the System

### Manage your watchlist — add your own stocks or browse trending ones

```bash
python main.py --watchlist
```

### Browse stocks by sector and see how they are performing

```bash
python main.py --sectors
```

### Single monitoring session — runs once and saves a report

```bash
python main.py --once
```

### Continuous monitoring — polls every POLL_INTERVAL seconds

```bash
python main.py
```

### Interactive AI chat — ask Gemini about your portfolio

```bash
python main.py --chat
```

---

## Running the Tests

```bash
pytest tests/test_system.py -v
```

All 33 tests should pass. Tests are fully isolated — no live API calls are
made during testing. Yahoo Finance and FRED calls are mocked using
`unittest.mock`.

---

## How the System Works

Each monitoring session runs in this order:

1. **FRED API** is called once to fetch the federal funds rate, CPI, and
   10-year Treasury yield.

2. **Yahoo Finance** fetches live prices and 30-day closing history for
   every ticker on the watchlist.

3. For each ticker, the **sector ETF return** is fetched from Yahoo Finance
   (e.g. XLK for Technology stocks) to provide market context.

4. A **JSON payload** is assembled combining all three data sources and sent
   to **Gemini AI**, which returns a 2-3 sentence contextual interpretation
   of the price movement.

5. The **Calculator Tool** computes the 20-day SMA, percentage change from
   the previous close, and deviation of the current price from the SMA.

6. The **Alert Tool** evaluates the computed values against the user's
   thresholds. If a threshold is breached, it fires an alert with a severity
   level of low, medium, or high. Severity is downgraded when the sector ETF
   moved similarly, indicating a market-wide move rather than a
   company-specific event.

7. The **File Writer** saves a timestamped CSV report to the output directory
   containing one row per ticker with all price data, calculator output,
   macro indicators, and alert results.

---

## Additional Features

### Watchlist Manager
Add stocks manually by ticker symbol, browse and add from a live trending
stocks list, or remove stocks. Changes are saved to the `.env` file and
used automatically the next time the system runs.

### Sector Viewer
Browse 10 market sectors — Technology, Finance, Healthcare, Energy, Electric
Vehicles, E-Commerce, Entertainment, Real Estate, Consumer Goods, and
Industrials. Each sector shows live prices, percentage change, sector ETF
benchmark return, and a performance rating for every stock. Stocks can be
added directly to your watchlist from the sector view.

### AI Chat Mode
Ask Gemini questions about your portfolio in plain English. The chat mode
loads live stock data at startup and uses it as context for every answer.
Type `refresh` to update the data mid-conversation or `quit` to exit.

Example questions:
- Which stocks are performing well today?
- Which stocks should I be worried about?
- Is AAPL a good buy right now?
- What does the macro environment mean for my portfolio?

---

## Output

Reports are saved to the `output/` directory as:

```
output/report_2024-01-15_14-30-00.csv
```

Each row contains:

| Column             | Description                              |
|--------------------|------------------------------------------|
| timestamp          | Time of the price fetch                  |
| ticker             | Stock symbol                             |
| current_price      | Live price                               |
| previous_close     | Previous session closing price           |
| sma_20             | 20-day simple moving average             |
| pct_change         | % change from previous close             |
| sma_deviation      | % deviation from SMA                     |
| sector             | Company sector (e.g. Technology)         |
| sector_etf         | Corresponding sector ETF (e.g. XLK)     |
| sector_return      | Sector ETF % return today                |
| federal_funds_rate | FRED: current federal funds rate         |
| cpi                | FRED: latest CPI reading                 |
| treasury_10y       | FRED: 10-year Treasury yield             |
| alert_triggered    | True/False                               |
| alert_type         | drop or spike                            |
| severity           | low / medium / high                      |
| sector_context     | Company-specific or market-wide          |

---

## Error Handling

- If Yahoo Finance returns no data for a ticker, that ticker is skipped and
  the session continues for the remaining tickers.
- If the FRED API is unreachable, macro values are set to None and the
  session continues without them.
- If the Gemini API call fails, a fallback message is recorded in the summary
  and execution continues.
- All external calls are wrapped in try/except blocks so a single failure
  never stops the monitoring loop.

---

## Dependencies

- `yfinance` — Yahoo Finance stock data
- `google-generativeai` — Gemini AI analysis
- `requests` — FRED API HTTP calls
- `python-dotenv` — environment variable loading
- `pytest` — test suite
