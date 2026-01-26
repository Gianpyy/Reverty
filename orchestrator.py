from helpers.ast_printer import print_ast
from agents.parser_agent import ParserAgent
from agents.transpiler_agent import TranspilerAgent
from agents.architect_agent import ArchitectAgent
from clients.mock_llm_client import MockLLMClient


class Orchestrator:
    """
    Orchestrator class.
    """

    def __init__(
        self,
        use_mock: bool = False,
    ):
        """
        Initialize the Orchestrator.

        Args:
            use_mock: If True, use MockLLMClient. If None, use config.USE_MOCK
            api_key: API key for OpenAI. If None, use config.OPENAI_API_KEY
            github_token: GitHub Personal Access Token for GitHub Models API
            use_ollama: If True, use local Ollama
        """
        if use_mock:
            print("[Orchestrator] Using MOCK LLM")
            self.client = MockLLMClient()

        self.architect = ArchitectAgent(self.client)
        self.parser = ParserAgent(self.client)
        self.transpiler = TranspilerAgent(self.client)

    def run(self, user_prompt: str):
        """
        Main orchestrator loop.
        """
        print("[Orchestrator] Starting execution for \n", user_prompt)

        # Parser agent
        result = self.parser.run(user_prompt)
        if result["status"] == "error":
            error_message = result["message"]
            print("[Orchestrator] Error in Parser Agent: {error_message}")
            return {"status": "error", "message": error_message}
        else:
            ast = result["ast"]
            print("[Orchestrator] AST generated correctly\n")
            print_ast(ast)

        # Transpiler agent
        result_python_code = self.transpiler.run(ast)
        if result_python_code["status"] == "error":
            error_message = result_python_code["message"]
            print("[Orchestrator] Error in Transpiler Agent: {error_message}")
            return {"status": "error", "message": error_message}
        else:
            python_code = result_python_code["python_code"]
            print("[Orchestrator] Python code generated correctly\n")
            print(python_code)
            return {"status": "success", "python_code": python_code}
