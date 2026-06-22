import re
import threading
import logging

logger = logging.getLogger(__name__)

class EvidenceEngine:

    def __init__(self):
        # Thread-Local Storage isolation prevents concurrent tasks from
        # polluting or overwriting each other's research datasets.
        self._thread_isolated_state = threading.local()

    @property
    def evidence(self) -> list:
        """Dynamically fetch or initialize the array unique to the executing thread."""
        if not hasattr(self._thread_isolated_state, "data"):
            self._thread_isolated_state.data = []
        return self._thread_isolated_state.data

    @evidence.setter
    def evidence(self, value: list):
        self._thread_isolated_state.data = value

    def clear(self):
        self.evidence = []

    def add_evidence(
        self,
        claim: str,
        source="Research Agent",
        confidence=0.5
    ):
        self.evidence.append(
            {
                "claim": claim,
                "source": source,
                "confidence": confidence
            }
        )

    def extract_from_text(self, text: str):
        self.clear()
        
        if not text:
            return self.evidence

        # High-precision UI filter to drop operational website trash
        junk_indicators = [
            r"terms of service", r"privacy policy", r"cookie settings", 
            r"all rights reserved", r"click here", r"subscribe to", 
            r"login", r"create an account", r"forgot password"
        ]
        junk_pattern = re.compile("|".join(junk_indicators), re.IGNORECASE)

        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # Pass-through validations
            if len(line) < 20:
                continue
                
            if junk_pattern.search(line):
                continue

            # ========================================================
            # CORE ALIGNMENT METRICS (Preserved Mathematical Engine)
            # ========================================================
            score = 0.5

            if re.search(r"\d", line):
                score += 0.2

            if "%" in line:
                score += 0.1

            if "$" in line:
                score += 0.1

            self.add_evidence(
                claim=line,
                confidence=min(score, 1.0)
            )

        logger.info(f"Thread-isolated extraction complete. Extracted sentences: {len(self.evidence)}")
        return self.evidence

    def get_all(self):
        return self.evidence


# Globally exposed instantiation mapping back perfectly to system components
evidence_engine = EvidenceEngine()