import logging
import threading
from tools.gemini_client import ask_gemini
from tools.groq_client import ask_groq

# Setup institutional logging format
logger = logging.getLogger(__name__)

class LLMRouter:

    def __init__(self):
        self.gemini_disabled = False
        # Thread lock guarantees atomic read/write states and clean, un-garbled console outputs
        self._lock = threading.Lock()

    def ask_llm(self, prompt):
        # Thread-safe read of the disabled state
        with self._lock:
            is_gemini_active = not self.gemini_disabled

        # ==========================
        # TRY GEMINI ONLY IF ACTIVE
        # ==========================
        if is_gemini_active:
            try:
                # Thread-safe output presentation
                logger.info("LLM Router dispatching primary request to Gemini...")
                print("\n[LLM ROUTER] Trying Gemini...\n")

                result = ask_gemini(prompt)
                
                if result is not None:
                    return result
                
                # If ask_gemini returned None (e.g. safety blocks), treat as a soft failure
                raise ValueError("Gemini returned an empty response.")

            except Exception as e:
                err = str(e)
                
                with self._lock:
                    # 🚨 HARD STOP CONDITION: Check if this was a rate limit or quota exclusion
                    if "RESOURCE_EXHAUSTED" in err or "429" in err:
                        if not self.gemini_disabled:
                            logger.critical(f"Gemini quota hit ({err}) → DISABLING Gemini permanently for this session.")
                            print("\n[LLM ROUTER] Gemini quota hit → DISABLING Gemini permanently.\n")
                            self.gemini_disabled = True
                    else:
                        logger.warning(f"Gemini request failed: {err}. Routing fallback to Groq.")
                        print("\n[LLM ROUTER] Gemini failed (unknown error). Switching to Groq.\n")

                # IMMEDIATE FALLBACK
                return self.ask_groq(prompt)

        # ==========================
        # DIRECT GROQ PATH
        # ==========================
        return self.ask_groq(prompt)

    def ask_groq(self, prompt):
        logger.info("LLM Router dispatching request to Groq...")
        print("\n[LLM ROUTER] Trying Groq...\n")

        try:
            result = ask_groq(prompt)
            if result is not None:
                return result
            raise ValueError("Groq returned an empty response.")

        except Exception as e:
            logger.error(f"Groq primary fallback execution failed: {e}", exc_info=True)
            print(f"\n[LLM ROUTER] Groq failed: {e}\n")
            return "All LLM providers failed."


# Global Singleton instance mapping back perfectly to your existing architecture
router = LLMRouter()


def ask_llm(prompt):
    """Global wrapper function mimicking the system's execution pipeline."""
    return router.ask_llm(prompt)