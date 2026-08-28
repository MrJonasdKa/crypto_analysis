from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/prices", tags=["prices"])

VALID_SYMBOLS = {"BTC", "ETH", "SOL", "BNB"}


@router.get("/{symbol}")
def get_prices(
    symbol: str,
    days: int = Query(90, ge=1, le=1095, description="How many days of history to return"),
    db: Session = Depends(get_db),
):
    symbol = symbol.upper()
    if symbol not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")

    since = date.today() - timedelta(days=days)

    query = text("""
        SELECT dp.price_date, dp.close_price, dp.volume, dp.market_cap
        FROM daily_prices dp
        JOIN coins c ON c.id = dp.coin_id
        WHERE c.symbol = :symbol AND dp.price_date >= :since
        ORDER BY dp.price_date ASC
    """)
    rows = db.execute(query, {"symbol": symbol, "since": since}).mappings().all()

    return {"symbol": symbol, "days": days, "data": [dict(r) for r in rows]}
