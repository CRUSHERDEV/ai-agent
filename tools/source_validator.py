TRUSTED_SOURCES = {
    "reuters.com": 10,
    "bloomberg.com": 10,
    "wsj.com": 10,
    "cnbc.com": 9,
    "finance.yahoo.com": 8,
    "fxstreet.com": 8,
    "investing.com": 8,
    "tradingview.com": 7
}


def get_source_score(url):

    for source, score in TRUSTED_SOURCES.items():

        if source in url:
            return score

    return 1


def classify_source(url):

    score = get_source_score(url)

    if score >= 9:
        return "Tier 1"

    if score >= 7:
        return "Tier 2"

    return "Tier 3"