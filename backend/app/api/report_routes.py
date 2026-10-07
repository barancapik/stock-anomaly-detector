from fastapi import APIRouter, HTTPException
from app.schemas.report import ReportRequest, ReportResponse
from app.rag.generator import generate_risk_report
from app.core.ollama import check_ollama

router = APIRouter()

@router.post("/generate-report", response_model=ReportResponse)
async def create_report(request: ReportRequest):
    check_ollama()
    try:
        report_text , context = await generate_risk_report(
            ticker=request.ticker,
            query=request.query
        )

        return ReportResponse(
            ticker=request.ticker,
            report_text = report_text,
            context_used = context
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail= str(e))
