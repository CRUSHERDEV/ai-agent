import os
import sys
import logging
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# Initialize basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("ModelDiscovery")

# Load environment configuration
load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.critical("Initialization Failed: 'GEMINI_API_KEY' environment variable is missing from your .env file.")
        sys.exit(1)
        
    logger.info("Connecting to Google GenAI API platform...")
    
    try:
        # Instantiate the official new google-genai client
        client = genai.Client(api_key=api_key)
        
        # Pull active models mapped to your credential permissions
        models = client.models.list()
        
        print("\n==================================================")
        print("   VERIFIED ACTIVE GEMINI MODELS FOR YOUR API KEY  ")
        print("==================================================\n")
        
        count = 0
        for m in models:
            # Format output beautifully showing name and supported capabilities
            capabilities = []
            if hasattr(m, "supported_actions"):
                capabilities = [action.split("/")[-1] for action in m.supported_actions]
                
            print(f"🔹 Model ID:      {m.name}")
            if capabilities:
                print(f"   Capabilities:  {', '.join(capabilities)}")
            print("-" * 50)
            count += 1
            
        print(f"\n[SUCCESS] Discovery complete. Found {count} active models matching your API tier.")
        print("==================================================\n")

    except APIError as api_err:
        logger.error(f"Google GenAI API Authentication or Connection error: {api_err.message} (Status Code: {api_err.code})")
    except Exception as e:
        logger.error(f"An unexpected system fault occurred during model discovery: {e}", exc_info=True)

if __name__ == "__main__":
    list_available_models()