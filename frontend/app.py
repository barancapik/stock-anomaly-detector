import os
import streamlit as st
import requests
import pandas as pd
from components.charts import build_anomaly_chart

# Reads from Docker environment variable if present, else defaults to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")

st.set_page_config(
    page_title="Fipro | Market Risk & Anomaly System",
    page_icon="📈",
    layout="wide"
)

# Custom Styling Adjustments
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stMetric { background-color: #1e222d; padding: 12px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
st.sidebar.title("🛡️ Fipro Control Center")
selected_ticker = st.sidebar.selectbox("Select Asset", ["GARAN.IS", "THYAO.IS"])

st.sidebar.markdown("---")
st.sidebar.subheader("Pipeline Orchestration")

if st.sidebar.button("1. Ingest Latest Data", use_container_width=True):
    with st.spinner("Fetching Yahoo Finance data..."):
        try:
            res = requests.post(f"{API_BASE_URL}/ingest")
            if res.status_code == 200:
                st.sidebar.success(f"Ingested! New rows: {res.json().get('new_records_added')}")
                st.cache_data.clear() # Clear cache to show new data
            else:
                st.sidebar.error("Ingestion failed.")
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")

if st.sidebar.button("2. Run ML Detector", use_container_width=True):
    with st.spinner("Training Isolation Forest..."):
        try:
            res = requests.post(f"{API_BASE_URL}/detect")
            if res.status_code == 200:
                st.sidebar.success(f"Detected {res.json().get('new_anomalies_detected')} anomalies!")
                st.cache_data.clear()
            else:
                st.sidebar.error("ML Detection failed.")
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")

if st.sidebar.button("3. Index to Vector DB", use_container_width=True):
    with st.spinner("Embedding via Ollama nomic-embed-text..."):
        try:
            res = requests.post(f"{API_BASE_URL}/index-anomalies")

            if res.status_code == 200:
                st.sidebar.success(
                    f"Upserted {res.json().get('vectors_upserted')} vectors."
                )

            elif res.status_code == 503:
                error_detail = res.json().get(
                    "detail",
                    "Ollama is not available."
                )
                st.sidebar.error(f"⚠️ {error_detail}")

            else:
                st.sidebar.error(
                    f"Vectorization failed ({res.status_code})."
                )

        except requests.exceptions.ConnectionError:
            st.sidebar.error(
                "Could not connect to the Fipro backend."
            )

        except Exception as e:
            st.sidebar.error(f"Unexpected error: {e}")

# ----------------- DATA LOADING WITH ERROR HANDLING -----------------
@st.cache_data(ttl=60)
def load_market_data(ticker: str):
    try:
        p_res = requests.get(f"{API_BASE_URL}/market-data/{ticker}", timeout=5)
        a_res = requests.get(f"{API_BASE_URL}/anomalies/{ticker}", timeout=5)
        
        price_df = pd.DataFrame(p_res.json()) if p_res.status_code == 200 else pd.DataFrame()
        anomaly_df = pd.DataFrame(a_res.json()) if a_res.status_code == 200 else pd.DataFrame()
        
        return price_df, anomaly_df, None
    except requests.exceptions.ConnectionError:
        return pd.DataFrame(), pd.DataFrame(), "Connection refused: Backend service is starting up or offline."
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), str(e)

price_df, anomaly_df, conn_error = load_market_data(selected_ticker)

# ----------------- DASHBOARD MAIN -----------------
st.title(f"Quantitative Risk Briefing: {selected_ticker}")

if conn_error:
    st.error(f"⚠️ **Backend Communication Error:** {conn_error}")
    st.info("Please wait a moment for the backend container to finish booting up, then refresh the page.")
    st.stop()

if price_df.empty:
    st.warning("No data found. Use the sidebar to ingest and detect anomalies first.")
    st.stop()

# Key Financial Metrics Row
last_row = price_df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Last Close", f"{last_row['close_price']:.2f} TRY")
col2.metric("Total Trading Days", len(price_df))
col3.metric("Anomalies Flagged", len(anomaly_df))
col4.metric("Anomaly Rate", f"{(len(anomaly_df) / len(price_df) * 100):.1f}%")

# Main Interactive Candlestick Chart
st.plotly_chart(
    build_anomaly_chart(price_df, anomaly_df, selected_ticker),
    use_container_width=True
)

st.markdown("---")

# ----------------- RAG REPORT & CHAT -----------------
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📋 Executive Risk Briefing")
    
    if st.button("Generate Fresh Report with Llama 3.2", type="primary", use_container_width=True):
        with st.spinner("Querying ChromaDB & synthesizing report via Ollama..."):
            payload = {
                "ticker": selected_ticker,
                "query": "Provide a comprehensive executive risk briefing on recent severe anomalies."
            }
            try:
                res = requests.post(f"{API_BASE_URL}/generate-report", json=payload)
                if res.status_code == 200:
                    report_data = res.json()
                    st.session_state[f"report_{selected_ticker}"] = report_data
                    
                elif res.status_code == 503:
                    error_detail = res.json().get(
                        "detail",
                        "Ollama is not available."
                    )
                    st.error(f"⚠️ {error_detail}")

                else:
                    st.error(f"Failed to generate report ({res.status_code}).")
                     
            except Exception as e:
                st.error(f"Connection Error: {e}")

    report = st.session_state.get(f"report_{selected_ticker}")
    if report:
        st.markdown(report["report_text"])
        with st.expander("🔍 View Grounding Context (Retrieved from ChromaDB)"):
            for ctx in report["context_used"]:
                st.info(ctx)
    else:
        st.info("Click the button above to generate a deterministic LLM briefing from the latest anomalies.")

with right_col:
    st.subheader("💬 Interactive Anomaly Q&A")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User chat query
    if prompt := st.chat_input("Ask about volume spikes, volatility, or dates..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing vector database context..."):
                payload = {"ticker": selected_ticker, "query": prompt}
                try:
                    res = requests.post(f"{API_BASE_URL}/generate-report", json=payload)
                    if res.status_code == 200:
                        answer = res.json()["report_text"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    elif res.status_code == 503:
                        error_detail = res.json().get(
                            "detail",
                            "Ollama is not available."
                        )
                        st.error(f"⚠️ {error_detail}")

                    else:
                        st.error(
                            f"Error communicating with Ollama ({res.status_code})."
                        )
                except Exception as e:
                    st.error(f"Connection Error: {e}")