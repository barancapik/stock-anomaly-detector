from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import yfinance as yf
import pandas as pd
from datetime import datetime

from app.core.database import get_db
from app.models.market_data import StockData
from app.schemas.market_data import StockDataCreate

router = APIRouter()

TARGET_TICKERS = ["THYAO.IS", "GARAN.IS"]

@router.post("/ingest")
def ingest_data(db: Session = Depends(get_db)):
    records_added = 0
    for ticker in TARGET_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period = "2y")

            if df.empty:
                continue

            df = df.reset_index()

            for _, row in df.iterrows():

                record_date = row['Date'].date()

                existing = db.query(StockData).filter(
                    StockData.ticker == ticker,
                    StockData.date == record_date
                ).first()

                if not existing:
                    valid_data = StockDataCreate(
                        ticker=ticker,
                        date = record_date,
                        open_price=float(row["Open"]),
                        high_price=float(row["High"]),
                        low_price=float(row["Low"]),
                        close_price=float(row["Close"]),
                        volume=int(row["Volume"])
                    )
                    db_record = StockData(**valid_data.model_dump())
                    db.add(db_record)
                    records_added +=1
        except Exception as e:
            print(f"error while processing {ticker}:{e}")
            db.rollback()
            raise HTTPException(status_code=500,detail=str(e))

    db.commit()

    return{
        "-m":"ingestion compleate",
        "new_records_added":records_added
    }

