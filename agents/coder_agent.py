from helpers.utils import print_ast_string
from helpers.utils import print_ast
from helpers.system_prompts import CODER_SYSTEM_PROMPT
from typing import Dict, Any, Tuple
from agents.agent import Agent
import json
import traceback
from tools.parser import Parser
from tools.transpiler import Transpiler
from tools.linter import Linter
from tools.type_checker import TypeChecker
from helpers.prompt_generator import generate_test_fix_request, generate_initial_code_request, generate_static_fix_request
from lark import Tree
from helpers.enums import AnalysisResult, Status, ErrorType
from config import MAX_VALIDATION_ITERATIONS

import streamlit as st

class CoderAgent(Agent):
    """
    Coder Agent: Code Generator.
    Uses LLM to generate code based on a contract.
    """

    def __init__(self, client, grammar, model="llama3.2", max_validation_iterations: int = MAX_VALIDATION_ITERATIONS):
        super().__init__(client)
        self.model = model
        self.grammar = grammar
        self.contract : Dict[str, Any] | None = None
        self.parser = Parser(grammar)
        self.transpiler = Transpiler()
        self.linter = Linter()
        self.type_checker = TypeChecker()
        self.max_validation_iterations = max_validation_iterations
        

    def build_initial_code(self, contract: Dict[str, Any]) -> Tuple[str, str, AnalysisResult]:
        """
        Generates Reverty code based on the contract.
        """
        
        self.contract = contract
        coder_prompt = generate_initial_code_request(contract)

        self.log(f"[CODER] Initial code prompt:\n{coder_prompt}")

        reverty_code = self._generate_code(coder_prompt)

        self.log(f"[CODER] Initial code:\n{reverty_code}")

        return self._validate_code(reverty_code)

    def fix_code(self, contract: Dict[str, Any], reverty_code: str, python_code: str, errors: str) -> Tuple[str, str, AnalysisResult]:
        """
        Fixes Reverty code based on the contract, python code and errors.
        """

        coder_prompt = generate_test_fix_request(contract, reverty_code, python_code, errors)

        self.log(f"Fix code prompt:\n{coder_prompt}")

        reverty_code = self._generate_code(coder_prompt)

        self.log(f"Fixed code:\n{coder_prompt}")

        return self._validate_code(reverty_code)

    def _generate_code(self, coder_prompt: str) -> str:

        """
        Generates Reverty code based on the coder prompt (can be initial or fix prompt).
        """
        
        response = self.client.generate(
            user_prompt=coder_prompt,
            system_prompt=CODER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        self.log(f"[Coder Agent] Response: {response}")
        reverty_code_json = self.extract_response(response)
        reverty_code = reverty_code_json["code"] + "\n"

        return reverty_code


    def _validate_code(self, reverty_code: str) -> Tuple[str, str, AnalysisResult]:
        """
        Validates Reverty code doing multiple iterations of parsing, transpiling, linting and type checking.
        """

        self.log(f"[Coder Agent] Reverty Code:\n {reverty_code}")
        final_status = AnalysisResult(Status.ERROR, "")

        try:
            for i in range(self.max_validation_iterations):
                self.log(f"\n[Coder Agent] --------------- Starting validation loop: iteration {i + 1}/{self.max_validation_iterations} ----------------------------")

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

                ast_string = print_ast_string(ast)
                st.session_state["shared_ast_string"] = ast_string

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

                # --- LINTING ---
                # Check for linting errors
                linter_response = self._check_linting_errors(python_code, reverty_code)

                if linter_response.status == Status.ERROR:
                    final_status = AnalysisResult(Status.ERROR, "Linting failed.")
                    reverty_code = linter_response.message
                    continue

                # --- TYPE CHECKING ---
                # Check for type errors
                type_checker_response = self._check_type_errors(python_code, reverty_code)

                if type_checker_response.status == Status.ERROR:
                    final_status = AnalysisResult(Status.ERROR, "Type checking failed.")
                    reverty_code = type_checker_response.message
                    continue

                final_status = AnalysisResult(Status.SUCCESS, "Code built successfully.")

                self.log(f"[Coder] Python code: {python_code}")

                return reverty_code, python_code, final_status

        except Exception:
            traceback.print_exc()
            final_status = AnalysisResult(
                Status.ERROR, "Exception occurred during code building."
            )

        finally:
            self.log(f"[Coder] Finished execution with status: {final_status.status.value}")

        return reverty_code, "", final_status

    def _parse_reverty_code(self, reverty_code: str) -> AnalysisResult:
        """
        Parses Reverty code to AST. If there's a parsing error, it fixes it and returns the fixed code.
        """
        # Parse Reverty code to AST
        parser_response = self.parser.run(reverty_code)

        # If there's a parsing error, fix it
        if parser_response.status == Status.ERROR:
            reverty_code = self._fix_static_errors(
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
            reverty_code = self._fix_static_errors(
                errors=transpiler_response.message,
                reverty_code=reverty_code,
                error_type=ErrorType.TRANSPILATION.value,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return Python code
        return AnalysisResult(Status.SUCCESS, transpiler_response.message)

    def _check_linting_errors(self, python_code: str, reverty_code: str) -> AnalysisResult:
        """
        Lints Python code. If there's a linting error, it fixes it and returns the fixed code.
        """
        # Check for linting errors
        linter_response = self.linter.run(python_code)

        # If there's a linting error, fix it
        if linter_response.status == Status.ERROR:
            reverty_code = self._fix_static_errors(
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
            reverty_code = self._fix_static_errors(
                errors=type_checker_response.message,
                reverty_code=reverty_code,
                error_type=ErrorType.TYPE_CHECKING.value,
            )

            # Return fixed code
            return AnalysisResult(Status.ERROR, reverty_code)

        # Return success status
        return AnalysisResult(Status.SUCCESS, type_checker_response.message)

    def _fix_static_errors(self, errors: str, reverty_code: str, error_type: str) -> AnalysisResult:
        """
        Fixes Reverty code based on error messages.
        """

        # Build fix prompt
        fix_prompt = generate_static_fix_request(
            reverty_code=reverty_code,
            errors=errors,
            error_type=error_type,
            contract=self.contract,
        )

        # Call LLM
        self.log(f"\n[Coder Agent] Fix Prompt: {fix_prompt}")
        response = self.client.generate(
            user_prompt=fix_prompt,
            system_prompt=CODER_SYSTEM_PROMPT + "\n\n" + self.grammar,
        )

        fix_result = self.extract_response(response)

        return fix_result["code"]
