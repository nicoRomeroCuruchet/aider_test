"""
Scalable Agent Orchestrator for Aider.
Strictly adheres to PEP8 and uses absolute paths for reliability.
All comments and documentation are in English as requested[cite: 2, 4].
"""

import os
import sys
import subprocess
import logging
from typing import List

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

class AiderOrchestrator:
    """
    Manages the Aider CLI lifecycle in a headless environment.
    """
    
    def __init__(self, model_identifier: str = "ollama/qwen2.5-coder:7b"):
        self.model = model_identifier
        self.issue_title = os.getenv("ISSUE_TITLE", "")
        self.issue_body = os.getenv("ISSUE_BODY", "")
        # Get absolute path from environment variable set in YAML
        self.aider_bin = os.getenv("AIDER_BIN", "aider")
        
        if not self.issue_title:
            logger.critical("No issue title found in environment variables.")
            sys.exit(1)

    def _generate_prompt(self) -> str:
        """Constructs the engineering-focused prompt for the LLM."""
        return (
            f"Fix the following issue.\nTitle: {self.issue_title}\n"
            f"Description: {self.issue_body}\n\n"
            "Technical Requirements:\n"
            "- Implement highly efficient, memory-optimized solutions.\n"
            "- Ensure strict PEP8 compliance.\n"
            "- All code and comments MUST be in English[cite: 2, 4].\n"
            "- Refactor for scalability and concurrency."
        )

    def run(self) -> bool:
        """Executes the Aider process using the absolute binary path."""
        prompt = self._generate_prompt()
        
        command: List[str] = [
            self.aider_bin,
            "--model", self.model,
            "--yes",
            "--no-suggest-shell-commands",
            "--message", prompt
        ]
        
        try:
            # Execute with a 10-minute timeout for the 3070 to process 
            subprocess.run(command, check=True, timeout=600)
            logger.info("Aider task completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Aider failed with exit code: {e.returncode}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False

if __name__ == "__main__":
    orchestrator = AiderOrchestrator()
    if not orchestrator.run():
        sys.exit(1)
