import os
import logging
from groq import Groq
from dotenv import load_dotenv

# Initialize institutional logging framework
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

client = None

if API_KEY:
    # Set an explicit timeout on the client wrapper level (e.g., 20 seconds) 
    # to guarantee that a hung connection never traps an execution thread.
    client = Groq(
        api_key=API_KEY,
        timeout=20.0
    )
else:
    logger.critical("Groq Client Initialization Failed: 'GROQ_API_KEY' environment variable is missing.")


def ask_groq(prompt):
    if not prompt:
        logger.warning("Invocation Aborted: Prompt payload passed to ask_groq is empty.")
        return None

    if not client:
        logger.error("Execution Refused: Groq client is uninitialized due to a missing API key.")
        return None

    logger.info(f"Initiating Groq API dispatch utilizing model '{MODEL}'. Payload: {len(prompt)} characters.")

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        # Defensive Structure Checks: Safely unpack response tree layers
        if not completion or not hasattr(completion, "choices") or not completion.choices:
            logger.error("Groq API Execution anomaly: Server returned an empty or malformed choice block payload.")
            return None

        message_node = completion.choices[0].message
        if message_node and hasattr(message_node, "content") and message_node.content:
            token_output = message_node.content.strip()
            logger.info(f"Groq recovery token generation successful. Received: {len(token_output)} characters.")
            return token_output

        logger.warning("Groq API response executed but text content block is blank.")
        return None

    except Exception as e:
        # Replaced the raw multi-thread unsafe print statement with structured logger tracking
        logger.error(f"Critical execution error during Groq API fallback routing: {e}", exc_info=True)
        return None