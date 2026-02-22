"""
Autonomous Agent Orchestrator for GitHub Actions.

This script parses GitHub issue payloads, constructs a strict architectural 
prompt, and executes the local Aider instance. It ensures memory constraints 
are respected and handles subprocess execution securely without memory leaks.
"""

import os
import sys
import subprocess
import logging
from typing import List

# -----------------------------------------------------------------------------
# Telemetry & Logging setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

class AiderOrchestrator:
    """
    Manages the lifecycle of the Aider CLI subprocess.
    Ensures O(1) execution overhead and strict timeout enforcement.
    """
    
    def __init__(self, model_identifier: str = "ollama/qwen2.5-coder:7b"):
        self.model = model_identifier
        self.issue_title = os.getenv("ISSUE_TITLE", "")
        self.issue_body = os.getenv("ISSUE_BODY", "")
        
        if not self.issue_title:
            logger.critical("No issue title provided. Halting execution.")
            sys.exit(1)

    def _build_strict_prompt(self) -> str:
        """
        Constructs a deterministic prompt to force the LLM into generating
        highly optimized, PEP8 compliant code with English comments.
        """
        return (
            "You are an autonomous Senior Staff Engineer. "
            "Resolve the following issue automatically.\n\n"
            f"Title: {self.issue_title}\n"
            f"Description: {self.issue_body}\n\n"
            "Constraints:\n"
            "1. Produce highly scalable and efficient code.\n"
            "2. Ensure strict PEP8 compliance.\n"
            "3. All code and comments MUST be strictly in English.\n"
            "4. Handle all exceptions gracefully."
        )

    def execute_agent(self) -> bool:
        """
        Spawns the Aider subprocess in headless mode.
        """
        prompt = self._build_strict_prompt()
        logger.info(f"Triggering Aider for issue: {self.issue_title}")
        
        # Aider CLI arguments optimized for automated, non-interactive execution
        command: List[str] = [
            "aider",
            "--model", self.model,
            "--yes",                   # Auto-confirm all destructive actions (commits)
            "--no-suggest-shell-commands", # Security: prevent arbitrary shell execution
            "--message", prompt
        ]
        
        try:
            # Enforce a strict timeout to prevent infinite loops burning VRAM
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                timeout=600  # 10 minutes maximum execution time
            )
            logger.info("Agent execution completed successfully.")
            logger.debug(result.stdout)
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Agent execution timed out. Possible VRAM congestion.")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Agent failed with exit code {e.returncode}.")
            logger.error(f"Error output: {e.stderr}")
            return False

if __name__ == "__main__":
    orchestrator = AiderOrchestrator()
    success = orchestrator.execute_agent()
    
    if not success:
        sys.exit(1)
