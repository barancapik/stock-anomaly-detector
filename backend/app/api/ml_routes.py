from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.machine_learning.detector import detect_and_store_anomalies

router = APIRouter()

TARGET_TICKERS = ["THYAO.IS", "GARAN.IS"]

@router.post("/detect/")
def run_anomaly_detection(db:Session=Depends(get_db)):
    total_anomalies = 0
    try:
        for ticker in TARGET_TICKERS:
            count = detect_and_store_anomalies(db,ticker)
            total_anomalies += count
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Detection complete", "new_anomalies_detected": total_anomalies}