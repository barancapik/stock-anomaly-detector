from pydantic import BaseModel, ConfigDict
from datetime import date

class AnomalyBase(BaseModel):
    ticker: str
    date: date
    log_return:float
    volatility_20d: float
    volume_z_score:float
    anomaly_score :float
    severity: str

class AnomalyCreate(AnomalyBase):
    pass

class AnomalyResponse(AnomalyBase):
    id:int
    model_config= ConfigDict(from_attributes = True)
