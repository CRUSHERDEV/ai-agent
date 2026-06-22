from tools.llm_router import ask_llm

prices = [
    100,
    101,
    102,
    104,
    106,
    108,
    110,
    111,
    113,
    115,
    117,
    119,
    121,
    122,
    124,
    126,
    127,
    128,
    130,
    132,
]

print(
    "EWMA:",
    quant_engine.ewma(prices)
)

print(
    "ZScore:",
    quant_engine.z_score(prices)
)

print(
    "Sentiment:",
    quant_engine.normalize_sentiment(
        4.2
    )
)

print(
    "Position Size:",
    quant_engine.position_size(
        equity=10000,
        risk_percent=1,
        atr=500
    )
)