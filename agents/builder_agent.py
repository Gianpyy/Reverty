from helpers.utils import print_ast
from helpers.system_prompts import BUILDER_SYSTEM_PROMPT
from typing import Dict, Any
from agents.agent import Agent
import json
from tools.parser import Parser
from tools.transpiler import Transpiler
from helpers.prompt_generator import generate_fix_request
from lark import Tree
from helpers.analysis_result import AnalysisResult, Status


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

        print(
            f"[Builder] Building implementation for contract: {contract.get('function_name')}..."
        )

        code_prompt = f"""Contract Specification: {json.dumps(contract, indent=2)}
                          Implement the function according to this contract.
                       """

        response = self.client.generate(
            user_prompt=code_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        reverty_code_json = self._extract_json(response)
        reverty_code = reverty_code_json["code"] + "\n"

        final_status = "FAILED"

        try:
            for i in range(max_iterations):
                print(f"\n[Builder] Iteration {i + 1}...")

                # --- Parse Reverty code to AST ---

                parser_response = self._parse_reverty_code(reverty_code)

                if parser_response.status == Status.ERROR:
                    parsing_fix_prompt = generate_fix_request(
                        reverty_code=reverty_code,
                        errors=parser_response.message,
                        error_type="parsing",
                    )
                    reverty_code = self._fix_code(parsing_fix_prompt)

                    continue

                ast = parser_response.message
                print_ast(ast)

                # --- Transpile AST to Python ---

                transpiler_response = self._transpile_ast_to_python(ast)

                if transpiler_response.status == Status.ERROR:
                    transpilation_fix_prompt = generate_fix_request(
                        reverty_code=reverty_code,
                        errors=transpiler_response.message,
                        error_type="transpilation",
                    )
                    reverty_code = self._fix_code(transpilation_fix_prompt)

                    continue

                python_code = transpiler_response.message

                print(f"\n[Python Code]\n{python_code}")

                # TODO
                # Static analysis 1. Flake 2. Mypy
                # if errors -> LLM FIX with error messages prompt

                final_status = "SUCCESS"
                return reverty_code
        except Exception as e:
            print(f"\n[Error] Exception occurred: {e}", flush=True)
            final_status = "ERROR"

        finally:
            print(f"[Builder] Finished execution with status: {final_status}")

    def _parse_reverty_code(self, reverty_code: str) -> AnalysisResult:
        """
        Parses Reverty code into an AST.
        """

        response = self.parser.run(reverty_code)

        if response.status == Status.ERROR:
            return AnalysisResult(status=Status.ERROR, message=response.message)

        return AnalysisResult(status=Status.SUCCESS, message=response.message)

    def _transpile_ast_to_python(self, ast: Tree[Any]) -> AnalysisResult:
        """
        Transpiles AST to Python code.
        """

        response = self.transpiler.run(ast)

        if response.status == Status.ERROR:
            return AnalysisResult(status=Status.ERROR, message=response.message)

        return AnalysisResult(status=Status.SUCCESS, message=response.message)

    def _fix_code(self, fix_prompt: str) -> str:
        """
        Fixes Reverty code based on error messages.
        """

        response = self.client.generate(
            user_prompt=fix_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        fix_result = self._extract_json(response)

        return fix_result["code"]
