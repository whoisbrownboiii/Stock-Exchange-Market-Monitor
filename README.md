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

