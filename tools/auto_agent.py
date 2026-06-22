import schedule
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from tools.research_engine import research

# Setup institutional logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("auto_agent_system.log", mode="a")
    ]
)
logger = logging.getLogger("AutoAgent")

# Topics your AI will monitor automatically
TOPICS = [
    "AI startups",
    "robotics companies",
    "African fintech trends",
]

def execute_single_topic_research(topic: str):
    """Worker task executed inside the thread pool to avoid blocking other operations."""
    logger.info(f"Starting background research execution for topic: '{topic}'")
    try:
        # Calls your unaltered internal logic
        result = research(topic)
        
        # Structure the terminal print cleanly without interfering with logs
        print(f"\n==================== [RESULT FOR: {topic.upper()}] ====================")
        print(result)
        print("========================================================================\n")
        
    except Exception as e:
        logger.error(f"Execution failure on topic '{topic}': {e}", exc_info=True)

def run_daily_research():
    logger.info("Auto Research Triggered. Initializing worker threads...")
    
    # Run the topic research concurrently so they don't block one another
    # max_workers=3 means all 3 topics are analyzed at the exact same moment
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="ResearchWorker") as executor:
        executor.map(execute_single_topic_research, TOPICS)
        
    logger.info("All scheduled research tasks completed for this session.")

# Schedule (every 1 hour for testing)
schedule.every(1).hours.do(run_daily_research)

logger.info("Autonomous Research Agent successfully started. Listening in background...")

# The resilient execution loop
try:
    while True:
        schedule.run_pending()
        time.sleep(1) # Reduced to 1 second for higher tracking precision
except KeyboardInterrupt:
    logger.info("System shutdown signal received via user keyboard interrupt. Exiting safely.")
except Exception as system_fault:
    logger.critical(f"Fatal scheduler crash: {system_fault}", exc_info=True)