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
    "ASML", "TSM",
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

# ── Signal Summary ───────────────────────────────────────────────────────────
# ── Signal Summary ───────────────────────────────────────────────────────────
signal = str(df["signal"].iloc[-1]) if "signal" in df.columns and not df.empty else "neutral"
rsi_val = get_val(df, "RSI_14", -1) if not df.empty else 50.0

if signal == "bullish":
    st.success("📈 **สัญญาณ: Bullish (ขาขึ้น)** — MA_20 ข้ามขึ้นเหนือ MA_50 บ่งบอกว่าแนวโน้มราคากำลังดีขึ้น น่าจับตามอง")
elif signal == "bearish":
    st.error("📉 **สัญญาณ: Bearish (ขาลง)** — MA_20 ต่ำกว่า MA_50 บ่งบอกว่าแนวโน้มราคากำลังอ่อนตัว ควรระวัง")
else:
    st.info("➡️ **สัญญาณ: Neutral** — ยังไม่มีสัญญาณชัดเจน MA_20 และ MA_50 ใกล้เคียงกันอยู่")

if rsi_val < 30:
    st.warning(f"⚠️ **RSI = {rsi_val:.1f}** — Oversold (ถูกขายมากเกินไป) บางครั้งเป็นจังหวะที่น่าสนใจสำหรับนักลงทุน")
elif rsi_val > 70:
    st.warning(f"⚠️ **RSI = {rsi_val:.1f}** — Overbought (ถูกซื้อมากเกินไป) ราคาอาจปรับตัวลงในระยะสั้น")
else:
    st.success(f"✅ **RSI = {rsi_val:.1f}** — อยู่ในโซนปกติ (30-70)")
if rsi_val < 30:
    st.warning(f"⚠️ **RSI = {rsi_val:.1f}** — Oversold (ถูกขายมากเกินไป) บางครั้งเป็นจังหวะที่น่าสนใจสำหรับนักลงทุน")
elif rsi_val > 70:
    st.warning(f"⚠️ **RSI = {rsi_val:.1f}** — Overbought (ถูกซื้อมากเกินไป) ราคาอาจปรับตัวลงในระยะสั้น")
else:
    st.success(f"✅ **RSI = {rsi_val:.1f}** — อยู่ในโซนปกติ (30-70)")

# ── Indicator Guide ──────────────────────────────────────────────────────────
with st.expander("📚 ตัวชี้วัดเหล่านี้คืออะไร? (คลิกเพื่อดู)"):
    st.markdown("""
    **📊 MA (Moving Average) — เส้นค่าเฉลี่ยเคลื่อนที่**
    - **MA_20** = ค่าเฉลี่ยราคาปิด 20 วันล่าสุด → บอกแนวโน้มระยะสั้น
    - **MA_50** = ค่าเฉลี่ยราคาปิด 50 วันล่าสุด → บอกแนวโน้มระยะกลาง
    - ถ้า MA_20 **ข้ามขึ้น**เหนือ MA_50 เรียกว่า **Golden Cross** → สัญญาณขาขึ้น 🟢
    - ถ้า MA_20 **ข้ามลง**ใต้ MA_50 เรียกว่า **Death Cross** → สัญญาณขาลง 🔴

    **📈 RSI (Relative Strength Index) — ดัชนีความแข็งแกร่งสัมพัทธ์**
    - วัดว่าหุ้นถูก "ซื้อ" หรือ "ขาย" มากเกินไปหรือเปล่า (ค่า 0-100)
    - **RSI < 30** = Oversold — ถูกขายมากเกิน อาจเด้งกลับขึ้น 🟡
    - **RSI 30-70** = โซนปกติ ✅
    - **RSI > 70** = Overbought — ถูกซื้อมากเกิน อาจปรับตัวลง 🟡

    **🚦 Signal**
    - **Bullish** = แนวโน้มขาขึ้น (MA_20 > MA_50)
    - **Bearish** = แนวโน้มขาลง (MA_20 < MA_50)
    - **Neutral** = ยังไม่มีทิศทางชัดเจน

    > ⚠️ **หมายเหตุ:** ตัวชี้วัดเหล่านี้เป็นเพียงการวิเคราะห์ทางเทคนิคเบื้องต้น
    > ไม่ใช่คำแนะนำการลงทุน ควรศึกษาข้อมูลเพิ่มเติมก่อนตัดสินใจซื้อขายเสมอ
    """)

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
    
