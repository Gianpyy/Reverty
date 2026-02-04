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
from config import MAX_ORCHESTRATOR_ITERATIONS


class Orchestrator:
    """
    Orchestrates the entire workflow of the system.
    """

    def __init__(self, llm_client_type: LLMClientType = LLMClientType.MOCK):
        """
        Initializes the Orchestrator with the necessary agents and LLM client.
        """
        self.grammar = load_grammar()

        match llm_client_type:
            case LLMClientType.MOCK:
                print("[Orchestrator] Using MOCK LLM")
                self.client = MockLLMClient()

            case LLMClientType.OLLAMA:
                print("[Orchestrator] Using OLLAMA LLM")
                self.client = OllamaClient(model="qwen2.5-coder:7b")

            case LLMClientType.GITHUB_MODELS:
                print("[Orchestrator] Using GITHUB MODELS LLM")
                self.client = GitHubModelsClient()

            case _:
                self.client = None

        # Agents
        self.evaluator = EvaluatorAgent(self.client)
        self.architect = ArchitectAgent(self.client)
        self.coder = CoderAgent(self.client, self.grammar)
        self.test_generator = TestGeneratorAgent(self.client)
        self.tester = TesterAgent(self.client)

        # State
        self.request_type = RequestType.INITIAL
        self.reverty_code: str | None = None
        self.python_code: str | None = None
        self.tests: str | None = None
        self.code_errors: str | None = None
        self.test_errors: str | None = None

    # --- Main Flow ---

    def run(self, user_prompt: str):
        """
        Executes the entire compilation and translation workflow.
        """
        print(f"--- Starting Workflow for: {user_prompt} ---")

        # 1. Evaluate complexity
        complexity = self._evaluate_request_complexity(user_prompt)

        print(f"[Orchestrator] Complexity: {complexity}")

        # 2. Define requirements and create the contract
        contract = self._design_technical_contract(user_prompt, complexity)

        for i in range(MAX_ORCHESTRATOR_ITERATIONS):
            print(f"[Orchestrator] --------------- Starting iteration {i + 1}/{MAX_ORCHESTRATOR_ITERATIONS} ---------------")
            # 3. Generate Reverty/Python code with result based on request type (starting code generation or fix code)
            result = self._generate_code(contract)

            if result.status == Status.SUCCESS:
                # 4. Build test suite
                self._generate_tests(contract)

                # 5. Test the code
                tester_result = self._execute_tests(contract)
                print("[Orchestrator] Tester result: \n", tester_result)

                # Check if the code is correct, otherwise fix it and retry
                if tester_result["status"] == Status.SUCCESS.value:
                    print("\n[Orchestrator] Workflow finished successfully!")
                    return {"status": result.status.value, "code": self.reverty_code}
                else:
                    self.code_errors = tester_result["code_failures"]
                    self.test_errors = tester_result["test_failures"]
                    self._set_new_request_type(self.code_errors, self.test_errors)
                    continue
            else:
                # Exit from loop if code generation failed
                print("\n[Orchestrator] Workflow finished. Reason: code generation failed")
                return {"status": result.status.value, "message": result.message}

        # Exit from loop if max retries reached
        print("\n[Orchestrator] Workflow finished. Reason: max retries reached")
        return {"status": result.status.value, "code": self.reverty_code}

    # --- Coordination Actions ---
    def _evaluate_request_complexity(self, user_prompt: str):
        """
        Interacts with the Evaluator Agent to evaluate the complexity of the user prompt.
        """

        print("[Orchestrator] Evaluating request...")
        evaluation = self.evaluator.evaluate_request(user_prompt)
        return evaluation["complexity"]

    def _design_technical_contract(self, user_prompt: str, complexity: int):
        """
        Interacts with the Architect Agent to define the technical requirements.
        """
        
        print("[Orchestrator] Designing technical contract...")
        contract = self.architect.create_contract(user_prompt, complexity)
        return contract

    def _generate_code(self, contract) -> AnalysisResult:
        """
        Interacts with the CoderAgent to generate Reverty code with its Python equivalent.
        """

        if self.request_type == RequestType.INITIAL:
            print("\n[Orchestrator] Generating Reverty code...")
            self.reverty_code, self.python_code, result = self.coder.generate_code(contract)
            return result

        elif self.request_type == RequestType.FIX_CODE or self.request_type == RequestType.FIX_BOTH:
            print("\n[Orchestrator] Fixing Reverty code...")
            self.reverty_code, self.python_code, result = self.coder.fix_code(contract, self.reverty_code, self.python_code, self.code_errors)
            return result

        return AnalysisResult(status=Status.SUCCESS, message="No coding actions needed.")

    def _generate_tests(self, contract):
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
