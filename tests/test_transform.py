import pytest
import pandas as pd
import numpy as np
from pipeline.transform import transform


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """DataFrame ที่มีข้อมูลครบ 60 วัน (มากพอให้คำนวณ MA_50 ได้)"""
    n = 60
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.array([30.0 + i * 0.1 for i in range(n)])
    return pd.DataFrame({
        "Open":   close - 0.5,
        "High":   close + 1.0,
        "Low":    close - 1.0,
        "Close":  close,
        "Volume": [1000] * n,
        "ticker": ["PTT.BK"] * n,
    }, index=idx)


@pytest.fixture
def df_with_zero_volume(sample_df):
    """DataFrame ที่มีบางแถวที่ Volume = 0"""
    df = sample_df.copy()
    df.loc[df.index[5], "Volume"] = 0
    df.loc[df.index[10], "Volume"] = 0
    return df


# ── Column Output ────────────────────────────────────────────────────────────

class TestTransformColumns:

    def test_output_has_ma20_column(self, sample_df):
        result = transform(sample_df)
        assert "MA_20" in result.columns

    def test_output_has_ma50_column(self, sample_df):
        result = transform(sample_df)
        assert "MA_50" in result.columns

    def test_output_has_rsi14_column(self, sample_df):
        result = transform(sample_df)
        assert "RSI_14" in result.columns

    def test_output_has_signal_column(self, sample_df):
        result = transform(sample_df)
        assert "signal" in result.columns


# ── Data Cleaning ────────────────────────────────────────────────────────────

class TestDataCleaning:

    def test_removes_zero_volume_rows(self, df_with_zero_volume):
        """แถวที่ Volume = 0 ต้องถูกตัดออก"""
        result = transform(df_with_zero_volume)
        assert (result["Volume"] > 0).all()

    def test_row_count_reduced_after_zero_volume_filter(self, df_with_zero_volume):
        """จำนวนแถวต้องลดลงหลังตัด Volume = 0 ออก"""
        original_len = len(df_with_zero_volume)
        result = transform(df_with_zero_volume)
        assert len(result) < original_len


# ── Feature Engineering ──────────────────────────────────────────────────────

class TestFeatureEngineering:

    def test_ma20_is_rolling_mean(self, sample_df):
        """MA_20 ต้องเท่ากับ rolling mean 20 วันของราคาปิด"""
        result = transform(sample_df)
        expected = sample_df["Close"].rolling(20).mean()
        pd.testing.assert_series_equal(
            result["MA_20"].dropna(),
            expected.dropna(),
            check_names=False
        )

    def test_rsi_range(self, sample_df):
        """RSI ต้องอยู่ในช่วง 0-100 เสมอ"""
        result = transform(sample_df)
        rsi = result["RSI_14"].dropna()
        assert (rsi >= 0).all() and (rsi <= 100).all()

    def test_signal_values_are_valid(self, sample_df):
        """ค่า signal ต้องเป็นแค่ bullish, bearish หรือ neutral เท่านั้น"""
        result = transform(sample_df)
        valid = {"bullish", "bearish", "neutral"}
        assert set(result["signal"].unique()).issubset(valid)


# ── Signal Logic ─────────────────────────────────────────────────────────────

class TestSignalLogic:

    def test_bullish_when_ma20_above_ma50(self, sample_df):
        """ถ้า MA_20 > MA_50 ต้องเป็น bullish"""
        result = transform(sample_df)
        mask = result["MA_20"] > result["MA_50"]
        assert (result.loc[mask, "signal"] == "bullish").all()

    def test_bearish_when_ma20_below_ma50(self):
        """ถ้า MA_20 < MA_50 ต้องเป็น bearish"""
        n = 60
        idx = pd.date_range("2024-01-01", periods=n, freq="D")
        # ราคาลดลงทุกวัน → MA_20 จะต่ำกว่า MA_50
        close = pd.array([60.0 - i * 0.2 for i in range(n)])
        df = pd.DataFrame({
            "Open": close - 0.5, "High": close + 1.0,
            "Low":  close - 1.0, "Close": close,
            "Volume": [1000] * n, "ticker": ["PTT.BK"] * n,
        }, index=idx)

        result = transform(df)
        mask = result["MA_20"] < result["MA_50"]
        assert (result.loc[mask, "signal"] == "bearish").all()


# ── Validation ───────────────────────────────────────────────────────────────

class TestValidation:

    def test_raises_on_negative_close(self, sample_df):
        """ถ้าราคาปิดติดลบต้องเกิด AssertionError"""
        df = sample_df.copy()
        df.loc[df.index[30], "Close"] = -1.0
        with pytest.raises(AssertionError):
            transform(df)