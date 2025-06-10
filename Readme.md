# Algorithmic Trading Fund Prototype

This repository contains a simple end-to-end algorithmic trading fund prototype. It consists of four main components:

1. **DataPipeline**: Ingests historical market data from Yahoo Finance and stores it in a local SQLite database.
2. **Backtester**: Runs a backtest on the stored data using a mean-reversion strategy and outputs daily P\&L as JSON.
3. **API**: Serves the backtest results via a FastAPI web service.
4. **Dashboard**: A React/TypeScript frontend that fetches the P\&L JSON and displays a performance chart.

---

## Prerequisites

* **Operating System**: macOS (instructions assume macOS, but Linux should work similarly).
* **Python**: 3.10 or higher
* **Node.js & Yarn**: For the React dashboard
* **SQLite3**: (optional) to inspect the database

## Repository Structure

```
TradingFund/
├── Backtester/             # Python backtesting logic
│   ├── strategies/
│   │   └── mean_reversion.py  # Mean-reversion strategy implementation
│   ├── backtest.py           # Backtest runner script
│   └── db.py                 # SQLAlchemy engine pointing at the shared DB
│   └── requirements.txt      # Additional Python deps (if any)
│
├── DataPipeline/           # Python data ingestion logic
│   ├── pipeline.py          # Downloads and stores OHLCV data in SQLite
│   ├── db.py                # SQLAlchemy engine for market_data.db
│   ├── requirements.txt     # DataPipeline-specific Python deps
│   └── .env                 # Environment variables (e.g., DB_PATH)
│
├── API/                    # FastAPI service to expose P&L
│   ├── main.py              # Defines /pnl and health endpoints
│   ├── requirements.txt     # API-specific Python deps
│   └── .env                 # Environment variables (e.g., DB_PATH)
│   └── pnl_<symbol>_<strategy>.json  # Backtest output (created at runtime)
│
└── Dashboard/              # React/TypeScript frontend
    ├── public/             # Static assets
    ├── src/
    │   ├── api/
    │   │   └── client.ts    # Axios client configured for FastAPI
    │   ├── components/
    │   │   └── PnlChart.tsx # Recharts-based performance chart
    │   └── App.tsx          # Main React component
    ├── package.json         # Node/yarn config
    └── tsconfig.json        # TypeScript config

.venv/                      # Python virtual environment (ignored by Git)
.gitignore                  # Git ignore rules
README.md                   # This file
```

---

## Setup

1. **Clone the repository**

   ```bash
   git clone <YOUR_REPO_URL>
   cd TradingFund
   ```

2. **Create a Python virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```

3. **Install shared Python dependencies**

   ```bash
   pip install pandas numpy sqlalchemy backtrader fastapi uvicorn python-dotenv ib_insync openai yfinance
   ```

   All other subfolders (`DataPipeline`, `Backtester`, `API`) have their own `requirements.txt` if you want to keep them isolated.

4. **Install Node.js dependencies**

   ```bash
   cd Dashboard
   yarn install
   cd ..
   ```

---

## 1. DataPipeline: Ingest Historical Data

**Location:** `DataPipeline/pipeline.py`

### Purpose

* Downloads equity OHLCV via the `yfinance` library.
* Downloads crypto OHLCV via `ccxt` (Binance).
* Filters by a start/end date range.
* Strips timezone info and writes the filtered DataFrame to SQLite tables in `market_data.db`.

### How to Run

1. Ensure the `.venv` is active:

   ```bash
   source .venv/bin/activate
   ```
2. (Optional) Inspect or edit `DataPipeline/.env` to set `DB_PATH` (default: `market_data.db`).
3. Run the pipeline script (optionally pass `--start` and `--end` in `YYYY-MM-DD` format):

   ```bash
   cd DataPipeline
   python pipeline.py --start 2020-01-01 --end 2023-01-01
   ```
4. Confirm the database:

   ```bash
   sqlite3 market_data.db
   sqlite> .tables
   AAPL  GOOGL  MSFT  # etc.
   sqlite> SELECT COUNT(*) FROM AAPL;
   ```

> **Note:** If you encounter rate-limit or network errors, the script will wait 10 seconds and retry once per symbol.

---

## 2. Backtester: Run a Mean-Reversion Backtest

**Location:** `Backtester/backtest.py`

### Purpose

* Reads price data from the shared SQLite database (`market_data.db`).
* Filters to a specified date range (e.g., `2022-01-01` to `2023-12-31`).
* Runs the `MeanReversionStrategy` on a single symbol (default: AAPL).
* Records daily portfolio value (`self.value_history`) in the strategy.
* Outputs a JSON array of `{ "date": "YYYY-MM-DD", "value": float }` to a file (e.g., `API/pnl_aapl_mean_reversion.json`).

### Strategy Details

* **20-day lookback** for SMA and standard deviation.
* **Z-score threshold**: 2.0 (go long if price < SMA – 2σ; go short if price > SMA + 2σ).
* **Exit** when z-score crosses 0.
* **Stake**: 100 shares per trade (default).

### How to Run

1. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```
2. Ensure your data is up to date (DataPipeline step). Then run:

   ```bash
    cd Backtester
    python backtest.py \
      --symbol AAPL \
      --start 2022-01-01 \
      --end   2023-12-31 \
      --cash  100000 \
      --output ../API/pnl_aapl_enhanced.json \
      --strategy enhanced
   ```
3. You should see:

   * Starting Portfolio Value (e.g., 100,000.00)
   * Final Portfolio Value (e.g., 99,452.00)
    * `P&L series written to ../API/pnl_aapl_enhanced.json`

### Customization

* **Different symbol**: change `--symbol MSFT` (make sure you ingested MSFT).
* **Other strategy**: pass `--strategy enhanced` to try the RSI-based version or add your own file under `strategies/`.
* **Parameter tuning**: add new `--period`, `--devfactor`, `--stake` arguments and pass into `cerebro.addstrategy(...)`.
* **Multiple symbols**: modify `run_backtest()` to loop through a list of symbols and add multiple data feeds.

---

## 3. API: Serve P\&L via FastAPI

**Location:** `API/main.py`

### Purpose

* A minimal web service that reads the JSON output from the backtester (e.g., `pnl_aapl_mean_reversion.json`) and returns it via HTTP.
* Enables Cross-Origin Resource Sharing (CORS) for the React Dashboard on port 3000.

### Endpoints

* **GET /pnl**: Accepts `symbol` and `strategy` query params and returns the array of `{ date, value }` from `pnl_{symbol}_{strategy}.json`.
* **GET /health**: Returns `{ "status": "ok" }` for a quick health check.

### How to Run

1. Activate your virtual environment:

   ```bash
   source .venv/bin/activate
   ```
2. (Optional) Inspect `API/.env` to set `DB_PATH` (not used directly here) or IB credentials if you add live trading.
3. Start the service:

   ```bash
   cd API
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Verify:

   ```bash
   curl http://localhost:8000/health
   # { "status": "ok" }

   curl "http://localhost:8000/pnl?symbol=AAPL&strategy=mean_reversion"
   # [ { "date":"2022-01-03", "value":100250.00 }, ... ]
   ```

---

## 4. Dashboard: React Frontend

**Location:** `Dashboard/`

### Purpose

* A single-page React/TypeScript app that displays a line chart of daily portfolio value.
* On mount, it calls `GET http://localhost:8000/pnl?symbol=AAPL&strategy=mean_reversion` (using selected values) to fetch the JSON data and passes it to a Recharts component.

### Components

* **`src/api/client.ts`**: Axios instance with `baseURL` set to `http://localhost:8000`.
* **`src/components/PnlChart.tsx`**: Renders a Recharts `LineChart` for the P\&L array.
* **`src/App.tsx`**: Main component that:

1. Uses `useEffect` to fetch `/pnl?symbol=AAPL&strategy=mean_reversion` (or the currently selected options) on page load.
  2. Manages `loading`, `error`, and `pnlData` state.
  3. Renders `<PnlChart data={pnlData} />` if data is present.

### How to Run

1. Install dependencies (once only):

   ```bash
   cd Dashboard
   yarn install
   cd ..
   ```
2. Start the frontend server:

   ```bash
   cd Dashboard
   yarn start
   ```
3. A browser window should open at `http://localhost:3000`. If not, manually navigate there.
4. The app will show:

   * A loading message while fetching.
    * The performance chart once the `/pnl` endpoint returns data.
   * An error message if the API is unavailable or returns an error.
## 5. Live Trading: Interactive Brokers

**Location:** `LiveTrader/trader.py`

This optional component connects to the IB Gateway or Trader Workstation using `ib_insync`.
It streams live prices and places market orders whenever the mean
reversion logic triggers. Start in a paper account to understand the behaviour.

### How to Run

1. Ensure TWS or the IB Gateway is running with API access enabled.
2. Edit `LiveTrader/.env` to specify `IB_HOST`, `IB_PORT` and (optionally) `IB_CLIENT_ID`.
3. Activate your Python environment with `ib_insync` installed.
4. Execute:

```bash
cd LiveTrader
python trader.py AAPL
```

The script prints trade actions to the console as it reacts to live prices.

---

## Summary of the Data Flow

```text
DataPipeline: pipeline.py
  ↓ (writes)        
Backtester: backtest.py ↓ (writes)
                           API: main.py (GET /pnl?symbol=...&strategy=...)
                             ↓ (serves)
                        Dashboard: App.tsx (fetch /pnl?symbol=...&strategy=...)
                             ↓ (displays)
                       PnlChart.tsx (line chart)
```

1. **DataPipeline** downloads and stores historical data in `market_data.db`.
2. **Backtester** reads `market_data.db`, runs a mean-reversion strategy on one symbol (e.g., AAPL), and writes daily portfolio values to `API/pnl_<symbol>_<strategy>.json`.
3. **API** serves that JSON array via `/pnl?symbol=<symbol>&strategy=<strategy>`.
4. **Dashboard** fetches the same endpoint and renders a performance chart in the browser.

---

## Next Steps / Customization Ideas

* **Add more tickers**: Update `DataPipeline/pipeline.py` to include additional symbols, rerun, then backtest them one by one or as a portfolio.
* **Try different strategies**: Create new strategy files (e.g., momentum, breakout) and call them from `backtest.py`.
* **Multi-asset backtest**: Modify `backtest.py` to loop through multiple `symbol`s, add multiple data feeds to `cerebro`, and update the strategy to handle multiple data streams.
* **Metrics & Reporting**: Instead of just P\&L, compute Sharpe ratio, max drawdown, CAGR. Add new API endpoints like `/metrics` and frontend components to display them.
* **Live trading integration**: Use `ib_insync` (Interactive Brokers) to place real or paper orders based on your strategy signals.
* **Containerize**: Write `Dockerfile`s for each component and orchestrate with `docker-compose` to simplify deployment.
* **User authentication**: Protect the API endpoints with JWT and build a multi-page React dashboard with login, user roles, and audit logs.

---

### Congratulations!

You now have a working prototype of an algorithmic trading fund: automated data ingestion, backtesting, a simple REST API, and an interactive web dashboard. Feel free to explore, iterate, and extend each piece to fit your needs.
