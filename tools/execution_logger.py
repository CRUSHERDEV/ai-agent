import time
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExecutionLogger:
    def __init__(self):
        # Thread-Local Storage isolates log lines so concurrent agent jobs
        # do not mix up their operational timelines or clear each other's traces.
        self._thread_isolated_state = threading.local()

    @property
    def steps(self) -> list:
        """Dynamically fetch or initialize the log array unique to the executing thread."""
        if not hasattr(self._thread_isolated_state, "log_steps"):
            self._thread_isolated_state.log_steps = []
        return self._thread_isolated_state.log_steps

    @steps.setter
    def steps(self, value: list):
        self._thread_isolated_state.log_steps = value

    def log(self, step: str, message: str):
        raw_timestamp = time.time()
        
        # Preserves your exact required dictionary payload structure
        entry = {
            "step": step,
            "message": message,
            "timestamp": raw_timestamp
        }
        
        # Create a clean human-readable timestamp string for standard outputs
        human_time = datetime.fromtimestamp(raw_timestamp).strftime('%H:%M:%S')
        
        # Route to your application's logging framework (records to your log file)
        logger.info(f"[{step}] {message}")
        
        # Clear stdout printing that maps perfectly back to your monitoring terminal
        print(f"[{human_time}] [{step}] {message}")
        
        self.steps.append(entry)

    def get_logs(self) -> list:
        return self.steps

    def clear(self):
        self.steps = []