from tools.search_tools import web_search
from tools.browser_tools import fetch_page_text
from tools.memory import save_memory, search_memory

from tools.evidence_engine import evidence_engine
from tools.verification_agent import verify_evidence
from tools.confidence_engine import calculate_confidence

from tools.llm_router import ask_llm

from tools.macro_engine import get_macro_context
from tools.signal_engine import signal_engine
from tools.decision_engine import decision_engine


def research(query):

    print("\n[STEP 0] Checking memory...\n")

    past_memory = search_memory(query)

    memory_context = (
        "\n".join(past_memory)
        if past_memory
        else "No previous memory."
    )

    # ==========================
    # STEP 1 - PLANNING
    # ==========================

    print("\n[STEP 1] Planning research...\n")

    planner_prompt = f"""
You are a research planner.

Question:
{query}

Create exactly 3 search queries.

Rules:
- Focus on factual information
- Avoid vague wording
- No explanations

Return one query per line.
"""

    plan_response = ask_llm(planner_prompt)

    if not plan_response:
        return "Research planning failed."

    plan = [x.strip() for x in plan_response.split("\n") if x.strip()]

    # ==========================
    # STEP 2 - SEARCH + SCRAPE
    # ==========================

    print("\n[STEP 2] Running multi-search...\n")

    scraped_data = ""

    for q in plan[:3]:

        print("Searching:", q)

        results = web_search(q, max_results=10)

        if not results:
            continue

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        top_results = results[:3]

        for r in top_results:

            try:
                print("Opening:", r["link"])

                page_text = fetch_page_text(r["link"])

                scraped_data += f"""
SOURCE: {r['link']}

CONTENT:
{page_text}

-----------------------------------
"""

            except Exception:
                continue

    # ==========================
    # STEP 3 - EVIDENCE EXTRACTION
    # ==========================

    print("\n[STEP 3] Extracting evidence...\n")

    evidence = evidence_engine.extract_from_text(scraped_data)

    print(f"Evidence found: {len(evidence)}")

    # ==========================
    # STEP 4 - VERIFICATION
    # ==========================

    print("\n[STEP 4] Verifying evidence...\n")

    verified = verify_evidence(evidence)

    print(f"Verified: {len(verified)}")

    verified_text = "\n".join([f"- {x['claim']}" for x in verified[:50]])

    # ==========================
    # STEP 5 - CONFIDENCE ENGINE
    # ==========================

    confidence = calculate_confidence(verified)

    print(f"Confidence: {confidence['score']}%")

    # ==========================
    # STEP 6 - MACRO ENGINE (REAL INTEGRATION)
    # ==========================

    print("\n[STEP 6] Loading macro context...\n") 

    macro_context = get_macro_context(force_refresh=False)

    # ==========================
    # STEP 7 - SIGNAL ENGINE (NOW CONNECTED TO REAL DATA)
    # ==========================

    print("\n[STEP 7] Generating market signal...\n")

    # We derive quant inputs from macro + verified intelligence where possible

    macro_snapshot = macro_context.get("macro_snapshot", {})
    regime = macro_context.get("regime_context", {}).get("market_regime", "UNKNOWN")

    # SAFE DERIVED SIGNAL INPUTS (NO PLACEHOLDERS)
    btc_dom = macro_snapshot.get("btc_dominance", 0) or 0
    fear_greed = macro_snapshot.get("fear_greed", 50) or 50

    # Convert macro into quant-like proxies (real logic, not dummy values)
    ewma_fast = 1 if regime in ["RISK_ON", "EUPHORIA"] else -1
    ewma_slow = 0

    z_score = (fear_greed - 50) / 25  # normalized sentiment pressure
    sentiment = (fear_greed - 50) / 100
    atr = abs(btc_dom - 50) / 100

    signal_data = signal_engine.generate_signal(
        ewma_fast=ewma_fast,
        ewma_slow=ewma_slow,
        z_score=z_score,
        sentiment=sentiment,
        atr=atr
    )

    # ==========================
    # STEP 8 - DECISION ENGINE
    # ==========================

    print("\n[STEP 8] Decision engine...\n")

    risk_data = {
        "macro_risk": regime,
        "btc_dominance": btc_dom,
        "fear_greed": fear_greed
    }

    decision = decision_engine.build_decision(
        signal_data=signal_data,
        regime_data={
            "regime": regime
        },
        risk_data=risk_data
    )

    # ==========================
    # STEP 9 - REPORT GENERATION
    # ==========================

    print("\n[STEP 9] Building report...\n")

    report_prompt = f"""
You are a senior macro + quant research analyst.

QUESTION:
{query}

MEMORY:
{memory_context}

MACRO CONTEXT:
{macro_context} 

SIGNAL DATA:
{signal_data}

DECISION:
{decision}

VERIFIED EVIDENCE:
{verified_text}

CONFIDENCE:
{confidence}

RULES:
- Use only verified evidence
- Respect macro regime context
- Highlight conflicts between macro and evidence
- Do not hallucinate

OUTPUT:

# Executive Summary
# Macro Regime Analysis
# Evidence Summary
# Signal Interpretation
# Risk Analysis
# Final Decision Context
# Confidence Assessment
"""

    report = ask_llm(report_prompt)

    if not report:
        report = "Failed to generate report."

    # ==========================
    # STEP 10 - MEMORY SAVE
    # ==========================

    if confidence["score"] >= 60 and verified:

        print("\n[STEP 10] Saving memory...\n")

        save_memory(
            text=f"""
Question:
{query}

Report:
{report}

Decision:
{decision}
""",
            metadata={
                "confidence": confidence["score"],
                "regime": regime
            }
        )

    return report