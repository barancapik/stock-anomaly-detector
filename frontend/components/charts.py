import plotly.graph_objects as go
import pandas as pd

def build_anomaly_chart(price_df: pd.DataFrame, anomaly_df: pd.DataFrame, ticker: str) -> go.Figure:
    fig = go.Figure()

    # 1. Base Candlestick Chart
    fig.add_trace(
        go.Candlestick(
            x=price_df['date'],
            open=price_df['open_price'],
            high=price_df['high_price'],
            low=price_df['low_price'],
            close=price_df['close_price'],
            name="OHLC",
            increasing_line_color="#09c428",
            decreasing_line_color="#b63533"
        )
    )

    # 2. Overlay Isolation Forest Outliers
    if not anomaly_df.empty:
        # Merge to align anomaly coordinates with the corresponding day's high price
        merged = pd.merge(anomaly_df, price_df, on='date', how='inner')

        fig.add_trace(
            go.Scatter(
                x=merged['date'],
                y=merged['high_price'] * 1.02,  # Position marker slightly above candle
                mode='markers+text',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color="#e91212",
                    line=dict(width=1, color='white')
                ),
                text=["⚠️" for _ in range(len(merged))],
                textposition="top center",
                name="ML Anomaly",
                hovertemplate=(
                    "<b>Date:</b> %{x}<br>" +
                    "<b>Log Return:</b> %{customdata[0]:.4f}<br>" +
                    "<b>Vol (20d):</b> %{customdata[1]:.4f}<br>" +
                    "<b>Vol Z-Score:</b> %{customdata[2]:.2f}σ<br>" +
                    "<b>Severity:</b> %{customdata[3]}<extra></extra>"
                ),
                customdata=merged[['log_return', 'volatility_20d', 'volume_z_score', 'severity']].values
            )
        )

    fig.update_layout(
        title=f"{ticker} — Price Action & Detected Outliers",
        yaxis_title="Price (TRY)",
        xaxis_title="Timeline",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=550,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig