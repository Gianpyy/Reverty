from helpers.system_prompts import BUILDER_SYSTEM_PROMPT
from typing import Dict, Any
from agents.agent import Agent
import json

class BuilderAgent(Agent):
    """
    Builder Agent: Code Generator.
    Uses LLM to generate code based on a contract.
    """
    def __init__(self, client, grammar, model="llama3.2"):
        super().__init__(client)
        self.model = model
        self.grammar = grammar

    # TODO: Add loggers and verification loop
    def build_code(self, contract: Dict[str, Any], max_iterations: int = 3) -> str:
        """
        Generates implementation code based on the contract.

        Args:
            contract: Contract in JSON format.
            max_iterations: Maximum number of iterations.

        Returns: Generated Reverty code
        """
        print(f"[Builder] Building implementation for contract: {contract.get('function_name')}...")

        code_prompt = f"""Contract Specification: {json.dumps(contract, indent=2)}
                          Implement the function according to this contract.
                       """

        response = self.client.generate(
            user_prompt=code_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT+"\n\n"+self.grammar
        )
        
        # Verification Loop - TODO
        # Static Analysis - TODO

        final_status = "FAILED"
        try:
            for i in range(max_iterations):
                print("ktm")
        except Exception as e:
            print(f"\n[Error] Exception occurred: {e}", flush=True)
            final_status = "ERROR"
        
        finally:
            print(f"\n✓ Builder Agent finished execution with status: {final_status}")

        # Try to parse JSON
        try:
            reverty_code = self._extract_json(response)
            return reverty_code["code"]
        except json.JSONDecodeError as e:
            print(f"[Builder Agent] Error decoding JSON: {e}")
            print(f"[Builder Agent] Response was: {reverty_code[:200]}")
            return {}