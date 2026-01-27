from helpers.ast_printer import print_ast
from agents.parser_agent import ParserAgent
from agents.transpiler_agent import TranspilerAgent
from agents.architect_agent import ArchitectAgent
from agents.builder_agent import BuilderAgent
from clients.mock_llm_client import MockLLMClient
from config import grammar_path


class Orchestrator:
    """
    Orchestrator class.
    """

    def get_grammar(self):
        """
        Get the grammar from the grammar Lark file.
        """
        with open(grammar_path, "r") as file:
            return file.read()

    def __init__(self, use_mock: bool = False):
        """
        Initialize the Orchestrator.

        Args:
            use_mock: If True, use MockLLMClient. If None, use config.USE_MOCK
            api_key: API key for OpenAI. If None, use config.OPENAI_API_KEY
            github_token: GitHub Personal Access Token for GitHub Models API
            use_ollama: If True, use local Ollama
        """

        self.grammar = self.get_grammar()

        if use_mock:
            print("[Orchestrator] Using MOCK LLM")
            self.client = MockLLMClient()

        self.architect = ArchitectAgent(self.client)
        self.builder = BuilderAgent(self.client, self.grammar)
        self.parser = ParserAgent(self.grammar)
        self.transpiler = TranspilerAgent()

    def run(self, user_prompt: str):
        """
        Main orchestrator loop.
        """
        print("[Orchestrator] Starting execution for \n", user_prompt)

        # Step 1: Architect creates contract
        print("[Orchestrator] Step 1: Architect creating contract...")
        contract = self.architect.create_contract(user_prompt)
        print(f"[Contract] {contract}")

        # Step 2: Builder generates code
        print("\n[Orchestrator] Step 2: Builder generating code...")
        reverty_code = self.builder.build_code(contract)


        # Parser agent
        print("\n[Orchestrator] Step 3: Parser validating syntax...")
        print("\n[Reverty Code]\n", reverty_code)
        result = self.parser.run(reverty_code)
        if result["status"] == "error":
            error_message = result["message"]
            print(f"[Orchestrator] Error in Parser Agent: {error_message}")
            return {"status": "error", "message": error_message}
        else:
            ast = result["ast"]
            print("[Orchestrator] AST generated correctly\n")
            print_ast(ast)

        # Transpiler agent
        result_python_code = self.transpiler.run(ast)
        if result_python_code["status"] == "error":
            error_message = result_python_code["message"]
            print(f"[Orchestrator] Error in Transpiler Agent: {error_message}")
            return {"status": "error", "message": error_message}
        else:
            python_code = result_python_code["python_code"]
            print("[Orchestrator] Python code generated correctly\n")
            print(python_code)
            return {"status": "success", "python_code": python_code}

      
        # TODO Step 3: Testing
        # TODO Step 4: Verification Loop

    
        