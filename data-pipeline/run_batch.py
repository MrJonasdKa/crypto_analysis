"""
run_batch.py

Orchestrates the full daily batch: fetch latest prices, then run both
regressions. This is the single entry point for a cron job.

Suggested cron (once a day, e.g. 6am):
    0 6 * * * /path/to/venv/bin/python /path/to/data-pipeline/run_batch.py >> /var/log/crypto-batch.log 2>&1
"""
import sys
import traceback

import fetch_prices
import trend_regression
import feature_regression


def main():
    steps = [
        ("fetch_prices", fetch_prices.main),
        ("trend_regression", trend_regression.main),
        ("feature_regression", feature_regression.main),
    ]

    for name, fn in steps:
        print(f"\n=== Running {name} ===")
        try:
            fn()
        except Exception:
            print(f"!!! {name} failed:")
            traceback.print_exc()
            sys.exit(1)

    print("\nBatch run complete.")


if __name__ == "__main__":
    main()
