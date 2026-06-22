import re
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class AssetRouter:
    # Upgrade: Map the keyword to BOTH the Symbol and the Asset Class.
    # This tells your downstream agents which API to use (e.g., YFinance vs Crypto API)
    ASSETS: Dict[str, Tuple[str, str]] = {
        # CRYPTO
        "btc": ("BTC-USD", "crypto"),
        "bitcoin": ("BTC-USD", "crypto"),
        "eth": ("ETH-USD", "crypto"),
        "sol": ("SOL-USD", "crypto"),
        "solana": ("SOL-USD", "crypto"),

        # STOCKS
        "tesla": ("TSLA", "equity"),
        "tsla": ("TSLA", "equity"),
        "apple": ("AAPL", "equity"),
        "aapl": ("AAPL", "equity"),
        "meta": ("META", "equity"),
        "facebook": ("META", "equity"),

        # COMMODITIES
        "gold": ("GC=F", "commodity"),
        "silver": ("SI=F", "commodity"),
        "oil": ("CL=F", "commodity"),
    }

    def __init__(self):
        # Pre-compile regex patterns when the class initializes.
        # \b ensures we match exact words (e.g., "sol" but NOT "consolidation")
        self._compiled_patterns = {
            keyword: re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            for keyword in self.ASSETS.keys()
        }

    def detect_asset(self, query: str) -> Optional[Tuple[str, str]]:
        """
        Scans the query for known assets using exact word boundaries.
        Returns a tuple of (Symbol, Asset_Class) or None.
        """
        for keyword, pattern in self._compiled_patterns.items():
            if pattern.search(query):
                symbol, asset_class = self.ASSETS[keyword]
                logger.info(f"Asset routed: '{keyword}' -> {symbol} ({asset_class})")
                return symbol, asset_class
                
        # CRITICAL FIX: Never default to a random asset. 
        # If no asset is found, return None so the agent knows to ask for clarification 
        # or skip the technical analysis step.
        logger.warning(f"No valid asset detected in query: '{query}'")
        return None

asset_router = AssetRouter()