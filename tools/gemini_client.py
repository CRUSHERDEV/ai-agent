import logging

logger = logging.getLogger(__name__)

def ask_gemini(prompt):
    """
    FAIL-FAST Gemini wrapper.
    No retries. No sleep. No hiding failures.
    Enhanced with thread-safe operational telemetry tracking.
    """
    if not prompt:
        logger.warning("Invocation Aborted: Prompt payload passed to ask_gemini is empty.")
        return None

    # Track entry context to debug payload bottlenecks in multi-threaded runs
    logger.info(f"Initiating Gemini API call. Payload weight: {len(prompt)} characters.")
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        # Confirm the structural validity of the response object before stripping
        if response and hasattr(response, "text") and response.text:
            token_output = response.text.strip()
            logger.info(f"Gemini token generation successful. Received: {len(token_output)} characters.")
            return token_output

        # If we reach here, the API didn't throw an error but returned no text 
        # (commonly happens if a prompt hits safety blocks or generation limits)
        logger.error("Gemini API execution finished without text content. Possible content suppression or safety trigger.")
        return None

    except Exception as e:
        # ❌ NEVER retry here - Honor your explicit fail-fast structural logic
        # Log the complete traceback footprint to your logging engine immediately
        logger.error(f"Critical execution error during Gemini API dispatch: {e}", exc_info=True)
        raise e