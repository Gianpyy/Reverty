import json
from gui.conversation_logger import log_message
from helpers.enums import AnalysisResult
from agents.tester_agent import TesterAgent
from agents.architect_agent import ArchitectAgent
from agents.coder_agent import CoderAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.test_generator_agent import TestGeneratorAgent
from clients.mock_llm_client import MockLLMClient
from helpers.utils import load_grammar
from helpers.enums import LLMClientType
from clients.ollama_client import OllamaClient
from clients.github_models_client import GitHubModelsClient
from helpers.enums import Status, RequestType
from config import MAX_ORCHESTRATOR_ITERATIONS, MAX_VALIDATION_ITERATIONS, MAX_EVALUATION_RETRIES
import streamlit as st
from typing import Dict, Any


class Orchestrator:
    """
    Orchestrates the entire workflow of the system.
    """

    def __init__(
        self, 
        llm_client_type: LLMClientType = LLMClientType.MOCK, 
        temperature: float = 0.3, 
        api_key: str = None, 
        on_log = None, 
        max_orchestrator_iterations: int = MAX_ORCHESTRATOR_ITERATIONS, 
        max_validation_iterations: int = MAX_VALIDATION_ITERATIONS, 
        max_evaluation_retries: int = MAX_EVALUATION_RETRIES
    ):
        """
        Initializes the Orchestrator with the necessary agents and LLM client.
        """
        self.grammar = load_grammar()
        self.on_log = on_log

        match llm_client_type:
            case LLMClientType.MOCK:
                print("[Orchestrator] Using MOCK LLM")
                self.client = MockLLMClient()

            case LLMClientType.OLLAMA:
                print("[Orchestrator] Using OLLAMA LLM")
                self.client = OllamaClient(temperature = temperature)

            case LLMClientType.GITHUB_MODELS:
                print("[Orchestrator] Using GITHUB MODELS LLM")
                self.client = GitHubModelsClient(temperature = temperature, api_key = api_key)

            case _:
                self.client = None

        # Agents
        self.evaluator = EvaluatorAgent(self.client, max_evaluation_retries=max_evaluation_retries)
        self.architect = ArchitectAgent(self.client)
        self.coder = CoderAgent(self.client, self.grammar, max_validation_iterations=max_validation_iterations)
        self.test_generator = TestGeneratorAgent(self.client)
        self.tester = TesterAgent(self.client)

        # State
        self.request_type = RequestType.INITIAL
        self.reverty_code: str | None = None
        self.python_code: str | None = None
        self.tests: str | None = None
        self.code_errors: str | None = None
        self.test_errors: str | None = None

        # Iteration limits
        self.max_orchestrator_iterations = max_orchestrator_iterations
        self.max_validation_iterations = max_validation_iterations

        # Set logger for agents
        self.set_logger(on_log)

    def set_logger(self, on_log):
        """
        Sets the logging callback and propagates it to agents.
        """
        self.on_log = on_log
        self.evaluator.set_logger(on_log)
        self.architect.set_logger(on_log)
        self.coder.set_logger(on_log)
        self.test_generator.set_logger(on_log)
        self.tester.set_logger(on_log)

    # --- Main Flow ---


    def run(self, user_prompt: str):

        """
        Executes the entire compilation and translation workflow.
        """

        
        print(f"--- Starting Workflow for: {user_prompt} ---")

        log_message(f"↺ Generating {self.request_type.value.upper()} for the requested task.")

        # 1. Evaluate complexity
        complexity: int = self._evaluate_request_complexity(user_prompt)

        log_message(f"Evaluated complexity of the requested task is {complexity}")
        print(f"[Orchestrator] Complexity: {complexity}")

        # 2. Define requirements and create the contract
        contract: Dict[str, Any] = self._design_technical_contract(user_prompt, complexity)
        formatted_contract = json.dumps(contract, indent=2, ensure_ascii=False)
        log_message(f"Technical Contract Created:\n{formatted_contract}")


        print("[Orchestrator] Max orchestrator iterations: ", self.max_orchestrator_iterations)
        print("[Orchestrator] Max validation iterations: ", self.max_validation_iterations)
        for i in range(self.max_orchestrator_iterations):
            print(f"[Orchestrator] --------------- Starting iteration {i + 1}/{self.max_orchestrator_iterations} --------------------------")
            log_message(f"----- STARTING ITERATION {i + 1}/{self.max_orchestrator_iterations} -----")
            # 3. Generate Reverty/Python code with result based on request type (starting code generation or fix code)

            log_message(f"↺ Generating initial code for {self.request_type.value.upper()} request.")
            result: AnalysisResult = self._generate_or_fix_code(contract)

            st.session_state.shared_reverty_code = self.reverty_code
            st.session_state.shared_python_code = self.python_code

            if result.status == Status.SUCCESS:
                # 4. Build test suite
                self._generate_or_fix_tests(contract)

                # 5. Test the code
                tester_result = self._execute_tests(contract)
                print("[Orchestrator] Tester result: \n", tester_result)

                # Check if the code is correct, otherwise fix it and retry
                if tester_result["status"] == Status.SUCCESS.value:
                    print("\n[Orchestrator] Workflow finished successfully!")

                    st.session_state.shared_log_string += tester_result["status"] + "\n"
                    # TODO: Costruire Payload per inviare al client
                    return {"status": result.status.value, "reverty_code": self.reverty_code, "python_code": self.python_code}
                else:
                    self.code_errors = tester_result["code_failures"]
                    self.test_errors = tester_result["test_failures"]

                    st.session_state.shared_log_string += f"⚠️ Errore Test: {self.test_errors}\n"
                    st.session_state.shared_log_string += f"❌ Errore Codice: {self.code_errors}\n"

                    self._set_new_request_type(self.code_errors, self.test_errors)
                    continue
            else:
                # Exit from loop if code generation failed
                print("\n[Orchestrator] Workflow finished. Reason: code generation failed")
                return {"status": result.status.value, "message": result.message}

        # Exit from loop if max retries reached
        print("\n[Orchestrator] Workflow finished. Reason: max retries reached")

        # TODO: Costruire Payload per inviare al client
        return {"status": result.status.value, "reverty_code": self.reverty_code, "python_code": self.python_code}

    # --- Coordination Actions ---
    def _evaluate_request_complexity(self, user_prompt: str) -> int:
        """
        Interacts with the Evaluator Agent to evaluate the complexity of the user prompt.
        """

        print("[Orchestrator] Evaluating request...")
        complexity: int = self.evaluator.evaluate_request(user_prompt)
        return complexity

    def _design_technical_contract(self, user_prompt: str, complexity: int) -> Dict[str, Any]:
        """
        Interacts with the Architect Agent to define the technical requirements.
        """
        
        print("[Orchestrator] Designing technical contract...")
        contract: Dict[str, Any] = self.architect.create_contract(user_prompt, complexity)
        return contract

    def _generate_or_fix_code(self, contract: Dict[str, Any]) -> AnalysisResult:
        """
        Interacts with the CoderAgent to generate Reverty code with its Python equivalent.
        """

        if self.request_type == RequestType.INITIAL:
            print("\n[Orchestrator] Generating Reverty code...")
            self.reverty_code, self.python_code, result = self.coder.build_initial_code(contract)
            return result

        elif self.request_type == RequestType.FIX_CODE or self.request_type == RequestType.FIX_BOTH:
            print("\n[Orchestrator] Fixing Reverty code...")
            self.reverty_code, self.python_code, result = self.coder.fix_code(contract, self.reverty_code, self.python_code, self.code_errors)
            return result

        return AnalysisResult(status=Status.SUCCESS, message="No coding actions needed.")

    def _generate_or_fix_tests(self, contract: Dict[str, Any]):
        """
        Interacts with the Tester Agent to generate tests.
        """

        if self.request_type == RequestType.INITIAL:
            print("\n[Orchestrator] Generating tests...")
            self.tests = self.test_generator.build_tests(contract, self.python_code)
        elif self.request_type == RequestType.FIX_TESTS or self.request_type == RequestType.FIX_BOTH:
            print("\n[Orchestrator] Fixing tests...")
            self.tests = self.test_generator.fix_tests(contract, self.python_code, self.test_errors)

        print(f"\n[Tests]\n{self.tests}")

    def _execute_tests(self, contract):
        """
        Interacts with the TesterAgent to execute tests.
        """
        print("\n[Orchestrator] Executing tests...")
        result = self.tester.test(contract, self.python_code, self.reverty_code, self.tests)
        return result

    def _set_new_request_type(self, code_errors: str | None, test_errors: str | None):
        """
        Sets the new request type based on the errors.
        """
        if code_errors is not None and test_errors is not None:
            self.request_type = RequestType.FIX_BOTH
        elif code_errors is not None:
            self.request_type = RequestType.FIX_CODE
        elif test_errors is not None:
            self.request_type = RequestType.FIX_TESTS
    
    
