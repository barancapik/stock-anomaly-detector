from sqlalchemy import Column, Float, Integer, String, Date
from app.core.database import Base

class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String,index=True, nullable=False)
    date = Column(Date, nullable=False)
    log_return = Column(Float, nullable=False)
    volatility_20d = Column(Float, nullable=False)
    volume_z_score = Column(Float,nullable=False)
    anomaly_score = Column(Float,nullable=False)
    severity = Column(String,nullable=False)
    