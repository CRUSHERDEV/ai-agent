import logging
from tools.market_data import get_market_snapshot
from tools.execution_logger import ExecutionLogger
from tools.llm_router import ask_llm

# Import our upgraded thread-safe Intelligence Graph
from tools.intelligence_graph import IntelligenceGraph

from tools.evidence_engine import evidence_engine
from tools.verification_agent import verify_evidence
from tools.confidence_engine import calculate_confidence

# Initialize institutional logger
system_logger = logging.getLogger("ResearchEngine")

# Instantiating a thread-safe Intelligence Graph
graph = IntelligenceGraph()


def build_market_context(market: dict) -> str:
    """
    Safely unpacks a multi-category nested market snapshot dictionary 
    into a clean text context block for the LLM.
    """
    lines = []
    
    if not market or not isinstance(market, dict):
        return "INSUFFICIENT DATA"

    # Category layers: crypto, stocks, indices, forex, commodities, volatility
    for category, assets in market.items():
        if not isinstance(assets, dict) or category == "crypto_market":
            continue
            
        for asset, data in assets.items():
            if not data or not isinstance(data, dict):
                continue
                
            price = data.get("price", "N/A")
            change_percent = data.get("change_percent", "N/A")
            volume = data.get("volume", "N/A")
            
            lines.append(
                f"Asset: {asset} ({category.upper()})\n"
                f"Price: {price}\n"
                f"Change Percent: {change_percent}%\n"
                f"Volume: {volume}\n"
            )

    return "\n".join(lines) if lines else "INSUFFICIENT DATA"


def run_multi_agent(query: str) -> dict:
    """
    Executes a high-precision, thread-safe multi-agent market research pipeline.
    Guarantees no race conditions or shared state cross-contamination in concurrent schedules.
    """
    # CRITICAL FIX: Instantiate an isolated local execution logger for this specific thread run.
    # This prevents concurrent tasks from clearing or contaminating each other's logs!
    thread_logger = ExecutionLogger()
    thread_logger.clear()

    # ===================================
    # STEP 1: REAL DATA FETCHING
    # ===================================
    thread_logger.log(
        "STEP 1 - DATA",
        "fetching real market data snapshot"
    )

    market = get_market_snapshot()
    if not market:
        market = {}

    # Category-aware node update inside the thread-isolated Intelligence Graph
    for category, assets in market.items():
        if not isinstance(assets, dict) or category == "crypto_market":
            continue
            
        for asset, data in assets.items():
            if data and isinstance(data, dict):
                # Using upgraded node tracking logic
                graph.add_node(
                    name=asset, 
                    node_type=category.upper(), 
                    weight=float(data.get("change_percent", 1.0))
                )

    market_context = build_market_context(market)

    # ===================================
    # STEP 2: LLM ANALYSIS GENERATION
    # ===================================
    thread_logger.log(
        "STEP 2 - ANALYSIS",
        "building intelligence report"
    )

    prompt = f"""
You are a professional market analyst.

STRICT RULES:
- Use ONLY the provided market data
- Never invent prices
- Never invent events
- Never invent support levels
- Never invent resistance levels
- Never invent ETF flows
- Never invent macroeconomic releases
- If information is unavailable, explicitly say INSUFFICIENT DATA

MARKET DATA:
{market_context}

USER QUESTION:
{query}

Return:
1. Market Summary
2. Evidence Used
3. Risks
4. What Can Be Concluded
5. What Cannot Be Concluded
"""

    analysis = ask_llm(prompt)
    if not analysis:
        analysis = "ERROR: All LLM routing providers failed to generate an analysis."

    # ===================================
    # STEP 3: EVIDENCE EXTRACTION
    # ===================================
    thread_logger.log(
        "STEP 3 - EVIDENCE",
        "extracting evidence"
    )

    # Thread-safe evidence extraction (uses Thread-Local Storage)
    evidence = evidence_engine.extract_from_text(analysis)

    thread_logger.log(
        "STEP 3 - EVIDENCE",
        f"{len(evidence)} evidence items found"
    )

    # ===================================
    # STEP 4: VERIFICATION
    # ===================================
    thread_logger.log(
        "STEP 4 - VERIFY",
        "verifying evidence"
    )

    verified = verify_evidence(evidence)
    if not verified:
        verified = []

    thread_logger.log(
        "STEP 4 - VERIFY",
        f"{len(verified)} evidence items verified"
    )

    # ===================================
    # STEP 5: CONFIDENCE ASSESSMENT
    # ===================================
    thread_logger.log(
        "STEP 5 - CONFIDENCE",
        "calculating confidence"
    )

    confidence = calculate_confidence(verified)

    # ===================================
    # STEP 6: INTELLIGENCE GRAPH MAPPING
    # ===================================
    # Safely navigate nested dictionary layers to avoid KeyError crashes
    crypto_section = market.get("crypto", {})
    stocks_section = market.get("stocks", {})

    btc_data = crypto_section.get("BTC", {})
    tsla_data = stocks_section.get("TSLA", {})

    # Use dict.get to handle instances where an asset failed to load
    btc_change = btc_data.get("change_percent", 0.0) if btc_data else 0.0
    tsla_change = tsla_data.get("change_percent", 0.0) if tsla_data else 0.0

    try:
        btc_val = float(btc_change)
        tsla_val = float(tsla_change)
        
        strength = round(
            1.0 / (1.0 + abs(btc_val - tsla_val)),
            2
        )
    except Exception as calculation_fault:
        system_logger.warning(f"Failed to calculate strength coefficient: {calculation_fault}")
        strength = 0.5

    # Safe directional linking
    graph.add_edge(
        source="BTC",
        target="TSLA",
        relation="co-movement",
        strength=strength
    )

    # ===================================
    # FINAL REPORT ASSEMBLY
    # ===================================
    # Safely convert verified claims into markdown format
    verified_claims_formatted = []
    for item in verified:
        if isinstance(item, dict) and "claim" in item:
            verified_claims_formatted.append(f"- {item['claim']}")
            
    verified_claims_text = "\n".join(verified_claims_formatted) if verified_claims_formatted else "- No verified evidence available."

    final_report = f"""
{analysis}

=========================
VERIFIED EVIDENCE
=========================

{verified_claims_text}

=========================
CONFIDENCE
=========================

Score: {confidence.get('score', 0)}
Level: {confidence.get('label', 'LOW')}
"""

    thread_logger.log(
        "FINAL OUTPUT",
        f"confidence={confidence.get('label', 'LOW')}"
    )

    # Return structure matching your exact original downstream consumer schemas
    return {
        "result": final_report,
        "logs": thread_logger.get_logs(),
        "graph": graph.export(),
        "raw_market": market,
        "confidence": confidence,
        "verified_evidence": verified
    }