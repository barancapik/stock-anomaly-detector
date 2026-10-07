from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import ingestion, ml_routes,rag_routes,report_routes, data_routes
from app.models import market_data, anomaly


Base.metadata.create_all(bind = engine)
app = FastAPI(title="Figro Engine API")

app.include_router(ingestion.router, prefix= "/api", tags = ["Data Ingestion"])
app.include_router(ml_routes.router, prefix="/api", tags=["Machine Learning"])
app.include_router(rag_routes.router,prefix="/api",tags=["RAG"])
app.include_router(report_routes.router, prefix="/api", tags=["AI Reporting"])
app.include_router(data_routes.router, prefix="/api", tags=["market data"])

@app.get("/")
def health_check():
    return{"status": "Fipro backend is running"}