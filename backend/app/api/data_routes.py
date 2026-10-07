from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm  import Session
from typing import List

from app.core.database import get_db
from app.models.market_data import StockData
from app.models.anomaly import AnomalyEvent
from app.schemas.market_data import StockDataResponse
from app.schemas.anomaly import AnomalyResponse

router = APIRouter()

@router.get("/market-data/{ticker}", response_model=List[StockDataResponse])
def get_market_data(ticker: str, db: Session= Depends(get_db)):
    records = (
        db.query(StockData).filter(StockData.ticker ==ticker).order_by(StockData.date.asc()).all()

    )
    if not records:
        raise HTTPException(status_code=404, detail="no price data for this ticker")
    return records

@router.get("/anomalies/{ticker}", response_model=List[AnomalyResponse])
def get_anomalies(ticker: str, db: Session = Depends(get_db)):
    anomalies = (
        db.query(AnomalyEvent).filter(AnomalyEvent.ticker == ticker).order_by(AnomalyEvent.date.asc()).all()

    )
    return anomalies
