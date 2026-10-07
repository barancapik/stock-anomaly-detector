from pydantic import BaseModel
from typing import List,Optional

class ReportRequest(BaseModel):
    ticker:str
    query:Optional[str] = "Provide an executive summary of the most severe recent anomalies and the associated market risks."

class ReportResponse(BaseModel):
    ticker: str
    report_text : str
    context_used : List[str]
