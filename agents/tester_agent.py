from typing import Dict, Any
from agents.agent import Agent
from helpers.system_prompts import TESTER_SYSTEM_PROMPT
from helpers.prompt_generator import generate_tester_request

class TesterAgent(Agent):
    """
    Uses LLM to generate pytest tests based on a formal contract and implementation code.
    """

    def build_tests(self, contract: Dict[str, Any], code: str) -> str:
        """
        Generates pytest tests based on the contract and implementation code.
        
        """
        print(f"[Tester] Writing tests for: {contract.get('function_name')}...")
        
        test_prompt = generate_tester_request(contract, code)

        response = self.client.generate(
            user_prompt=test_prompt,
            system_prompt=TESTER_SYSTEM_PROMPT
        )
        
        # Clean up potential markdown formatting
        print(f"[Tester Agent] Response: {response}")
        test_code = self._extract_json(response)["code"] + "\n"
        
        return test_code