from datetime import date, timedelta

import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/correlation", tags=["correlation"])


@router.get("")
def get_correlation(
    days: int = Query(90, ge=7, le=1095, description="Window of history to correlate over"),
    db: Session = Depends(get_db),
):
    since = date.today() - timedelta(days=days)

    query = text("""
        SELECT c.symbol, dp.price_date, dp.close_price
        FROM daily_prices dp
        JOIN coins c ON c.id = dp.coin_id
        WHERE dp.price_date >= :since
        ORDER BY dp.price_date ASC
    """)
    rows = db.execute(query, {"since": since}).mappings().all()

    if not rows:
        return {"days": days, "matrix": {}}

    df = pd.DataFrame(rows)
    pivot = df.pivot(index="price_date", columns="symbol", values="close_price")
    corr = pivot.corr(method="pearson")

    return {"days": days, "matrix": corr.round(4).to_dict()}
