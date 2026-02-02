from helpers.utils import print_ast
from helpers.system_prompts import BUILDER_SYSTEM_PROMPT
from typing import Dict, Any, Tuple
from agents.agent import Agent
import json
import traceback
from tools.parser import Parser
from tools.transpiler import Transpiler
from tools.linter import Linter
from tools.type_checker import TypeChecker
from helpers.prompt_generator import generate_fix_request, generate_builder_request
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
        self.type_checker = TypeChecker()

    def build_code(self, contract: Dict[str, Any], max_iterations: int = 3) -> Tuple[str, str, AnalysisResult]:
        """
        Generates implementation code based on the contract.
        """

        print(
            f"[Builder] Building implementation for contract: {contract.get('function_name')}..."
        )

        builder_prompt = generate_builder_request(contract)

        response = self.client.generate(
            user_prompt=builder_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        print(f"[Builder Agent] Response: {response}")
        reverty_code_json = self._extract_json(response)
        reverty_code = reverty_code_json["code"] + "\n"

        print(f"[Builder Agent] Reverty Code: {json.dumps(reverty_code, indent=2)}")
        final_status = AnalysisResult(Status.ERROR, "")

        try:
            for i in range(max_iterations):
                print(f"\n[Builder] Iteration {i + 1}...")

                # --- PARSING ---
                # Parse Reverty code to AST
                parser_response = self._parse_reverty_code(reverty_code)

                # Update Reverty code if there's a parsing error
                if parser_response.status == Status.ERROR:
                    final_status = AnalysisResult(Status.ERROR, "Parsing failed.")
                    reverty_code = parser_response.message
                    continue

                # Get AST from response
                ast = parser_response.message
                print_ast(ast)

                # --- TRANSPILATION ---
                # Transpile AST to Python
                transpiler_response = self._transpile_ast_to_python(ast, reverty_code)

                # Update Reverty code if there's a transpilation error
                if transpiler_response.status == Status.ERROR:
                    final_status = AnalysisResult(Status.ERROR, "Transpilation failed.")
                    reverty_code = transpiler_response.message
                    continue

                # Get transpiled Python code
                python_code = transpiler_response.message

                print(f"\n[Python Code]\n{python_code}")

                # --- LINTING ---
                # Check for linting errors
                linter_response = self._check_linting_errors(python_code, reverty_code)

                if linter_response.status == Status.ERROR:
                    final_status = AnalysisResult(Status.ERROR, "Linting failed.")
                    reverty_code = linter_response.message
                    continue

                # --- TYPE CHECKING ---
                # Check for type errors
                type_checker_response = self._check_type_errors(
                    python_code, reverty_code
                )

                if type_checker_response.status == Status.ERROR:
                    final_status = AnalysisResult(Status.ERROR, "Type checking failed.")
                    reverty_code = type_checker_response.message
                    continue

                final_status = AnalysisResult(Status.SUCCESS, "Code built successfully.")

                return reverty_code, python_code, final_status


        except Exception:
            traceback.print_exc()
            final_status = AnalysisResult(Status.ERROR, "Exception occurred during code building.")

        finally:
            print(f"[Builder] Finished execution with status: {final_status.status.value}")      
            return reverty_code, "", final_status

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
                error_type=ErrorType.PARSING.value,
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
                error_type=ErrorType.TRANSPILATION.value,
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
                error_type=ErrorType.LINTING.value,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return success status
        return AnalysisResult(Status.SUCCESS, linter_response.message)

    def _check_type_errors(self, python_code: str, reverty_code: str) -> AnalysisResult:
        """
        Checks for type errors in Python code. If there's a type error, it fixes it and returns the fixed code.
        """
        # Check for type errors
        type_checker_response = self.type_checker.run(python_code)

        # If there's a type error, fix it
        if type_checker_response.status == Status.ERROR:
            reverty_code = self._fix_code(
                errors=type_checker_response.message,
                reverty_code=reverty_code,
                error_type=ErrorType.TYPE_CHECKING.value,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return success status
        return AnalysisResult(Status.SUCCESS, type_checker_response.message)

    def _fix_code(
        self, errors: str, reverty_code: str, error_type: str
    ) -> AnalysisResult:
        """
        Fixes Reverty code based on error messages.
        """

        # Build fix prompt
        fix_prompt = generate_fix_request(
            reverty_code=reverty_code,
            errors=errors,
            error_type=error_type,
        )

        # Call LLM
        print(f"\n[Builder Agent] Fix Prompt: {fix_prompt}")
        response = self.client.generate(
            user_prompt=fix_prompt,
            system_prompt=BUILDER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        fix_result = self._extract_json(response)

        return fix_result["code"]
