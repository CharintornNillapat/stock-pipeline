import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pipeline.ingest import fetch_with_retry, get_last_date


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """DataFrame จำลองที่ yfinance ควรจะคืนมา"""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame({
        "Open":   [30.0, 31.0, 32.0, 33.0, 34.0],
        "High":   [31.0, 32.0, 33.0, 34.0, 35.0],
        "Low":    [29.0, 30.0, 31.0, 32.0, 33.0],
        "Close":  [30.5, 31.5, 32.5, 33.5, 34.5],
        "Volume": [1000, 2000, 3000, 4000, 5000],
    }, index=idx)


# ── fetch_with_retry ─────────────────────────────────────────────────────────

class TestFetchWithRetry:

    @patch("pipeline.ingest.yf.download")
    def test_returns_dataframe_on_success(self, mock_download, sample_df):
        """ถ้า yfinance ตอบกลับปกติ ต้องได้ DataFrame และมีคอลัมน์ ticker"""
        mock_download.return_value = sample_df
        result = fetch_with_retry("PTT.BK", start="2024-01-01")

        assert isinstance(result, pd.DataFrame)
        assert "ticker" in result.columns
        assert result["ticker"].iloc[0] == "PTT.BK"

    @patch("pipeline.ingest.yf.download")
    def test_ticker_column_value_is_correct(self, mock_download, sample_df):
        """ค่าใน column ticker ต้องตรงกับ ticker ที่ส่งเข้าไป"""
        mock_download.return_value = sample_df
        result = fetch_with_retry("AOT.BK", start="2024-01-01")
        assert (result["ticker"] == "AOT.BK").all()

    @patch("pipeline.ingest.time.sleep")
    @patch("pipeline.ingest.yf.download")
    def test_retries_on_failure_then_succeeds(self, mock_download, mock_sleep, sample_df):
        """ถ้าล้มเหลว 2 ครั้งแล้วสำเร็จครั้งที่ 3 ต้องคืน DataFrame ได้ปกติ"""
        mock_download.side_effect = [Exception("timeout"), Exception("timeout"), sample_df]
        result = fetch_with_retry("PTT.BK", start="2024-01-01", retries=3)

        assert not result.empty
        assert mock_download.call_count == 3

    @patch("pipeline.ingest.time.sleep")
    @patch("pipeline.ingest.yf.download")
    def test_returns_empty_df_when_all_retries_fail(self, mock_download, mock_sleep):
        """ถ้าล้มเหลวครบทุก attempt ต้องคืน DataFrame เปล่า"""
        mock_download.side_effect = Exception("network error")
        result = fetch_with_retry("PTT.BK", start="2024-01-01", retries=3)

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert mock_download.call_count == 3

    @patch("pipeline.ingest.time.sleep")
    @patch("pipeline.ingest.yf.download")
    def test_sleep_called_between_retries(self, mock_download, mock_sleep):
        """ต้องมีการ sleep ระหว่าง retry"""
        mock_download.side_effect = Exception("error")
        fetch_with_retry("PTT.BK", start="2024-01-01", retries=3)

        assert mock_sleep.call_count == 3


# ── get_last_date ────────────────────────────────────────────────────────────

class TestGetLastDate:

    def test_returns_fallback_when_file_not_found(self, tmp_path):
        """ถ้าไม่มีไฟล์ ต้องคืน fallback date 2024-01-01"""
        fake_path = str(tmp_path / "nonexistent.parquet")
        result = get_last_date(fake_path)
        assert result == "2024-01-01"

    def test_returns_max_date_from_existing_file(self, tmp_path, sample_df):
        """ถ้ามีไฟล์อยู่แล้ว ต้องคืนวันล่าสุดใน index"""
        filepath = str(tmp_path / "PTT.BK.parquet")
        sample_df.to_parquet(filepath)

        result = get_last_date(filepath)
        assert result == "2024-01-05"

    def test_returns_string_format(self, tmp_path, sample_df):
        """วันที่ที่คืนมาต้องเป็น string format YYYY-MM-DD"""
        filepath = str(tmp_path / "PTT.BK.parquet")
        sample_df.to_parquet(filepath)

        result = get_last_date(filepath)
        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD