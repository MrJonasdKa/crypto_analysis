from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/regression", tags=["regression"])

VALID_SYMBOLS = {"BTC", "ETH", "SOL", "BNB"}


@router.get("/trend/{symbol}")
def get_trend_regression(
    symbol: str,
    use_log: bool = Query(False, description="Return the log-price trend instead of raw price"),
    db: Session = Depends(get_db),
):
    symbol = symbol.upper()
    if symbol not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")

    query = text("""
        SELECT tr.run_date, tr.window_days, tr.use_log_price, tr.slope, tr.intercept, tr.r_squared
        FROM trend_regression tr
        JOIN coins c ON c.id = tr.coin_id
        WHERE c.symbol = :symbol AND tr.use_log_price = :use_log
        ORDER BY tr.run_date DESC
        LIMIT 1
    """)
    row = db.execute(query, {"symbol": symbol, "use_log": use_log}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="No trend regression results yet — run the batch job first")

    return {"symbol": symbol, **dict(row)}


@router.get("/feature/{symbol}")
def get_feature_regression(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.upper()
    if symbol not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")

    query = text("""
        SELECT fr.run_date, fr.horizon_days, fr.model_type, fr.features_used,
               fr.coefficients, fr.intercept, fr.r_squared, fr.predicted_price
        FROM feature_regression fr
        JOIN coins c ON c.id = fr.coin_id
        WHERE c.symbol = :symbol
        ORDER BY fr.run_date DESC
        LIMIT 1
    """)
    row = db.execute(query, {"symbol": symbol}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="No feature regression results yet — run the batch job first")

    return {"symbol": symbol, **dict(row)}
