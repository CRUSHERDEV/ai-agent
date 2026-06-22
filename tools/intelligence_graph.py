from collections import defaultdict
import json
import threading
import logging
import re

logger = logging.getLogger(__name__)


class IntelligenceGraph:
    """
    Thread-safe intelligence graph for building entity relationships
    from LLM-extracted financial/market data.
    """

    def __init__(self):
        # Thread-local storage prevents cross-request graph pollution
        self._thread_isolated_state = threading.local()

    # -----------------------------
    # Nodes (entities)
    # -----------------------------
    @property
    def nodes(self) -> dict:
        if not hasattr(self._thread_isolated_state, "graph_nodes"):
            self._thread_isolated_state.graph_nodes = {}
        return self._thread_isolated_state.graph_nodes

    # -----------------------------
    # Edges (relationships)
    # -----------------------------
    @property
    def edges(self) -> defaultdict:
        if not hasattr(self._thread_isolated_state, "graph_edges"):
            self._thread_isolated_state.graph_edges = defaultdict(list)
        return self._thread_isolated_state.graph_edges

    # -----------------------------
    # Add node
    # -----------------------------
    def add_node(self, name, node_type="entity", weight=1.0):
        if not name:
            return

        normalized_name = str(name).strip().upper()

        self.nodes[normalized_name] = {
            "type": node_type,
            "weight": float(weight)
        }

    # -----------------------------
    # Add edge
    # -----------------------------
    def add_edge(self, source, target, relation, strength=1.0):
        if not source or not target:
            return

        src = str(source).strip().upper()
        tgt = str(target).strip().upper()

        self.edges[src].append({
            "target": tgt,
            "relation": str(relation).strip(),
            "strength": float(strength)
        })

    # -----------------------------
    # Clean LLM output safely
    # -----------------------------
    def _clean_llm_output(self, text: str) -> str:
        if not text:
            return ""

        cleaned = text.strip()

        # Remove markdown code fences
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned)
            cleaned = cleaned.replace("```", "").strip()

        return cleaned

    # -----------------------------
    # Extract relationships via LLM
    # -----------------------------
    def extract_relationships(self, text, ask_ll):
        """
        Extract structured relationships using LLM callback.
        Returns list of relationship dicts and updates graph.
        """

        if not text or not ask_ll:
            return []

        prompt = f"""
Extract financial relationships from the text below.

Return ONLY valid JSON array:

[
  {{
    "source": "USD",
    "target": "GBPUSD",
    "relation": "strengthens",
    "strength": 0.8
  }}
]

Rules:
- Output ONLY JSON
- No explanation
- No markdown

Text:
{text}
"""

        try:
            result = ask_ll(prompt)

            if not result:
                return []

            cleaned_result = self._clean_llm_output(result)

            # -----------------------------
            # Parse JSON safely
            # -----------------------------
            data = json.loads(cleaned_result)

            if not isinstance(data, list):
                return []

            relationships = []

            for item in data:
                if not isinstance(item, dict):
                    continue

                if not all(k in item for k in ("source", "target", "relation")):
                    continue

                source = item["source"]
                target = item["target"]
                relation = item["relation"]
                strength = item.get("strength", 1.0)

                relationships.append(item)

                # Build graph
                self.add_node(source)
                self.add_node(target)

                self.add_edge(source, target, relation, strength)

            return relationships

        except json.JSONDecodeError as e:
            logger.error(f"[IntelligenceGraph] JSON decode error: {e}")
            return []

        except Exception as e:
            logger.error(f"[IntelligenceGraph] Unexpected error: {e}")
            return []