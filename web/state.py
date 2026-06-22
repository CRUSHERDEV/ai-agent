# web/state.py

import time

# -------------------------
# SIMPLE CIA MEMORY ENGINE
# -------------------------

LOGS = [
    "System initialized",
    "Agent ready",
    "Waiting for query..."
]

DECISION = {
    "action": "HOLD",
    "confidence": 0,
    "reason": "No analysis yet"
}


ASSETS = {
    "BTC": 72,
    "USD": 55,
    "GOLD": 60
}


RELATIONSHIPS = [
    {"from": "BTC", "to": "USD", "weight": -0.65},
    {"from": "GOLD", "to": "USD", "weight": 0.40},
    {"from": "BTC", "to": "GOLD", "weight": 0.25},
]


# -------------------------
# PUBLIC API FUNCTIONS
# -------------------------

def get_asset_scores():
    return ASSETS


def get_relationships():
    return RELATIONSHIPS


def get_logs():
    return LOGS[-20:]  # last 20 logs


def get_last_decision():
    return DECISION


# -------------------------
# CALLED BY YOUR AGENT
# (OPTIONAL HOOK)
# -------------------------

def update_logs(message: str):
    LOGS.append(f"{time.strftime('%H:%M:%S')} - {message}")


def update_decision(action: str, confidence: int, reason: str):
    global DECISION
    DECISION = {
        "action": action,
        "confidence": confidence,
        "reason": reason
    }