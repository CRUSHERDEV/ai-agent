from ddgs import DDGS
from datetime import datetime

from tools.source_validator import (
    get_source_score,
    classify_source
)

# Trusted finance/news sources
TRUSTED_SOURCES = [
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
    "cnbc.com",
    "finance.yahoo.com",
    "fxstreet.com",
    "investing.com",
    "tradingview.com"
]


def is_trusted(url):

    for domain in TRUSTED_SOURCES:

        if domain in url:
            return True

    return False


def web_search(query, max_results=10):

    results_data = []

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                max_results=max_results
            )

            for r in results:

                try:

                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")

                    trusted = is_trusted(url)

                    score = get_source_score(url)
                    tier = classify_source(url)

                    result = {
                        "title": title,
                        "link": url,
                        "snippet": body,
                        "trusted": trusted,
                        "score": score,
                        "tier": tier,
                        "timestamp": str(datetime.now())
                    }

                    results_data.append(result)

                except Exception:
                    continue

        # Sort by source quality score
        results_data.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results_data

    except Exception as e:

        print(f"\n[SEARCH ERROR] {e}")

        return []