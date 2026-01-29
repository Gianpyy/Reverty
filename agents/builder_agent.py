from helpers.utils import print_ast
from helpers.system_prompts import BUILDER_SYSTEM_PROMPT
from typing import Dict, Any
from agents.agent import Agent
import json
from tools.parser import Parser
from tools.transpiler import Transpiler
from helpers.prompt_generator import generate_fix_request

class BuilderAgent(Agent):
    """
    Builder Agent: Code Generator.
    Uses LLM to generate code based on a contract.
    """
    
    def __init__(self, client, grammar, model="llama3.2"):
        super().__init__(client)
        self.model = model
        self.grammar = grammar
        self.parser = Parser(grammar)
        self.transpiler = Transpiler()

    
    def build_code(self, contract: Dict[str, Any], max_iterations: int = 3) -> str:
        """
        Generates implementation code based on the contract.
        """
        
        print(f"[Builder] Building implementation for contract: {contract.get('function_name')}...")

        code_prompt = f"""Contract Specification: {json.dumps(contract, indent=2)}
                          Implement the function according to this contract.
                       """

        response = self.client.generate(
            user_prompt=code_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar
        )
        
        reverty_code_json = self._extract_json(response)
        reverty_code = reverty_code_json["code"] + "\n"


        final_status = "FAILED"
        
        try:
            for i in range(max_iterations):
                
                print(f"\n[Builder] Iteration {i + 1}...")

                # --- Parse Reverty code to AST ---
                
                parser_response = parse_reverty_code(reverty_code)

                if parser_response["status"] == "error":
                    
                    parsing_fix_prompt = generate_fix_request(reverty_code, parser_response["result"])
                    reverty_code = self.fix_code(parsing_fix_prompt)

                    continue

                ast = parser_response["result"]

                print(f"\n[Reverty Code]\n{print_ast(ast)}")


                # TODO
                # LLM call with transpilation error prompt

                # Static analysis 1. Flake 2. Mypy
                # if errors -> LLM FIX with error messages prompt


        except Exception as e:
            print(f"\n[Error] Exception occurred: {e}", flush=True)
            final_status = "ERROR"
        
        finally:
            print(f"\n✓ Builder Agent finished execution with status: {final_status}")

        return python_code

    def parse_reverty_code(self, reverty_code: str) -> Dict[str, Any]:

        """
        Parses Reverty code into an AST.
        """

        ast = self.parser.run(reverty_code)["ast"]
        
        if not ast:
            return {"status": "error", "result": ast["message"]}

        return {"status": "success", "result": ast}


    def fix_code(self, fix_prompt: str):

        """
        Fixes Reverty code based on error messages.
        """

        response = self.client.generate(
                prompt = fix_prompt,
                system_prompt = BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar
            )
        
        fix_result = self._extract_json(response)

        return fix_result["code"]
        



        
        