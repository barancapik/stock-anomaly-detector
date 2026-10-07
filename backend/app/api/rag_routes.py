from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.rag.indexer import vectorize_anomalies
from app.core.ollama import check_ollama

router = APIRouter()

@router.post("/index-anomalies")
def index_data(db:Session =Depends(get_db)):
    check_ollama()
    try:
        
        count = vectorize_anomalies(db)
        return {"message": "Vectorization complete", "vectors_upserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    