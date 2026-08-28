from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/coins", tags=["coins"])


@router.get("")
def list_coins(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, symbol, name FROM coins ORDER BY symbol")).mappings().all()
    return [dict(r) for r in rows]
