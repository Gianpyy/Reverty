from agents.architect_agent import ArchitectAgent
from agents.builder_agent import BuilderAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.tester_agent import TesterAgent
from clients.mock_llm_client import MockLLMClient
from helpers.utils import load_grammar, print_ast
from helpers.enums import LLMClientType
from clients.ollama_client import OllamaClient
from clients.github_models_client import GitHubModelsClient
from helpers.enums import Status

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
        self.builder = BuilderAgent(self.client, self.grammar)
        self.tester = TesterAgent(self.client)
        
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

        # 3. Generate Reverty/Python code
        reverty_code, python_code, result = self._generate_code(contract)


        if result.status == Status.SUCCESS:
            # 4. Build tests
            test_code = self._generate_tests(contract, python_code)

            print("\n[Orchestrator Test Code]\n")
            print(f"{test_code}")

        print("\n[Orchestrator] Workflow finished successfully!")
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

    def _generate_code(self, contract):
        """
        Interacts with the BuilderAgent to generate Reverty code with its Python equivalent.
        """

        print("\n[Orchestrator] Generating Reverty code...")
        response = self.builder.build_code(contract)
        print(f"\n[Reverty Code]\n{response}")
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
        tests = self.tester.build_tests(contract, python_code)
        
        print(f"\n[Tests]\n{tests}")
        return tests
