from lark import Lark
from lark.indenter import Indenter

class ReversePyIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['(']
    CLOSE_PAREN_types = [')']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

class Agent1Lexer:
    """
    Lexer Agent: Syntax Validator & Lexer.
    Uses Lark to validate the input structure.
    """
    def __init__(self, grammar_path="grammar.lark"):
        with open(grammar_path, "r") as f:
            self.grammar = f.read()
            
        self.parser = Lark(self.grammar, parser='lalr', postlex=ReversePyIndenter(), start='start')

    def run(self, code: str):
        print(f"[Lexer Agent] Validating Syntax...")
        try:
            if not code.endswith('\n'):
                code = code.strip() + "\n"
            
            tree = self.parser.parse(code)
            print(f"[Lexer Agent] Syntax OK! Tree generated.")
            return {"status": "success", "code": code, "ast_debug": tree.pretty()}
            
        except Exception as e:
            print(f"[Lexer Agent] Syntax Error: {e}")
            return {"status": "error", "message": str(e)}
