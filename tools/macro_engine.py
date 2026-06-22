import time
import logging
import threading
from tools.market_data import (
    get_market_snapshot,
    compute_market_regime
)

# Initialize institutional logging framework
logger = logging.getLogger(__name__)

# Thread-safe global caching parameters
_cache_lock = threading.Lock()
_macro_cache = None
_last_fetch_time = 0.0

# Define Cache Time-To-Live (TTL) -- e.g., 5 minutes (300 seconds)
# Macro trends do not fluctuate on a millisecond scale; caching protects your APIs.
CACHE_TTL_SECONDS = 300.0

def get_macro_context(force_refresh=False):
    """
    Retrieves the macro context snapshot and market regime.
    Implements a thread-safe caching system to prevent redundant API queries.
    """
    global _macro_cache, _last_fetch_time
    
    current_time = time.time()
    
    # 1. Thread-safe cached check block
    with _cache_lock:
        if not force_refresh and _macro_cache is not None:
            time_elapsed = current_time - _last_fetch_time
            if time_elapsed < CACHE_TTL_SECONDS:
                logger.debug(f"Returning cached macro context. Cache age: {time_elapsed:.1f}s / {CACHE_TTL_SECONDS}s.")
                return _macro_cache

        logger.info("Macro cache expired, empty, or refresh was explicitly forced. Querying live market feeds...")
        
        try:
            # 2. Invoke live data-fetch wrappers safely
            snapshot = get_market_snapshot()
            if not snapshot:
                logger.warning("Market data snapshot returned an empty payload. Utilizing empty baseline dictionary.")
                snapshot = {}
                
            regime = compute_market_regime(snapshot)
            if not regime:
                logger.warning("Market regime calculation failed. Falling back to neutral baseline structure.")
                regime = {
                    "regime": "NEUTRAL",
                    "score": 0.0,
                    "assets_analyzed": 0
                }
                
        except Exception as query_fault:
            logger.error(f"Failed to query macro and market data feeds: {query_fault}", exc_info=True)
            # Safe structural fallback to prevent crashing the executing background thread
            snapshot = {}
            regime = {
                "regime": "NEUTRAL",
                "score": 0.0,
                "assets_analyzed": 0
            }

        # 3. Defensive Extraction Layer
        crypto_market = snapshot.get("crypto_market", {})
        
        # Self-healing parameters: If fear_greed is supplied in the snapshot (or scraped), 
        # use it; otherwise, fall back safely to 50 instead of hardcoding it.
        fear_greed = crypto_market.get("fear_greed", snapshot.get("fear_greed", 50))
        
        btc_dom = crypto_market.get("btc_dominance", 50)

        # 4. Construct complete, safe output payload matching exact original keys
        result = {
            "macro_snapshot": {
                "btc_dominance": btc_dom,
                "fear_greed": fear_greed,
                "market_cap": crypto_market.get("total_market_cap", 0),
                "volume": crypto_market.get("total_volume", 0)
            },
            "regime_context": {
                "market_regime": regime.get("regime", "NEUTRAL"),
                "regime_score": regime.get("score", 0.0),
                "assets_analyzed": regime.get("assets_analyzed", 0)
            }
        }

        # Update global cache state atomically
        _macro_cache = result
        _last_fetch_time = current_time
        
        logger.info(f"Macro context successfully synchronized. Regime classified as: {result['regime_context']['market_regime']}")
        return result