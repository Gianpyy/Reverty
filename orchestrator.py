from agents.architect_agent import ArchitectAgent
from agents.builder_agent import BuilderAgent
from tools.reviewer import ReviewerAgent
from clients.mock_llm_client import MockLLMClient
from helpers.utils import load_grammar

class Orchestrator:

    """
    Orchestrates the entire workflow of the system.
    """ 

    def __init__(self, use_mock: bool = False):
        """
        Initializes the Orchestrator with the necessary agents and LLM client.
        """
        self.grammar = load_grammar()
        
        if use_mock:
            print("[Orchestrator] Using MOCK LLM")
            self.client = MockLLMClient()
        else:
            # Real client initialization would go here
            self.client = None 

        self.architect = ArchitectAgent(self.client)
        self.builder = BuilderAgent(self.client, self.grammar)
        self.reviewer = ReviewerAgent()

    # --- Main Flow ---

    def run(self, user_prompt: str):
        """
        Executes the entire compilation and translation workflow.
        """
        print(f"--- Starting Workflow for: {user_prompt} ---")

        # 1. Define requirements and create the contract
        contract = self._design_technical_contract(user_prompt)

        # 2. Generate source code (Reverty)
        reverty_code = self._generate_reverty_source(contract)

        

        # 5. Final verification
        if not self._verify_python_implementation(python_code):
            return {"status": "error", "step": "review"}

        print("\n[Orchestrator] Workflow finished successfully!")
        return {"status": "success", "python_code": python_code}

  

    # --- Coordination Actions ---

    def _design_technical_contract(self, user_prompt: str):
        """
        Interacts with the Architect Agent to define the technical requirements.
        """
        print("[Orchestrator] Designing technical contract...")
        contract = self.architect.create_contract(user_prompt)
        print(f"[Contract] {contract}")
        return contract

    def _generate_reverty_source(self, contract):
        """
        Interacts with the BuilderAgent to generate Reverty source code.
        """

        print("\n[Orchestrator] Generating Reverty source code...")
        code = self.builder.build_code(contract)
        print(f"\n[Reverty Code]\n{repr(code)}")
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

    def _verify_python_implementation(self, python_code: str):
        """
        Performs a final review of the generated Python code.
        """
        print("\n[Orchestrator] Final review of Python implementation...")
        result = self.reviewer.run(python_code)
        
        if result["status"] == "error":
            print(f"[Orchestrator] Reviewer found issues: {result['message']}")
            return False
            
        print("[Orchestrator] Implementation verified.")
        return True
    
    def _verify_and_refine(self, code, tests, contract, max_retries, logger):
        """
        Exclusively manages the test execution and code repair cycle.
        """
        
        for i in range(max_retries):
            logger.add_iteration_marker(i + 1)
            result = self.executor.run_tests(code, tests)

            if result.success:
                self._log_success(result, logger)
                return "SUCCESS", code, tests

            # If it fails, refine
            self._log_failure(result, logger)
            code, tests, logs = self.refiner.refine(code, tests, result.output, contract)
            self._log_refinement(code, tests, logs, logger)

        return "FAILED", code, tests

    