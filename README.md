financial-rag-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/                 # Routes: /fetch, /detect, /chat
│   │   ├── core/                # DB connections and config
│   │   ├── ml/                  # Feature engineering & Isolation Forest
│   │   ├── rag/                 # ChromaDB client & Ollama prompt formatting
│   │   └── schemas/             # Pydantic models (Data validation)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py                   # Streamlit dashboard
│   ├── components/              # Charting functions (Plotly candlesticks)
│   ├── requirements.txt
│   └── Dockerfile
├── data/                        # Persistent volume for SQLite & ChromaDB
├── docker-compose.yml           # Runs Backend, Frontend, and Ollama together
└── README.md