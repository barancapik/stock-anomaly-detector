from sqlalchemy.orm import Session
from app.models.anomaly import AnomalyEvent
from app.rag.vector_store import get_anomaly_collection

def vectorize_anomalies(db: Session):
    collection = get_anomaly_collection()

    anomalies = db.query(AnomalyEvent).all()


    if not anomalies:
        return 0
    documents = []
    metadatas = []
    ids = []

    for anomaly in anomalies:
        text_representation = (
            f"On {anomaly.date}, the asset {anomaly.ticker} experienced a {anomaly.severity} market anomaly. "
            f"The log return was {anomaly.log_return:.4f}, with a 20-day volatility of {anomaly.volatility_20d:.4f}. "
            f"Trading volume was {anomaly.volume_z_score:.2f} standard deviations from the 20-day average."
        )

        documents.append(text_representation)

        metadatas.append({
            "ticker": anomaly.ticker,
            "date": anomaly.date.isoformat(),
            "severity": anomaly.severity
        })

        ids.append(f"{anomaly.ticker}_{anomaly.date}")

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    return len(ids)