import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Config ──────────────────────────────────────────
st.set_page_config(page_title="Stock Dashboard", layout="wide")

TICKERS = [
    # หุ้นไทย SET
    "PTT.BK", "AOT.BK", "ADVANC.BK",
    "CPALL.BK", "SCB.BK", "KBANK.BK",
    # หุ้นต่างประเทศ
    "AAPL", "TSLA", "NVDA",
]

# ── Load Data ────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(ticker):
    df = pd.read_parquet(f"data/processed/{ticker}.parquet")
    # Drop duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    return df

# ── Helper: Safe Extraction ──────────────────────────
def get_val(dataframe, column_name, position):
    """Safely extracts a scalar float value, ignoring duplicate columns."""
    val = dataframe[column_name]
    # If duplicate columns somehow still exist, this forces it to take the first one
    if isinstance(val, pd.DataFrame):
        val = val.iloc[:, 0]
    return float(val.iloc[position])

# ── Sidebar ──────────────────────────────────────────
st.sidebar.title("⚙️ Settings")
selected = st.sidebar.selectbox("เลือกหุ้น", TICKERS)
df = load_data(selected)

# ── KPI Cards ────────────────────────────────────────
if len(df) >= 2:
    close_val = get_val(df, "Close", -1)
    prev_close = get_val(df, "Close", -2)
    change = close_val - prev_close
    pct = (change / prev_close) * 100 if prev_close != 0 else 0.0
elif len(df) == 1:
    close_val = get_val(df, "Close", -1)
    change = 0.0
    pct = 0.0
else:
    close_val = 0.0
    change = 0.0
    pct = 0.0

st.title(f"📈 {selected}")
col1, col2, col3, col4 = st.columns(4)

col1.metric("ราคาปิด", f"{close_val:.2f}", f"{change:+.2f} ({pct:+.2f}%)")

if not df.empty:
    col2.metric("MA 20",  f"{get_val(df, 'MA_20', -1):.2f}")
    col3.metric("MA 50",  f"{get_val(df, 'MA_50', -1):.2f}")
    col4.metric("RSI 14", f"{get_val(df, 'RSI_14', -1):.1f}")
else:
    col2.metric("MA 20", "N/A")
    col3.metric("MA 50", "N/A")
    col4.metric("RSI 14", "N/A")

# ── Candlestick + MA ─────────────────────────────────
if not df.empty:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3], vertical_spacing=0.05)

    # Note: If duplicate columns exist, Plotly handles it better, but we 
    # can force 1D arrays using the same logic if it crashes here.
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["MA_20"],
        line=dict(color="#00d4aa", width=1.5), name="MA 20"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["MA_50"],
        line=dict(color="#ff6b35", width=1.5), name="MA 50"), row=1, col=1)

    fig.add_trace(go.Bar(x=df.index, y=df["Volume"],
        marker_color="#2a3444", name="Volume"), row=2, col=1)

    fig.update_layout(height=600, xaxis_rangeslider_visible=False,
                      template="plotly_dark", showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

# ── Signal Table ─────────────────────────────────────
    st.subheader("📋 ข้อมูลล่าสุด 10 วัน")
    
    display_cols = ["Close", "MA_20", "MA_50", "RSI_14"]
    if "signal" in df.columns:
        display_cols.append("signal")
        
    st.dataframe(
        df.tail(10)[display_cols]
        .sort_index(ascending=False)
        .style.map(  # <--- CHANGED FROM applymap TO map
            lambda v: "color: #00d4aa" if v == "bullish"
                      else "color: #ff4d6d" if v == "bearish" else "",
            subset=["signal"] if "signal" in df.columns else []
        ),
        use_container_width=True
    )