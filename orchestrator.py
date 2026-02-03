from helpers.enums import AnalysisResult
from typing import Tuple
from agents.tester_agent import TesterAgent
from agents.architect_agent import ArchitectAgent
from agents.coder_agent import CoderAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.test_generator_agent import TestGeneratorAgent
from clients.mock_llm_client import MockLLMClient
from helpers.utils import load_grammar, print_ast
from helpers.enums import LLMClientType
from clients.ollama_client import OllamaClient
from clients.github_models_client import GitHubModelsClient
from helpers.enums import Status, RequestType

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
                self.client = OllamaClient()

            case LLMClientType.GITHUB_MODELS:
                print("[Orchestrator] Using GITHUB MODELS LLM")
                self.client = GitHubModelsClient()

            case _:
                self.client = None

        self.evaluator = EvaluatorAgent(self.client)
        self.architect = ArchitectAgent(self.client)
        self.coder = CoderAgent(self.client, self.grammar)
        self.test_generator = TestGeneratorAgent(self.client)
        self.tester = TesterAgent(self.client)
        
    # --- Main Flow ---

    def run(self, user_prompt: str, max_retries: int = 3):
        """
        Executes the entire compilation and translation workflow.
        """
        print(f"--- Starting Workflow for: {user_prompt} ---")

        # 1. Evaluate complexity
        complexity = self._evaluate_request_complexity(user_prompt)

        print(f"[Orchestrator] Complexity: {complexity}") 

        # 2. Define requirements and create the contract
        contract = self._design_technical_contract(user_prompt, complexity)

        request_type = RequestType.INITIAL
        reverty_code = ""
        python_code = ""
        errors = ""

        for i in range(max_retries):

            # 3. Generate Reverty/Python code with result based on request type (starting code generation or fix code)
            reverty_code, python_code, result = self._generate_code(contract=contract, request_type=request_type, reverty_code=reverty_code, python_code=python_code, errors=errors)
        
            if result.status == Status.SUCCESS:
                # 4. Build test suite
                test_code = self._generate_tests(contract, python_code)

                print("[Orchestrator] Test code: \n", python_code)
                # 5. Test the code
                tester_result = self.tester.test(contract, python_code, reverty_code, test_code, errors)
                print("[Orchestrator] Tester result: \n", tester_result)

                #Check if the code is correct, otherwise fix it and retry
                if tester_result["status"] == Status.SUCCESS.value:   # TODO: Da gestire meglio?
                    print("\n[Orchestrator] Workflow finished successfully")
                    return {"status": result.status.value, "code": reverty_code}
                else:
                    request_type = RequestType.FIX
                    errors = tester_result["test_failures"]
                    continue

        print("\n[Orchestrator] Workflow finished because max retries reached")
        return {"status": result.status.value, "code": reverty_code}

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

    def _generate_code(self, contract, request_type: RequestType, reverty_code: str, python_code: str, errors: str) -> Tuple[str, str, AnalysisResult]:
        """
        Interacts with the CoderAgent to generate Reverty code with its Python equivalent.
        """

        print("\n[Orchestrator] Generating Reverty code...")
        response = self.coder.run(contract = contract, request_type = request_type, reverty_code = reverty_code, python_code = python_code, errors = errors)
        return response

    def _validate_and_parse_syntax(self, reverty_code: str):
        """
        Validates the syntax of the Reverty code using the ParserAgent.
        """

        print("\n[Orchestrator] Validating syntax and building AST...")
        result = self.parser.run(reverty_code)

        if result["status"] == "error":
            print(f"[Orchestrator] Syntax Error: {result['message']}")
            return None

        print("[Orchestrator] AST generated successfully.")
        print_ast(result["ast"])
        return result["ast"]

    def _transpile_to_python(self, ast):
        """
        Transpiles the AST into Python code using the TranspilerAgent.
        """

        print("\n[Orchestrator] Transpiling AST to Python...")
        result = self.transpiler.run(ast)

        if result["status"] == "error":
            print(f"[Orchestrator] Transpilation Error: {result['message']}")
            return None

        print("[Orchestrator] Python code ready.")
        return result["python_code"]
    
    def _generate_tests(self, contract, python_code):
        """
        Interacts with the Tester Agent to generate tests.
        """

        print("\n[Orchestrator] Generating tests...")
        tests = self.test_generator.build_tests(contract, python_code)
        
        print(f"\n[Tests]\n{tests}")
        return tests
