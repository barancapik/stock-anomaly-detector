from sqlalchemy import Column, Float, Integer, String,Date
from app.core.database import Base

class StockData(Base):
    __tablename__ = "stock_data"

    ticker = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    