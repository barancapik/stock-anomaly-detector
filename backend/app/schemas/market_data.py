from datetime import date
from pydantic import BaseModel, ConfigDict

class StockDataBase(BaseModel):
    ticker: str
    date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int


class StockDataCreate(StockDataBase):
    pass


class StockDataResponse(StockDataBase):
    model_config = ConfigDict(from_attributes=True)