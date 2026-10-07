import pandas as pd 
import numpy as np
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.models.market_data import StockData
from app.models.anomaly import AnomalyEvent
from app.schemas.anomaly import AnomalyCreate

def detect_and_store_anomalies(db:Session,ticker:str):
    records = db.query(StockData).filter(StockData.ticker == ticker).order_by(StockData.date).all()
    if not records:
        return 0

    df = pd.DataFrame([{
        "date": record.date,
        "close": record.close_price,
        "volume":record.volume
    }for record in records])
    df.set_index("date", inplace=True)

    df['log_return'] = np.log((df['close']) / df['close'].shift())

    df['volatility_20d'] = df['log_return'].rolling(window=20).std()

    df['volume_mean_20d'] = df['volume'].rolling(window=20).mean()
    df['volume_std_20d'] = df['volume'].rolling(window=20).std()
    df['volume_z_score'] = (df['volume'] - df['volume_mean_20d']) / df['volume_std_20d']

    df.dropna(inplace=True)

    features = ['log_return', 'volatility_20d', 'volume_z_score']
    X = df[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(contamination=0.03, random_state=42)
    df['is_anomaly'] = model.fit_predict(X_scaled)

    df['anomaly_score'] = model.decision_function(X_scaled)

    anomalies = df[df['is_anomaly'] == -1]

    new_anomalies_count = 0

    for date, row in anomalies.iterrows():
        existing = db.query(AnomalyEvent).filter(
            AnomalyEvent.ticker == ticker,
            AnomalyEvent.date == date
        ).first()

        if not existing:
            severity = "Critical" if row['anomaly_score'] < -0.15 else "High"
            
            anomaly_data = AnomalyCreate(
                ticker=ticker,
                date=date,
                log_return=float(row['log_return']),
                volatility_20d=float(row['volatility_20d']),
                volume_z_score=float(row['volume_z_score']),
                anomaly_score=float(row['anomaly_score']),
                severity=severity
            )
            
            db_anomaly = AnomalyEvent(**anomaly_data.model_dump())
            db.add(db_anomaly)
            new_anomalies_count += 1

    db.commit()
    return new_anomalies_count

