"""
feature_regression.py

Short-horizon regression using engineered features instead of raw time:
- 7-day and 30-day moving averages
- 14-day rolling volatility (std dev of daily returns)
- volume

Target: close_price `horizon_days` ahead. This is still a simple linear
model — it won't reliably predict crypto prices (nothing does) — but it
demonstrates real feature engineering instead of a naive time trendline,
and it's honest about what it is: a short-horizon experiment, not a
trading signal.

Run: python feature_regression.py
"""
import os
from datetime import date

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import text

from db_conn import get_engine

HORIZON_DAYS = int(os.environ.get("FEATURE_HORIZON_DAYS", 7))
LOOKBACK_DAYS = int(os.environ.get("FEATURE_LOOKBACK_DAYS", 365))

FEATURE_COLS = ["ma_7", "ma_30", "volatility_14", "volume"]


def load_prices(engine, coin_id: int, lookback_days: int) -> pd.DataFrame:
    query = text("""
        SELECT price_date, close_price, volume
        FROM daily_prices
        WHERE coin_id = :coin_id
        ORDER BY price_date DESC
        LIMIT :lookback_days
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"coin_id": coin_id, "lookback_days": lookback_days})
    return df.sort_values("price_date").reset_index(drop=True)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ma_7"] = df["close_price"].rolling(7).mean()
    df["ma_30"] = df["close_price"].rolling(30).mean()
    df["daily_return"] = df["close_price"].pct_change()
    df["volatility_14"] = df["daily_return"].rolling(14).std()
    # target: price `HORIZON_DAYS` ahead
    df["target"] = df["close_price"].shift(-HORIZON_DAYS)
    return df


def fit_model(df: pd.DataFrame):
    data = df.dropna(subset=FEATURE_COLS + ["target"])
    if len(data) < 30:
        return None

    X = data[FEATURE_COLS].values
    y = data["target"].values

    model = LinearRegression()
    model.fit(X, y)
    r_squared = model.score(X, y)

    latest_features = df[FEATURE_COLS].iloc[-1:].values
    predicted_price = float(model.predict(latest_features)[0]) if not np.isnan(latest_features).any() else None

    coefficients = dict(zip(FEATURE_COLS, [float(c) for c in model.coef_]))
    return coefficients, float(model.intercept_), float(r_squared), predicted_price


def store_result(engine, coin_id: int, run_date: date, coefficients: dict,
                  intercept: float, r_squared: float, predicted_price):
    import json
    upsert_sql = text("""
        INSERT INTO feature_regression
            (coin_id, run_date, horizon_days, model_type, features_used, coefficients,
             intercept, r_squared, predicted_price)
        VALUES
            (:coin_id, :run_date, :horizon_days, 'linear', :features_used, :coefficients,
             :intercept, :r_squared, :predicted_price)
        ON DUPLICATE KEY UPDATE
            coefficients = VALUES(coefficients),
            intercept = VALUES(intercept),
            r_squared = VALUES(r_squared),
            predicted_price = VALUES(predicted_price)
    """)
    with engine.begin() as conn:
        conn.execute(upsert_sql, {
            "coin_id": coin_id, "run_date": run_date, "horizon_days": HORIZON_DAYS,
            "features_used": json.dumps(FEATURE_COLS), "coefficients": json.dumps(coefficients),
            "intercept": intercept, "r_squared": r_squared, "predicted_price": predicted_price,
        })


def main():
    engine = get_engine()
    run_date = date.today()

    with engine.connect() as conn:
        coins = conn.execute(text("SELECT id, symbol FROM coins")).mappings().all()

    for coin in coins:
        df = load_prices(engine, coin["id"], LOOKBACK_DAYS)
        if len(df) < 60:
            print(f"{coin['symbol']}: not enough data yet, skipping")
            continue

        df = build_features(df)
        result = fit_model(df)
        if result is None:
            print(f"{coin['symbol']}: not enough clean rows after feature engineering, skipping")
            continue

        coefficients, intercept, r_squared, predicted_price = result
        store_result(engine, coin["id"], run_date, coefficients, intercept, r_squared, predicted_price)
        print(f"{coin['symbol']}: r2={r_squared:.4f} predicted(+{HORIZON_DAYS}d)={predicted_price}")

    print("Feature regression done.")


if __name__ == "__main__":
    main()
