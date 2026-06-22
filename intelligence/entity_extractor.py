import json


def extract_entities(text, ask_gemini):

    prompt = f"""
You are a financial intelligence extractor.

Extract all important entities from this text.

Examples:

Federal Reserve
Bank of England
GBPUSD
EURUSD
Gold
Oil
Bitcoin
Nvidia
Tesla
Inflation
Interest Rates

Return ONLY JSON.

Example:

[
    "Federal Reserve",
    "USD",
    "GBPUSD",
    "Inflation"
]

TEXT:

{text}
"""

    response = ask_gemini(prompt)

    try:
        return json.loads(response)
    except:
        return []