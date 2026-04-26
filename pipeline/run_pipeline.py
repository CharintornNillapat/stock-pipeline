import subprocess
import pandas as pd
from pathlib import Path
from ingest import fetch_with_retry, get_last_date, TICKERS
from transform import transform

# Root project folder
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def save_parquet(df: pd.DataFrame, path: Path):
    df.to_parquet(path)


def git_push(commit_message: str):
    commands = [
        ["git", "config", "user.email", "actions@github.com"],
        ["git", "config", "user.name", "GitHub Actions"],
        ["git", "add", "data/"],
        ["git", "commit", "-m", commit_message],
        ["git", "push"],
    ]

    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(result.stderr)
            break


# --- Main ---
for ticker in TICKERS:
    raw_path = RAW_DIR / f"{ticker}.parquet"
    processed_path = PROCESSED_DIR / f"{ticker}.parquet"

    start_date = get_last_date(raw_path)
    df_raw = fetch_with_retry(ticker, start=start_date)

    save_parquet(df_raw, raw_path)

    df_processed = transform(df_raw)
    save_parquet(df_processed, processed_path)

git_push("chore: update data")