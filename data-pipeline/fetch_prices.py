"""
fetch_prices.py

Pulls historical daily price data from CoinGecko for the coins in the
`coins` table and upserts it into `daily_prices`.

CoinGecko's free /market_chart endpoint gives price + market_cap + volume
per day, but not separate OHLC — for a portfolio-scale daily analysis
that's fine; we store close_price = the daily price point and leave
open/high/low null unless you later swap in /ohlc for finer detail.

Run: python fetch_prices.py
"""
import os
import time
from datetime import datetime, timezone

import requests
from sqlalchemy import text

from db_conn import get_engine

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
HISTORY_DAYS = int(os.environ.get("HISTORY_DAYS", 730))


def fetch_market_chart(coingecko_id: str, days: int) -> dict:
    url = f"{COINGECKO_BASE}/coins/{coingecko_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def upsert_prices(engine, coin_id: int, chart: dict):
    prices = chart.get("prices", [])
    volumes = dict((p[0], p[1]) for p in chart.get("total_volumes", []))
    market_caps = dict((p[0], p[1]) for p in chart.get("market_caps", []))

    rows = []
    for ts_ms, price in prices:
        day = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).date()
        rows.append({
            "coin_id": coin_id,
            "price_date": day,
            "close_price": price,
            "volume": volumes.get(ts_ms),
            "market_cap": market_caps.get(ts_ms),
        })

    if not rows:
        return 0

    upsert_sql = text("""
        INSERT INTO daily_prices (coin_id, price_date, close_price, volume, market_cap)
        VALUES (:coin_id, :price_date, :close_price, :volume, :market_cap)
        ON DUPLICATE KEY UPDATE
            close_price = VALUES(close_price),
            volume = VALUES(volume),
            market_cap = VALUES(market_cap)
    """)

    with engine.begin() as conn:
        conn.execute(upsert_sql, rows)

    return len(rows)


def main():
    engine = get_engine()

    with engine.connect() as conn:
        coins = conn.execute(text("SELECT id, symbol, coingecko_id FROM coins")).mappings().all()

    for coin in coins:
        print(f"Fetching {coin['symbol']} ({coin['coingecko_id']})...")
        try:
            chart = fetch_market_chart(coin["coingecko_id"], HISTORY_DAYS)
            n = upsert_prices(engine, coin["id"], chart)
            print(f"  upserted {n} daily rows")
        except requests.HTTPError as e:
            print(f"  FAILED for {coin['symbol']}: {e}")

        # be polite to the free-tier rate limit
        time.sleep(2)

    print("Done.")


if __name__ == "__main__":
    main()
