import pandas as pd

def transform(df: pd.DataFrame) -> pd.DataFrame:

    # --- Handle MultiIndex columns ---
    if isinstance(df["Close"], pd.DataFrame):
        close = df["Close"].iloc[:, 0]
    else:
        close = df["Close"]

    if isinstance(df["Volume"], pd.DataFrame):
        volume = df["Volume"].iloc[:, 0]
    else:
        volume = df["Volume"]

    # --- Cleaning ---
    df = df[volume > 0].copy()
    df = df.ffill()

    # refresh close after filtering
    close = close.loc[df.index]

    # --- Validation ---
    assert (close > 0).all(), "พบราคาปิดที่ผิดปกติ"

    # --- Feature Engineering ---
    df["MA_20"] = close.rolling(20).mean()
    df["MA_50"] = close.rolling(50).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()

    df["RSI_14"] = 100 - (100 / (1 + gain / loss))

    df["signal"] = "neutral"
    df.loc[df["MA_20"] > df["MA_50"], "signal"] = "bullish"
    df.loc[df["MA_20"] < df["MA_50"], "signal"] = "bearish"

    return df.round(4)