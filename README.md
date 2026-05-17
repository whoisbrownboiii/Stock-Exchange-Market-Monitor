# Stock-Exchange-Market-Monitor (24/04)
An AI and Agent-based Stock Exchange Market Monitor system that allows a user to check what stocks to invest and see how the market is performing currently.

AI AND AGENT-BASED PYTHON SYSTEM

TASK: STOCK EXCHANGE MARKET MONITOR

The planned system to be developed will be a stock exchange monitor that is able to monitor current stock prices on the stock exchange market and be able to provide information on past and current trends to help predict future decisions on what is worth investing in and what is not. The goal is to help anyone that is looking to buy and sell stocks to be able to strategize and make concrete decisions on what they will decide to invest in with the help of the system’s intelligence architecture.
The approach being used is the AI-based approach will be single intelligent agent that follows reasons loop that receives user queries and decided what tools to call to retrieve and calculate stock data and return a natural human-like language response. It which provide a well refined analysis and report on what is currently happening in real time and previously in the stock market. It will be able to use tools that will retrieve the data from the market, calculate the data and respond seamlessly like one is asking for assistance from a help desk.
Tools being used: 
Claude AI, ChatGPT – AI brain decides to which tools to call and interprets results
Yahoo Finance API – Live Stock Prices Source
Calculator Tool – Computation brain that calculates the moving average, changes and thresholds
File Writer – Saves reports
Alert tool – Flags drops and increases in stocks

Programming Concepts:
Functions
APIs and HTTP requests
Loops
File I/O
Classes or dictionaries
Error handling
Environment variables
JSON handling
Conditionals and logic
String formatting
<img width="451" height="706" alt="image" src="https://github.com/user-attachments/assets/f5a48260-a0aa-4e80-96a3-17aa121335a2" />


# Stock-Exchange-Market-Monitor (10/05)

Updated Description

SECOND REPORT:

The system has undergone a few changes during the implementation progress as major changes have been made on to the code and additional features such as adding the ability to add stock that you want to monitor, additional AI assisted features to help you conversate deeply to provide more depth in terms on managing a users’ portfolio. The refined list of programming concepts are:
Functions,
APIs, 
Classes, 
Error handling, 
Environment variables, 
Conditionals and logic.

Updated System Description

The Stock Monitoring Agent was originally designed as a straightforward price monitoring tool that would fetch live stock prices, calculate moving averages, and save alerts to a report. During implementation the system grew significantly beyond that original scope. Three major additions were made. First, an interactive watchlist manager was built so users can add and remove stocks themselves rather than editing a configuration file manually. Second, a sector browser was added that lets users explore ten market sectors, see how every stock in that sector is performing in real time, and add any of them directly to their watchlist. Third, an AI-powered chat mode was introduced using the Gemini API, allowing users to have a conversation about their portfolio, ask which stocks are performing well or poorly, and get contextual analysis that factors in macroeconomic indicators and sector trends. The core monitoring loop, Calculator Tool, Alert Tool, and File Writer remain from the original design, but the system is now interactive rather than purely automated.

Refined Programming Concepts and How They Are Applied
Functions are the primary building block of the entire system. Every tool is wrapped in a named function with a single clear purpose. For example, get_live_prices() fetches Yahoo Finance data for the watchlist, calculate_sma() computes the 20-day moving average, evaluate_alert() checks whether a threshold has been breached, and write_report() saves the session CSV. The agent calls these functions in sequence each session, passing the output of one directly as the input of the next. The chat module uses ask_gemini() and build_system_prompt() as functions that prepare and send data to the AI. The watchlist manager uses load_watchlist(), save_watchlist(), add_stocks_manually(), and add_from_trending() to keep each action separate and reusable.
APIs are used at four points in the system. The Yahoo Finance API, accessed through the yfinance library, provides live prices, previous closing prices, trading volume, and 30 days of historical closing data for every stock on the watchlist. It is also used to fetch sector ETF returns, for example XLK for Technology stocks, which give the system a market-wide benchmark to compare individual stock movements against. The FRED API, accessed using the requests library, fetches three macroeconomic indicators once per session — the federal funds rate, the CPI, and the 10-year Treasury yield. These are included in every report row and passed to the AI so it can factor interest rate and inflation context into its analysis. The Gemini API, accessed through the google-generativeai library, powers both the per-ticker analysis in the monitoring session and the full conversational chat mode. Each API call is isolated in its own function so if one fails the rest of the system continues running.
Classes are used indirectly through the libraries. The Config class in config.py centralises all system settings — the watchlist, alert thresholds, poll interval, API keys, and sector ETF mappings — and makes them available throughout the codebase as typed attributes rather than scattered variables. The genai.GenerativeModel class from the Gemini library is instantiated once and reused across all AI calls. The OpenAI client class was used in the original implementation before the switch to Gemini. Dictionaries are used extensively as lightweight data structures to represent each ticker's state, for example holding the current price, moving average, percentage change, sector return, and alert result together in one object that is passed between tools.
Error handling is applied at every external call in the system using try/except blocks. If Yahoo Finance returns no data for a ticker, that ticker is skipped and the loop continues for the rest of the watchlist. If the FRED API is unreachable, macro values are set to None and the session proceeds without them rather than crashing. If the Gemini API call fails, a fallback message is recorded and execution continues. This approach was important during development because several errors occurred in real testing, including Yahoo Finance returning a differently structured DataFrame in newer library versions and Gemini returning 404 errors for deprecated model names. The error handling meant the system continued producing reports and alerts even while individual tools were being fixed.
Environment variables are used to store all credentials and user configuration outside the codebase. The .env file holds the Gemini API key, the FRED API key, the watchlist, the alert thresholds, the poll interval, and the output directory. These are loaded at startup using the python-dotenv library and accessed through the Config class. The watchlist manager writes back to the .env file using set_key() when the user saves changes, so the updated watchlist is automatically used the next time the system runs. This means no sensitive credentials or personal settings ever appear in the source code.
Conditionals and logic drive the two most important decisions in the system. In the Alert Tool, an if statement checks whether the percentage change exceeds the user's threshold or whether the price has deviated too far from the 20-day moving average. A second condition then checks the sector ETF return — if the sector moved by a similar amount on the same day, the severity is downgraded because the move is likely market-wide rather than company-specific. In the sector viewer, conditionals translate a raw percentage change into a plain-English performance rating: anything above 3% is labelled Strong Buy, between 1% and 3% is Performing Well, between -1% and 1% is Neutral, between -3% and -1% is Underperforming, and below -3% is a Heavy Drop. In the watchlist manager, conditionals handle whether the user chose to add stocks by number, by name, or by selecting all, and whether those stocks are already in the watchlist before adding them.
Tool Integration
The tools are integrated in a layered pipeline where each tool's output feeds directly into the next. At the start of each session the agent calls the FRED API tool once to get macroeconomic context, then calls the Yahoo Finance tool to get live prices and historical data for every ticker. For each ticker it fetches the sector ETF return from Yahoo Finance, merges all three data sources into a single JSON payload, and sends it to Gemini for contextual analysis. The Calculator Tool then receives the live price and historical array and returns the three computed values. Those values go to the Alert Tool alongside the user's thresholds and the sector return, which decides whether to fire an alert and at what severity. Finally the File Writer receives the complete session summary from the agent and all alert objects and saves everything to a timestamped CSV.
The watchlist manager and sector viewer are integrated as standalone interactive modes that run before the monitoring session. They write their output back to the .env file so the agent always reads the most up-to-date watchlist when it runs. The chat mode is integrated as a separate session that loads the same live data the monitoring session would use, builds a system prompt from it, and passes it to Gemini so the AI has full context about the current state of every stock on the watchlist when answering the user's questions.



<img width="451" height="682" alt="image" src="https://github.com/user-attachments/assets/b7d659e6-150f-436d-987f-cdfc36115183" />


# DESCRIPTION OF TESTING PROCESS (17/05)

Testing Process
Testing was carried out alongside implementation rather than at the end. Each tool was tested individually as it was built, and the full pipeline was tested end to end after each major addition. Three methods were used.
The first was a formal automated test suite written in tests/test_system.py using pytest, covering 33 test cases across the Calculator, Alert Tool, File Writer, Yahoo Finance, and FRED API tools. All external API calls are mocked using unittest.mock so tests run without internet or real API keys and produce consistent results every time. Run with pytest tests/test_system.py -v.
The second was live integration testing, where the system was run with real API keys against real market data. Console output and saved CSV reports were inspected after each run to confirm prices were fetched, calculations were correct, and alerts fired at the right thresholds.
The third was deliberate error testing. API keys were removed, invalid tickers were passed, and empty price histories were provided to confirm the system continued running gracefully in every case.

All 33 automated tests in tests/test_system.py passed successfully when run with pytest tests/test_system.py -v. These tests cover the Calculator Tool, Alert Tool, File Writer, Yahoo Finance tool, and FRED API tool, with all external calls mocked so no live internet connection was needed.
During live integration testing the following real errors were encountered and resolved:
Error 1 — Yahoo Finance DataFrame structure When fetching historical prices, the system crashed with the error 'DataFrame' object has no attribute 'tolist'. This was caused by a newer version of yfinance returning a MultiIndex column structure instead of a flat one. The fix was to detect and flatten the column structure before extracting the Close column.
Error 2 — Generative AI package deprecation The google.generativeai package produced a warning during runtime that all support had ended and it would no longer receive updates or bug fixes. The warning stated the package was fully deprecated and that the system must switch to google-genai as soon as possible. This required rewriting the Gemini integration from scratch, replacing import google.generativeai as genai and genai.configure() with the new from google import genai and genai.Client() pattern, and updating every function that called the model.
Error 3 — Generative AI model failures and unavailability Multiple Gemini model names failed with 404 errors during testing. The model gemini-1.5-flash-latest returned a 404 stating it was not found for the API version. The model gemini-2.0-flash returned a 404 stating it was no longer available to new users. The model gemini-2.0-flash-001 returned the same error. Each failure required identifying which models were actually available by running client.models.list() to print all accessible models, and updating the model name in the code accordingly. The final working model was gemini-2.5-pro.
Error 4 — AI chat text extraction issues When the stock search chat was tested with natural language queries such as "What is the stock price of Amazon", the system incorrectly extracted common English words as ticker symbols and attempted to look up stocks called STOCK, PRICE, and OF. This produced 404 errors from Yahoo Finance for each invalid ticker. The fix required adding a company name to ticker dictionary mapping over 50 major companies by their common name to their correct ticker symbol, and adding a large exclusion list of common English words that should never be treated as tickers. This allowed the system to correctly identify Amazon as AMZN from natural language without requiring the user to know the ticker symbol.
Error 5 — FRED API returning blank key The FRED API was returning 400 Bad Request errors because the API key was empty in the URL. This was caused by the .env file either not existing or not being loaded correctly. The fix was to ensure python-dotenv was installed and that the .env file was present in the correct project folder with the actual API key filled in.
Error 6 — Stock search ModuleNotFoundError When option 2 was selected from the main menu, the system threw ModuleNotFoundError: No module named 'stock_chat'. This was because stock_chat.py had not been placed in the correct folder. The fix was to ensure the file was saved in the root project folder alongside main.py and that the sys.path included the correct directory.
Conclusion All core functionality works correctly after resolving the above errors. Live prices are fetched, moving averages and alerts are calculated accurately, reports are saved to CSV, and the AI chat responds with relevant analysis. The generative AI integration required the most troubleshooting due to rapid deprecation of packages and models during the development period, which demonstrated the importance of testing against live APIs regularly rather than assuming they remain stable. All errors were identified through live testing and resolved, improving the robustness and reliability of the final system.

Test Scenarios
Scenario 1 — SMA with sufficient data Twenty identical closing prices of 100.00 are passed to the Calculator. Expected output is an SMA of 100.00, confirming the formula is correct when exactly 20 data points are available.
Scenario 2 — SMA with insufficient data Only 15 closing prices are provided. Expected output is None, confirming the system refuses to calculate a meaningless average.
Scenario 3 — Percentage change on a price drop Current price 190.00, previous close 200.00. Expected output is -5.0%, confirming the formula handles falling prices correctly.
Scenario 4 — Percentage change with zero previous close Previous close set to zero. Expected output is None, confirming no division by zero occurs.
Scenario 5 — Alert fires when threshold is breached Percentage change is -6.0% against a threshold of 5.0%. Expected output is an alert object with type set to drop.
Scenario 6 — No alert below threshold Percentage change is -2.0% and SMA deviation is -1.0%, both within thresholds. Expected output is None.
Scenario 7 — Severity downgraded for market-wide move Percentage change is -6.0% and sector ETF also fell -5.5%. Expected output is a downgraded severity level.
Scenario 8 — Company-specific alert flagged correctly Percentage change is -6.0% but sector ETF only fell -0.3%. Expected output is context reading company-specific move.
Scenario 9 — CSV report created with correct data A session summary with one ticker row is passed to the File Writer. Expected output is a timestamped CSV in the output directory with correct values.
Scenario 10 — Yahoo Finance returns None for invalid ticker Mocked response returns no price data. Expected output is that the ticker is skipped without crashing.
Scenario 11 — FRED API returns None on network failure A network exception is raised. Expected output is that the indicator is set to None and the session continues.
Scenario 12 — Alert tool handles None calculator values All calculator values are None due to insufficient history. Expected output is no alert and no crash.



Deployment Preparation
The system runs locally from the command line with no server or database required. To deploy on any machine three steps are needed.
Install dependencies:
bash
pip install -r requirements.txt
Create the environment file:
bash
cp .env.example .env
Fill in .env with your API keys:
GEMINI_API_KEY=your_key
FRED_API_KEY=your_key
WATCHLIST=AAPL,TSLA,MSFT
ALERT_THRESHOLD=5.0
SMA_DEVIATION_THRESHOLD=3.0
POLL_INTERVAL=300
OUTPUT_DIR=output
Run the system:
bash
python main.py
The program starts with a greeting and an interactive menu. Reports are saved automatically to the output/ folder.
Data Conversion and Transformation
Yahoo Finance returns raw JSON through yfinance. Live price data is extracted and converted to rounded floats stored in Python dictionaries. Historical data arrives as a pandas DataFrame which is flattened, cleaned with dropna(), and converted to a plain Python list of floats for the Calculator.
FRED returns JSON with an observations array. The most recent value is extracted as a string and converted to a float. Invalid entries return None.
Before each Gemini call, live prices, historical data, macro indicators, and sector ETF returns are merged into a single dictionary and serialised to JSON using json.dumps(). Gemini's response returns as plain text and is stored directly in the session summary.
At the end of each session the summary is written to CSV using csv.DictWriter. Each dictionary becomes one row, booleans write as True or False, and None values appear as empty cells. CSV was chosen because it opens directly in Excel with no conversion needed.
<img width="468" height="642" alt="image" src="https://github.com/user-attachments/assets/1c90d294-64cb-4a2b-9b3f-05d266c4bdf4" />


