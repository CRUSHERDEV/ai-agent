import math
import logging

logger = logging.getLogger(__name__)

def calculate_confidence(evidence):
    """
    Calculates a statistically adjusted confidence score based on verified evidence.
    Applies mathematical penalties for data contradiction (variance) and tiny sample sizes.
    """
    if not evidence:
        return {
            "score": 0,
            "label": "LOW"
        }

    try:
        # Extract raw confidence values safely (assumes floats between 0.0 and 1.0)
        raw_scores = [float(x["confidence"]) for x in evidence if "confidence" in x]
        n = len(raw_scores)
        
        if n == 0:
            return {"score": 0, "label": "LOW"}

        # 1. Base Arithmetic Average
        base_avg = sum(raw_scores) / n

        # 2. Consensus Variance Penalty
        # If sources wildly contradict each other, drop systemic confidence.
        if n > 1:
            variance = sum((score - base_avg) ** 2 for score in raw_scores) / n
            # Max possible variance for values bounded by [0, 1] is 0.25. 
            # We scale the penalty so heavy disagreement actively damages the score.
            variance_penalty = variance * 0.40
        else:
            # Single source has a built-in variance penalty because there is no consensus confirmation
            variance_penalty = 0.10

        # 3. Sample Size Weighting (Law of Small Numbers)
        # Quant models discount metrics built on tiny datasets. 
        # We require a baseline sample size (e.g., 5 or more unique sources) for maximum score realization.
        sample_size_factor = min(1.0, n / 5.0)

        # 4. Synthesize Adjusted Statistical Score
        adjusted_score = (base_avg - variance_penalty) * sample_size_factor
        
        # Norm and clamp safely between integer scales of 0 and 100
        score = max(0, min(100, round(adjusted_score * 100)))

    except Exception as e:
        logger.error(f"Error executing quantitative confidence adjustment: {e}")
        # Structural fallback to prevent killing the agent execution loop
        score = 0

    # Retain your exact system downstream categorical thresholds
    if score >= 80:
        label = "HIGH"
    elif score >= 60:
        label = "MEDIUM"
    else:
        label = "LOW"

    return {
        "score": score,
        "label": label
    }