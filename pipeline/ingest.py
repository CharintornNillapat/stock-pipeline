import yfinance as yf
import pandas as pd
import time

TICKERS = [
    # หุ้นไทย SET
    "PTT.BK",
    "AOT.BK",
    "ADVANC.BK",
    "CPALL.BK",
    "SCB.BK",
    "KBANK.BK",
    # หุ้นต่างประเทศ
    "AAPL",
    "TSLA",
    "NVDA",
]

def fetch_with_retry(ticker: str, start: str, retries: int = 3) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            df = yf.download(ticker, start=start, progress=False)
            df["ticker"] = ticker
            return df
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {ticker}: {e}")
            time.sleep(5)
    return pd.DataFrame()  # return empty ถ้าล้มทุก attempt

def get_last_date(filepath: str) -> str:
    try:
        df_existing = pd.read_parquet(filepath)
        return df_existing.index.max().strftime("%Y-%m-%d")
    except FileNotFoundError:
        return "2024-01-01"  # ← เปลี่ยนเป็นวันที่ไกลพอ เช่น 2024-01-01