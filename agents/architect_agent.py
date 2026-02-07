import json
from typing import Dict, Any
from agents.agent import Agent
from helpers.prompt_generator import generate_architect_request
from helpers.system_prompts import (
    ARCHITECT_SYSTEM_PROMPT_SIMPLE,
    ARCHITECT_SYSTEM_PROMPT_COMPLEX,
)


class ArchitectAgent(Agent):
    """
    Architect Agent: Contract Designer.
    Uses LLM to generate a contract from a user prompt.
    """

    def create_contract(self, user_prompt: str, complexity: int) -> Dict[str, Any]:
        """
        Creates a formal contract/specification for the requested code.
        """

        print(f"[Architect Agent] Designing contract for: '{user_prompt}'...")
        if complexity <= 5:
            print(f"[Architect Agent] Complexity is {complexity}, using simple system prompt.")
            system_prompt = ARCHITECT_SYSTEM_PROMPT_SIMPLE
        else:
            print(f"[Architect Agent] Complexity is {complexity}, using complex system prompt.")
            system_prompt = ARCHITECT_SYSTEM_PROMPT_COMPLEX

        request: str = generate_architect_request(user_prompt, complexity)
        print(f"[Architect Agent] Request: {request}")
        response: str = self.client.generate(user_prompt=request, system_prompt=system_prompt)

        # Try to parse response
        try:
            contract: Dict[str, Any] = self.extract_response(response)
            return contract
        except json.JSONDecodeError as e:
            print(f"[Architect Agent] Error decoding JSON: {e}")
            print(f"[Architect Agent] Response was: {response[:200]}")
            return {}

