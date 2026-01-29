import json
from typing import Dict, Any
from agents.agent import Agent
from helpers.prompt_generator import generate_architect_request
from helpers.system_prompts import ARCHITECT_SYSTEM_PROMPT


class ArchitectAgent(Agent):
    """
    Architect Agent: Contract Designer.
    Uses LLM to generate a contract from a user prompt.
    """

    def create_contract(self, user_prompt: str) -> Dict[str, Any]:
        """
        Creates a formal contract/specification for the requested code.
        """

        print(f"[Architect Agent] Designing contract for: '{user_prompt}'...")
        request = generate_architect_request(user_prompt)
        response = self.client.generate(
            user_prompt = request,
            system_prompt = ARCHITECT_SYSTEM_PROMPT
        )

        # Try to parse JSON
        try:
            contract = self._extract_json(response)
            return contract
        except json.JSONDecodeError as e:
            print(f"[Architect Agent] Error decoding JSON: {e}")
            print(f"[Architect Agent] Response was: {response[:200]}")
            return {}
