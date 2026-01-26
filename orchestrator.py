from helpers.ast_printer import print_ast
from agents.parser_agent import ParserAgent
from agents.transpiler_agent import TranspilerAgent


class Orchestrator:
    """
    Orchestrator class.
    """

    def __init__(self):
        """
        Initialize the Orchestrator.
        """
        self.parser = ParserAgent()
        self.transpiler = TranspilerAgent()

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
