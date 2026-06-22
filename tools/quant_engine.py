import numpy as np
import pandas as pd
import logging
from typing import Union, List, Optional

# Initialize institutional logging framework
logger = logging.getLogger("QuantEngine")

class QuantEngine:

    # ===================================
    # EWMA (Exponentially Weighted Moving Average)
    # ===================================
    @staticmethod
    def ewma(series: Union[List[float], np.ndarray, pd.Series], span: int = 20) -> Optional[float]:
        if series is None:
            return None
            
        try:
            # Safely cast input to a standard Pandas Series
            pd_series = pd.Series(series)
            
            # Filter out any non-numeric or NaN entries
            pd_series = pd.to_numeric(pd_series, errors='coerce').dropna()

            if len(pd_series) < span:
                logger.debug(f"EWMA aborted: Series length ({len(pd_series)}) is less than required span ({span}).")
                return None

            # Calculate the exponentially weighted moving average
            ewma_series = pd_series.ewm(span=span, adjust=False).mean()
            
            # Extract the last scalar value safely using direct integer location index (.iloc)
            # This avoids index label KeyError crashes.
            val = ewma_series.iloc[-1]
            return float(val) if not np.isnan(val) else None

        except Exception as e:
            logger.error(f"Quant calculations failed inside ewma module: {e}")
            return None

    # ===================================
    # Z-SCORE (Standardized Score)
    # ===================================
    @staticmethod
    def z_score(series: Union[List[float], np.ndarray, pd.Series]) -> Optional[float]:
        if series is None:
            return None
            
        try:
            # Safely cast to standard Numpy array for raw vector performance
            np_arr = np.asarray(series, dtype=float)
            # Purge any NaN or infinite numeric nodes
            np_arr = np_arr[np.isfinite(np_arr)]

            n = len(np_arr)
            if n < 20:
                logger.debug(f"Z-score aborted: Safe numeric sample count ({n}) is less than required 20.")
                return None

            mean = np.mean(np_arr)
            std = np.std(np_arr)

            # High-precision division guard: Check if standard deviation is zero 
            # or infinitely close to zero (floating-point epsilon)
            if std <= 1e-8:
                return 0.0

            # Direct array index lookup using raw NumPy indices.
            # This avoids Pandas label-matching KeyError crashes.
            last_value = float(np_arr[-1])
            z = (last_value - mean) / std
            
            return float(z) if np.isfinite(z) else 0.0

        except Exception as e:
            logger.error(f"Quant calculations failed inside z_score module: {e}")
            return None

    # ===================================
    # ATR (Average True Range)
    # ===================================
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return None

        try:
            # Check if all critical price columns exist inside the dataframe
            required_cols = ["High", "Low", "Close"]
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"ATR Calculation aborted: Dataframe is missing columns. Required: {required_cols}")
                return None

            # Unpack columns safely using clean pandas types
            high = pd.to_numeric(df["High"], errors='coerce')
            low = pd.to_numeric(df["Low"], errors='coerce')
            close = pd.to_numeric(df["Close"], errors='coerce')

            # Drop missing value rows that would break statistical indicators
            valid_idx = high.notna() & low.notna() & close.notna()
            high = high[valid_idx]
            low = low[valid_idx]
            close = close[valid_idx]

            if len(high) < period:
                logger.debug(f"ATR aborted: Available price periods ({len(high)}) are less than {period}.")
                return None

            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))

            # Combine True Range vectors and fetch maximum scalar row by row
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Standard Rolling Mean ATR
            atr_series = tr.rolling(period).mean()

            val = atr_series.iloc[-1]
            return float(val) if not np.isnan(val) else None

        except Exception as e:
            logger.error(f"Quant calculations failed inside ATR module: {e}")
            return None

    # ===================================
    # TANH SENTIMENT NORMALIZATION
    # ===================================
    @staticmethod
    def normalize_sentiment(score: float) -> float:
        try:
            if score is None:
                return 0.0
            # Maps any raw scalar input safely into bounds between -1.0 and 1.0
            return float(np.tanh(float(score)))
        except Exception as e:
            logger.error(f"Sentiment normalization crash: {e}")
            return 0.0

    # ===================================
    # POSITION SIZING MATRIX
    # ===================================
    @staticmethod
    def position_size(
        equity: float,
        risk_percent: float,
        atr: float
    ) -> float:
        try:
            # Type checks and numerical bounds guards
            equity_val = float(equity) if equity else 0.0
            risk_val = float(risk_percent) if risk_percent else 0.0
            atr_val = float(atr) if atr else 0.0

            if atr_val <= 0.0 or equity_val <= 0.0 or risk_val <= 0.0:
                return 0.0

            risk_amount = equity_val * (risk_val / 100.0)
            units = risk_amount / atr_val

            return round(float(units), 4)

        except Exception as e:
            logger.error(f"Quant calculations failed inside position sizing engine: {e}")
            return 0.0


# Globally exposed instantiation mapping back perfectly to system components
quant_engine = QuantEngine()