from tools.intelligence_graph import IntelligenceGraph

graph = IntelligenceGraph()

from dotenv import load_dotenv
import os

from tools.research_engine import research

load_dotenv()

print("\n===================================")
print(" AUTONOMOUS AI RESEARCH AGENT ")
print("===================================\n")

print("Type 'exit' to stop.\n")

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Agent stopped.")
        break

    try:
        answer = research(user_input)
        print("\nAI RESPONSE:\n")
        print(answer)

    except Exception as e:
        print("\nERROR:", e)

    print("\n" + "=" * 60 + "\n")