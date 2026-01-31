from agents.architect_agent import ArchitectAgent
from agents.builder_agent import BuilderAgent
from clients.mock_llm_client import MockLLMClient
from helpers.utils import load_grammar, print_ast
from helpers.enums import LLMClientType
from clients.ollama_client import OllamaClient

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

            case _:
                self.client = None

        self.architect = ArchitectAgent(self.client)
        self.builder = BuilderAgent(self.client, self.grammar)

    # --- Main Flow ---

    def run(self, user_prompt: str):
        """
        Executes the entire compilation and translation workflow.
        """
        print(f"--- Starting Workflow for: {user_prompt} ---")

        # 1. Define requirements and create the contract
        contract = self._design_technical_contract(user_prompt)

        # 2. Generate Reverty code
        reverty_code = self._generate_reverty_code(contract)

        # 5. Final verification
        # if not self._verify_python_implementation(python_code):
        #    return {"status": "error", "step": "review"}

        print("\n[Orchestrator] Workflow finished successfully!")
        return {"status": "success", "code": reverty_code}

    # --- Coordination Actions ---

    def _design_technical_contract(self, user_prompt: str):
        """
        Interacts with the Architect Agent to define the technical requirements.
        """
        print("[Orchestrator] Designing technical contract...")
        contract = self.architect.create_contract(user_prompt)
        return contract

    def _generate_reverty_code(self, contract):
        """
        Interacts with the BuilderAgent to generate Reverty code.
        """

        print("\n[Orchestrator] Generating Reverty code...")
        code = self.builder.build_code(contract)
        print(f"\n[Reverty Code]\n{code}")
        return code

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

