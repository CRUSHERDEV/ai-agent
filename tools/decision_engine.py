import logging

logger = logging.getLogger(__name__)

class DecisionEngine:

    def build_decision(
        self,
        signal_data,
        regime_data,
        risk_data
    ):
        # Safe extraction layer using .get() to prevent missing key failures
        signal = signal_data.get("signal", "HOLD")
        regime = regime_data.get("regime", "NEUTRAL")
        score = float(signal_data.get("score", 0))
        reasons = list(signal_data.get("reasons", []))

        # Core baseline tracking metric
        confidence = 50

        # Directional mapping variables
        is_bull_signal = score > 0
        is_bear_signal = score < 0

        # ======================
        # SIGNAL QUALITY
        # ======================
        confidence += abs(score) * 5

        # ======================
        # REGIME BOOST & DIRECTIONAL ALIGNMENT
        # ======================
        # Structural fix: Ensure the macro regime direction matches alpha signal vector
        if regime in ["TRENDING_BULL", "EUPHORIA"]:
            if is_bull_signal:
                confidence += 15
                reasons.append(f"Macro Confluence: Bullish directional vector aligns with dominant {regime} regime.")
            elif is_bear_signal:
                confidence -= 25  # Substantial structural penalty for counter-trend execution
                reasons.append(f"Macro Divergence: Bearish execution signal heavily conflicts with macro {regime} momentum.")
            else:
                confidence += 5

        elif regime in ["TRENDING_BEAR", "PANIC"]:
            if is_bear_signal:
                confidence += 15
                reasons.append(f"Macro Confluence: Bearish directional vector aligns with dominant {regime} regime.")
            elif is_bull_signal:
                confidence -= 25  # Substantial structural penalty for counter-trend execution
                reasons.append(f"Macro Divergence: Bullish execution signal heavily conflicts with macro {regime} momentum.")
            else:
                confidence += 5

        elif regime == "RANGING":
            confidence -= 10
            reasons.append("Structural Compression: Market state classified as RANGING. Reducing trade allocation limits.")

        # ======================
        # RISK FILTER ANALYSIS
        # ======================
        # Actively ingest and parse risk indicators to protect trading boundaries
        if isinstance(risk_data, dict):
            risk_level = str(risk_data.get("risk_level", risk_data.get("level", ""))).upper()
            risk_score = risk_data.get("risk_score", risk_data.get("score", 0))

            if risk_level in ["HIGH", "CRITICAL"] or (isinstance(risk_score, (int, float)) and risk_score >= 70):
                confidence -= 15
                reasons.append("Risk Mitigation Override: Systemic or volume-based risk parameters exceed normal boundaries.")
            elif risk_level == "LOW" or (isinstance(risk_score, (int, float)) and 0 < risk_score <= 30):
                confidence += 5

        # Hard mathematical containment thresholds
        confidence = max(0, min(100, round(float(confidence))))

        # ======================
        # EXECUTION DECISION
        # ======================
        if confidence >= 80:
            action = "EXECUTE"
        elif confidence >= 60:
            action = "WATCHLIST"
        else:
            action = "NO TRADE"

        logger.info(f"Decision Matrix Complete -> Action: {action} | Conf: {confidence}% | Regime: {regime}")

        return {
            "action": action,
            "confidence": confidence,
            "signal": signal,
            "regime": regime,
            "risk": risk_data,
            "reasons": reasons
        }


decision_engine = DecisionEngine()