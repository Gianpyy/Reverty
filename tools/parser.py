from lark import Lark
from lark.indenter import Indenter
from typing import Dict, Any


class RevertyIndenter(Indenter):
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = ["("]
    CLOSE_PAREN_types = [")"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


class Parser:
    """
    Parser: Syntax Validator & Parser.
    Uses Lark to validate the input structure.
    """

    def __init__(self, grammar):
        self.parser = Lark(
            grammar, parser="lalr", postlex=RevertyIndenter(), start="start"
        )

    def run(self, code: str) -> Dict[str, Any]:
        """
        Parses the input code and returns the AST.
        """
        print("[Parser] Validating Syntax...")
        try:
            if not code.endswith("\n"):
                code = code.strip() + "\n"

            ast = self.parser.parse(code)
            print("[Parser] Syntax OK! Tree generated.")
            return {"status": "success", "ast": ast}

        except Exception as e:
            print(f"[Parser] Syntax Error: {e}")
            return {"status": "error", "message": str(e)}
