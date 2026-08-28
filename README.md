# Crypto Data Analysis — BTC / ETH / SOL / BNB

Trend analysis + short-horizon regression dashboard, built as a portfolio
piece. Deliberately framed as **trend analysis**, not a price predictor —
see "On the regression" below.

## Structure

```
crypto-analysis/
├── data-pipeline/       # Python: fetch data + run regressions (batch job)
│   ├── db/schema.sql
│   ├── fetch_prices.py       # pulls OHLC-ish data from CoinGecko
│   ├── trend_regression.py   # price/log-price vs time
│   ├── feature_regression.py # MA/volatility/volume -> future price
│   ├── run_batch.py          # runs all three in order (cron entry point)
│   └── db_conn.py
├── backend/              # FastAPI: serves cached results as JSON
│   └── app/
│       ├── main.py
│       ├── db.py
│       └── routes/ (coins, prices, regression, correlation)
├── frontend/              # React dashboard — not scaffolded yet, see below
└── docker-compose.yml     # local MariaDB for dev
```

## Setup

1. **Start the DB**
   ```bash
   docker compose up -d
   ```
   This spins up MariaDB and runs `schema.sql` on first boot (creates
   tables + seeds the 4 coins).

2. **Data pipeline**
   ```bash
   cd data-pipeline
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # edit DB_PASSWORD to match docker-compose
   python run_batch.py
   ```
   This fetches ~2 years of daily prices for all 4 coins, then runs both
   regressions and stores results.

3. **Backend API**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   uvicorn app.main:app --reload --port 8000
   ```
   Check `http://localhost:8000/health` and `http://localhost:8000/docs`
   (FastAPI's auto-generated Swagger UI — handy for testing endpoints
   before the frontend exists).

4. **Frontend** — not scaffolded here since you've got the designer tool
   in Claude Code for this part. Quick start:
   ```bash
   npm create vite@latest frontend -- --template react
   ```
   Endpoints it'll consume:
   - `GET /coins`
   - `GET /prices/{symbol}?days=90`
   - `GET /regression/trend/{symbol}?use_log=false`
   - `GET /regression/feature/{symbol}`
   - `GET /correlation?days=90`

5. **Schedule the batch job** (once everything above works manually):
   ```
   0 6 * * * /path/to/data-pipeline/venv/bin/python /path/to/data-pipeline/run_batch.py >> /var/log/crypto-batch.log 2>&1
   ```

## On the regression

Two models, both clearly labeled for what they actually are:

- **Trend regression** (`trend_regression.py`) — price (or log-price) vs.
  time over a rolling 90-day window. Shows momentum/direction. This is
  *not* a forecast.
- **Feature regression** (`feature_regression.py`) — linear regression on
  7-day MA, 30-day MA, 14-day volatility, and volume, targeting price
  7 days out. This is a short-horizon experiment demonstrating feature
  engineering — still not a reliable trading signal (nothing publicly
  available is), but more honest and more interesting than a naive
  time-based line.

Both run daily via `run_batch.py` and get cached in the DB — the API
never computes regression live, it just serves the latest stored run.

## Still to do

- [ ] Frontend dashboard (React): price charts w/ trend line overlay,
      volatility bands, correlation heatmap
- [ ] Deploy target for the DB (currently local docker-compose only)
- [ ] Consider swapping CoinGecko's `/market_chart` for `/ohlc` if you
      want real open/high/low instead of just close price
- [ ] Add basic auth to the API if it's going to sit anywhere public
