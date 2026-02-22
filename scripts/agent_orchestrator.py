"""
Scalable Agent Orchestrator for Aider execution.
Strictly adheres to PEP8 and high-performance standards.
Uses absolute paths provided by the environment for maximum reliability.
"""
import os
import sys
import subprocess
import logging
from typing import List

# -----------------------------------------------------------------------------
# Telemetry Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


class AiderOrchestrator:
    """
    Manages the lifecycle of an autonomous Aider agent session.
    """

    def __init__(self, model: str = "ollama/qwen2.5-coder:7b"):
        self.model = model
        self.issue_title = os.getenv("ISSUE_TITLE", "")
        self.issue_body = os.getenv("ISSUE_BODY", "")
        self.aider_bin = os.getenv("AIDER_BIN", "/home/nromero/.local/bin/aider")

        if not self.issue_title:
            logger.critical("ISSUE_TITLE environment variable is missing.")
            sys.exit(1)

        if not os.path.isfile(self.aider_bin):
            logger.critical(f"Aider binary not found at: {self.aider_bin}")
            sys.exit(1)

    def _prepare_prompt(self) -> str:
        """Constructs the engineering-grade prompt for the model."""
        return (
            f"Fix the following issue.\n\nTitle: {self.issue_title}\n"
            f"Description: {self.issue_body}\n\n"
            "Requirements:\n"
            "- Fix blocking concurrency in ThreadPoolExecutor.\n"
            "- Implement requests.Session() for efficiency.\n"
            "- Ensure strict PEP8 compliance and O(1) memory usage.\n"
            "- All documentation and comments MUST be in English."
        )

    def run_agent(self) -> bool:
        """Spawns the Aider subprocess in headless mode."""
        prompt = self._prepare_prompt()

        cmd: List[str] = [
            self.aider_bin,
            "--model", self.model,
            "--yes",
            "--message", prompt
        ]

        try:
            logger.info(f"Starting Aider session for issue: {self.issue_title}")
            logger.info(f"Using Aider binary: {self.aider_bin}")
            subprocess.run(cmd, check=True, timeout=600)
            logger.info("Aider session completed and changes committed.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Aider failed with exit code {e.returncode}.")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Aider session timed out after 600 seconds.")
            return False
        except Exception as e:
            logger.error(f"An unexpected infrastructure error occurred: {e}")
            return False


if __name__ == "__main__":
    orchestrator = AiderOrchestrator()
    if not orchestrator.run_agent():
        sys.exit(1)
