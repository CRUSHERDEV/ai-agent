from tools.intelligence_graph import IntelligenceGraph
from tools.llm_router import ask_llm
graph = IntelligenceGraph()

text = """
Federal Reserve signals higher rates.
USD strengthens.
GBPUSD falls.
Gold weakens.
"""

relations = graph.ingest_analysis(
    text,
    ask_gemini
)

print(relations)
print(graph.export())