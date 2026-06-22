# tools/verification_agent.py

from tools.llm_router import ask_llm


def verify_evidence(evidence):

    if not evidence:
        return []

    claims = []

    for i, item in enumerate(evidence):
        claims.append(
            f"{i}| {item['claim']}"
        )

    prompt = f"""
You are a professional fact verification engine.

Review the claims below.

For each claim return:

VERIFIED:<index>

or

REJECT:<index>

Rules:

- Keep factual claims.
- Reject opinions.
- Reject speculation.
- Reject unsupported statements.
- Output ONLY decisions.

CLAIMS:

{chr(10).join(claims)}
"""

    result = ask_llm(prompt)

    verified_indexes = set()

    for line in result.splitlines():

        line = line.strip()

        if line.startswith("VERIFIED:"):

            try:
                idx = int(
                    line.replace(
                        "VERIFIED:",
                        ""
                    ).strip()
                )

                verified_indexes.add(idx)

            except:
                pass

    verified = []

    for i, item in enumerate(evidence):

        if i in verified_indexes:
            verified.append(item)

    return verified