import logging
import math
from typing import Dict, Any

# Initialize institutional logging framework
logger = logging.getLogger("RegimeEngine")

class RegimeEngine:

    def detect_regime(
        self,
        market_regime: str,
        sentiment: float,
        z_score: float,
        volatility: float
    ) -> Dict[str, Any]:
        """
        Classifies the prevailing market regime using broad market participation,
        momentum sentiment, extreme technical deviations (Z-scores), and volatility.
        
        Guarantees complete safety against uncoerced string inputs, None values, and NaN errors.
        """
        reasons = []

        # ==========================
        # INPUT SANITIZATION
        # ==========================
        # Safe string normalization
        market_regime_clean = str(market_regime).strip().upper() if market_regime is not None else "NEUTRAL"
        
        # Safe numeric casting with fallbacks to protect against type errors
        try:
            sentiment_val = float(sentiment) if sentiment is not None else 0.0
            if math.isnan(sentiment_val) or math.isinf(sentiment_val):
                sentiment_val = 0.0
        except (ValueError, TypeError):
            logger.warning(f"Invalid sentiment parameter type received: {sentiment}. Defaulting to 0.0")
            sentiment_val = 0.0

        try:
            z_score_val = float(z_score) if z_score is not None else 0.0
            if math.isnan(z_score_val) or math.isinf(z_score_val):
                z_score_val = 0.0
        except (ValueError, TypeError):
            logger.warning(f"Invalid z_score parameter type received: {z_score}. Defaulting to 0.0")
            z_score_val = 0.0

        try:
            volatility_val = float(volatility) if volatility is not None else 0.0
            if math.isnan(volatility_val) or math.isinf(volatility_val):
                volatility_val = 0.0
        except (ValueError, TypeError):
            logger.warning(f"Invalid volatility parameter type received: {volatility}. Defaulting to 0.0")
            volatility_val = 0.0

        # ==========================
        # RISK ENVIRONMENT
        # ==========================
        # Supports both legacy RISK-ON / RISK-OFF strings and modern TRENDING_BULL / TRENDING_BEAR indicators
        if market_regime_clean in ["RISK-ON", "RISK_ON", "TRENDING_BULL"]:
            reasons.append("Broad market participation bullish")
            base_regime = "RISK_ON"
        elif market_regime_clean in ["RISK-OFF", "RISK_OFF", "TRENDING_BEAR"]:
            reasons.append("Broad market participation bearish")
            base_regime = "RISK_OFF"
        else:
            reasons.append("Market participation neutral")
            base_regime = "NEUTRAL"

        # ==========================
        # PANIC DETECTION
        # ==========================
        if z_score_val < -3.0:
            logger.info("Market regime classified as: PANIC due to extreme downside deviation.")
            return {
                "regime": "PANIC",
                "confidence": 90,
                "reasons": reasons + ["Extreme downside deviation detected"]
            }

        # ==========================
        # EUPHORIA DETECTION
        # ==========================
        if z_score_val > 3.0:
            logger.info("Market regime classified as: EUPHORIA due to extreme upside deviation.")
            return {
                "regime": "EUPHORIA",
                "confidence": 90,
                "reasons": reasons + ["Extreme upside deviation detected"]
            }

        # ==========================
        # TRENDING DETECTION
        # ==========================
        if abs(sentiment_val) > 0.50:
            if sentiment_val > 0.0:
                logger.info("Market regime classified as: TRENDING_BULL due to positive sentiment momentum.")
                return {
                    "regime": "TRENDING_BULL",
                    "confidence": 80,
                    "reasons": reasons + ["Strong positive sentiment"]
                }
            else:
                logger.info("Market regime classified as: TRENDING_BEAR due to negative sentiment momentum.")
                return {
                    "regime": "TRENDING_BEAR",
                    "confidence": 80,
                    "reasons": reasons + ["Strong negative sentiment"]
                }

        # ==========================
        # VOLATILITY CHECK
        # ==========================
        if volatility_val > 3.0:
            logger.info("Market regime classified as: HIGH_VOLATILITY.")
            return {
                "regime": "HIGH_VOLATILITY",
                "confidence": 75,
                "reasons": reasons + ["Large market swings detected"]
            }

        # ==========================
        # RANGE MARKET
        # ==========================
        logger.info("Market regime classified as: RANGING.")
        return {
            "regime": "RANGING",
            "confidence": 60,
            "reasons": reasons + ["No strong directional bias"]
        }


# Globally exposed instantiation mapping back perfectly to system components
regime_engine = RegimeEngine()