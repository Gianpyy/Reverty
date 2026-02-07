from agents.agent import Agent
from typing import Dict, Any
from helpers.system_prompts import EVALUATOR_SYSTEM_PROMPT
from config import MAX_EVALUATION_RETRIES
import json


class EvaluatorAgent(Agent):
    """
    Evaluator Agent: Uses LLM to evaluate the complexity of a user prompt
    to create an adequate contract for the requested code.
    """

    def evaluate_request(self, user_prompt: str) -> int:
        """
        Evaluates the complexity of a user prompt to create an adequate contract for the requested code.
        """
        print(f"[Evaluator Agent] Evaluating request: '{user_prompt}'...")

        response: str = self._make_request(user_prompt)

        # Try to parse response
        try:
            evaluation: Dict[str, Any] = self.extract_response(response)

            # Retry for bad response
            i = 0
            while not isinstance(evaluation.get("complexity"), int) and i < MAX_EVALUATION_RETRIES:
                i += 1
                response: str = self._make_request(user_prompt)
                evaluation: Dict[str, Any] = self.extract_response(response)

            if not isinstance(evaluation.get("complexity"), int):
                return 5  # Default complexity

            return evaluation["complexity"]
        except json.JSONDecodeError as e:
            print(f"[Evaluator Agent] Error decoding JSON: {e}")
            print(f"[Evaluator Agent] Response was: {response[:200]}")
            return 5 # Default complexity


    def _make_request(self, user_prompt: str) -> str:
        """
        Makes a request to the LLM client to evaluate the complexity of a user prompt.
        """
        return self.client.generate(
            user_prompt=user_prompt,
            system_prompt=EVALUATOR_SYSTEM_PROMPT
        )
