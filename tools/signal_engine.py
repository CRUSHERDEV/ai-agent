# tools/signal_engine.py

from typing import Dict


class SignalEngine:

    def generate_signal(
        self,
        ewma_fast,
        ewma_slow,
        z_score,
        sentiment,
        atr
    ):

        score = 0

        reasons = []

        # =====================
        # TREND
        # =====================

        if ewma_fast > ewma_slow:
            score += 2
            reasons.append(
                "Bullish trend confirmed"
            )

        else:
            score -= 2
            reasons.append(
                "Bearish trend confirmed"
            )

        # =====================
        # Z SCORE
        # =====================

        if z_score < -2:
            score += 2
            reasons.append(
                "Deep oversold condition"
            )

        elif z_score > 2:
            score -= 2
            reasons.append(
                "Deep overbought condition"
            )

        # =====================
        # SENTIMENT
        # =====================

        if sentiment > 0.3:
            score += 1
            reasons.append(
                "Positive sentiment"
            )

        elif sentiment < -0.3:
            score -= 1
            reasons.append(
                "Negative sentiment"
            )

        # =====================
        # ATR
        # =====================

        if atr > 0:

            if atr > 0.05:
                reasons.append(
                    "High volatility"
                )

            else:
                reasons.append(
                    "Normal volatility"
                )

        # =====================
        # DECISION
        # =====================

        if score >= 3:

            signal = "STRONG BUY"

        elif score >= 1:

            signal = "BUY"

        elif score <= -3:

            signal = "STRONG SELL"

        elif score <= -1:

            signal = "SELL"

        else:

            signal = "NEUTRAL"

        return {
            "signal": signal,
            "score": score,
            "reasons": reasons
        }


signal_engine = SignalEngine()