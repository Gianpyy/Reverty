from helpers.utils import print_ast
from helpers.system_prompts import BUILDER_SYSTEM_PROMPT
from typing import Dict, Any
from agents.agent import Agent
import json
from tools.parser import Parser
from tools.transpiler import Transpiler
from tools.linter import Linter
from helpers.prompt_generator import generate_fix_request
from lark import Tree
from helpers.enums import AnalysisResult, Status, ErrorType


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
        self.linter = Linter()

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

                # --- PARSING ---
                # Parse Reverty code to AST
                parser_response = self._parse_reverty_code(reverty_code)

                # Update Reverty code if there's a parsing error
                if parser_response.status == Status.ERROR:
                    reverty_code = parser_response.message
                    continue

                # Get AST from response
                ast = parser_response.message
                print_ast(ast)

                # --- TRANSPILATION ---
                # Transpile AST to Python
                transpiler_response = self._transpile_ast_to_python(ast)

                # Update Reverty code if there's a transpilation error
                if transpiler_response.status == Status.ERROR:
                    reverty_code = transpiler_response.message
                    continue

                # Get transpiled Python code
                python_code = transpiler_response.message

                print(f"\n[Python Code]\n{python_code}")

                # --- LINTING ---
                # Check for linting errors
                linter_response = self._check_linting_errors(python_code, reverty_code)

                if linter_response.status == Status.ERROR:
                    reverty_code = linter_response.message
                    continue

                # TODO
                # 2. Mypy
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
        Parses Reverty code to AST. If there's a parsing error, it fixes it and returns the fixed code.
        """
        # Parse Reverty code to AST
        parser_response = self.parser.run(reverty_code)

        # If there's a parsing error, fix it
        if parser_response.status == Status.ERROR:
            reverty_code = self._fix_code(
                errors=parser_response.message,
                reverty_code=reverty_code,
                error_type=ErrorType.PARSING,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return AST
        return AnalysisResult(Status.SUCCESS, parser_response.message)

    def _transpile_ast_to_python(self, ast: Tree, reverty_code: str) -> AnalysisResult:
        """
        Transpiles AST to Python. If there's a transpilation error, it fixes it and returns the fixed code.
        """
        # Transpile AST to Python
        transpiler_response = self.transpiler.run(ast)

        # If there's a transpilation error, fix it
        if transpiler_response.status == Status.ERROR:
            reverty_code = self._fix_code(
                errors=transpiler_response.message,
                reverty_code=reverty_code,
                error_type=ErrorType.TRANSPILATION,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return Python code
        return AnalysisResult(Status.SUCCESS, transpiler_response.message)

    def _check_linting_errors(
        self, python_code: str, reverty_code: str
    ) -> AnalysisResult:
        """
        Lints Python code. If there's a linting error, it fixes it and returns the fixed code.
        """
        # Check for linting errors
        linter_response = self.linter.run(python_code)

        # If there's a linting error, fix it
        if linter_response.status == Status.ERROR:
            reverty_code = self._fix_code(
                errors=linter_response.message,
                reverty_code=reverty_code,
                error_type=ErrorType.LINTING,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return success status
        return AnalysisResult(Status.SUCCESS, linter_response.message)

    def _fix_code(
        self, errors: str, reverty_code: str, error_type: str
    ) -> AnalysisResult:
        """
        Fixes Reverty code based on error messages.
        """

        # Build fix prompt
        parsing_fix_prompt = generate_fix_request(
            reverty_code=reverty_code,
            errors=errors,
            error_type=error_type,
        )

        # Call LLM
        response = self.client.generate(
            user_prompt=parsing_fix_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        fix_result = self._extract_json(response)

        return fix_result["code"]
