"""
trend_regression.py

Simple trend-line regression: close_price (or log(close_price)) vs. time,
over a rolling window. This is a TREND indicator, not a forecast — labeled
that way deliberately. Shows direction/momentum of the last N days.

Run: python trend_regression.py
"""
import os
from datetime import date

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import text

from db_conn import get_engine

WINDOW_DAYS = int(os.environ.get("TREND_WINDOW_DAYS", 90))


def load_prices(engine, coin_id: int, window_days: int) -> pd.DataFrame:
    query = text("""
        SELECT price_date, close_price
        FROM daily_prices
        WHERE coin_id = :coin_id
        ORDER BY price_date DESC
        LIMIT :window_days
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"coin_id": coin_id, "window_days": window_days})
    return df.sort_values("price_date").reset_index(drop=True)


def fit_trend(df: pd.DataFrame, use_log: bool):
    x = np.arange(len(df)).reshape(-1, 1)
    y = np.log(df["close_price"].values) if use_log else df["close_price"].values

    model = LinearRegression()
    model.fit(x, y)
    r_squared = model.score(x, y)

    return float(model.coef_[0]), float(model.intercept_), float(r_squared)


def store_result(engine, coin_id: int, run_date: date, window_days: int,
                  use_log: bool, slope: float, intercept: float, r_squared: float):
    upsert_sql = text("""
        INSERT INTO trend_regression
            (coin_id, run_date, window_days, use_log_price, slope, intercept, r_squared)
        VALUES
            (:coin_id, :run_date, :window_days, :use_log, :slope, :intercept, :r_squared)
        ON DUPLICATE KEY UPDATE
            slope = VALUES(slope),
            intercept = VALUES(intercept),
            r_squared = VALUES(r_squared)
    """)
    with engine.begin() as conn:
        conn.execute(upsert_sql, {
            "coin_id": coin_id, "run_date": run_date, "window_days": window_days,
            "use_log": use_log, "slope": slope, "intercept": intercept, "r_squared": r_squared,
        })


def main():
    engine = get_engine()
    run_date = date.today()

    with engine.connect() as conn:
        coins = conn.execute(text("SELECT id, symbol FROM coins")).mappings().all()

    for coin in coins:
        df = load_prices(engine, coin["id"], WINDOW_DAYS)
        if len(df) < 10:
            print(f"{coin['symbol']}: not enough data yet, skipping")
            continue

        for use_log in (False, True):
            slope, intercept, r_squared = fit_trend(df, use_log)
            store_result(engine, coin["id"], run_date, WINDOW_DAYS, use_log, slope, intercept, r_squared)
            kind = "log-price" if use_log else "price"
            print(f"{coin['symbol']} [{kind}]: slope={slope:.4f} r2={r_squared:.4f}")

    print("Trend regression done.")


if __name__ == "__main__":
    main()
