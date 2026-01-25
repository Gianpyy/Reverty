from lark import Transformer


class TranspilerAgent:
    """
    Agent 3: The Transpiler (Lark -> Python).
    Converts ReversePy AST to Python 3 code.
    """

    class ReversePyToPython(Transformer):
        # --- Gestione dei Blocchi ---
        def start(self, items):
            return "\n".join([str(i) for i in items if i is not None]).strip()

        def suite(self, items):
            indented_lines = []
            for item in items:
                # Gestisce item che potrebbero essere già stringhe multi-riga
                for line in str(item).split("\n"):
                    if line.strip():
                        indented_lines.append("    " + line)
                    else:
                        indented_lines.append(line)
            return "\n".join(indented_lines)

        # --- Definizioni di Funzione ---
        def func_def(self, items):
            # Grammatica: "fed" NAME "(" [params] ")" "->" type_hint ":" suite
            # Lark scarta i letterali stringa ("fed", "(", ")", "->", ":")
            # Items: [NAME, params, type_hint, suite]
            return_type, params, name, body = items
            params_str = params if params is not None else ""
            return f"def {name}({params_str}) -> {return_type}:\n{body}"

        def params(self, items):
            return ", ".join(items)

        def param(self, items):
            # NAME ":" type_hint
            return f"{items[1]}: {items[0]}"

        # --- Istruzioni di Controllo ---
        def conditional_stmt(self, items):
            # Unisce if, elif ed else
            return "\n".join(items)

        def if_stmt(self, items):
            # Grammatica: ":" expr "fi" suite
            # Items: [expr, suite]
            condition, body = items
            return f"if {condition}:\n{body}"

        def elif_stmt(self, items):
            # Grammatica: ":" expr "file" suite
            # Items: [expr, suite]
            condition, body = items
            return f"elif {condition}:\n{body}"

        def else_stmt(self, items):
            # Grammatica: ":" "esle" suite
            # Items: [suite]
            body = items[0]
            return f"else:\n{body}"

        def while_stmt(self, items):
            # Grammatica: ":" expr "elihw" suite
            # Items: [expr, suite]
            condition, body = items
            return f"while {condition}:\n{body}"

        def for_stmt(self, items):
            # Grammatica: ":" loop_expr "ni" NAME "rof" suite
            # Items: [loop_expr, NAME, suite]
            iterable = str(items[0])
            var_name = str(items[1])
            body = items[2]

            return f"for {var_name} in {iterable}:\n{body}"

        # --- Gestione Loop Expressions ---
        def range_expr(self, items):
            # items: [NUMBER] oppure [func_call]
            # Lark scarta "range", "(" e ")" se sono letterali stringa
            param = str(items[0])
            return f"range({param})"

        def loop_expr(self, items):
            # items[0] può essere una STRING o il risultato di range()
            return str(items[0])

        # --- Chiamate di Funzione ed Espressioni ---
        def func_call(self, items):
            # items: [NAME, arguments]
            name, args = items
            args_str = args if args is not None else ""
            return f"{name}({args_str})"

        def arguments(self, items):
            return ", ".join(str(i) for i in items)

        def assign_stmt(self, items):
            # NAME ":" type_hint "=" expr
            name, type_h, expression = items
            return f"{name}: {type_h} = {expression}"

        def return_stmt(self, items):
            # "nruter" [expr]
            val = items[0] if items else ""
            return f"return {val}".strip()

        def expr_stmt(self, items):
            return str(items[0])

        # Aggiungi questi all'interno di ReversePyToPython
        def comp_op(self, items):
            # Estrae il valore testuale dal Token all'interno del Tree
            return str(items[0].value)

        def add_op(self, items):
            return str(items[0].value)

        def mul_op(self, items):
            return str(items[0].value)

        # --- Mapping dei Tipi ---
        def type_int(self, _):
            return "int"

        def type_str(self, _):
            return "str"

        def type_bool(self, _):
            return "bool"

        def type_none(self, _):
            return "None"

        def type_float(self, _):
            return "float"

        # --- Operazioni Logiche e Matematiche ---
        def logic_or(self, items):
            return " or ".join(str(i) for i in items)

        def logic_and(self, items):
            return " and ".join(str(i) for i in items)

        def not_expr(self, items):
            # items: [expr] (perché "ton" è scartato se non nominato come token)
            return f"not {items[0]}"

        def comparison(self, items):
            return " ".join(str(i) for i in items)

        def sum(self, items):
            return " ".join(str(i) for i in items)

        def product(self, items):
            return " ".join(str(i) for i in items)

        # --- Atomi ---
        def number(self, items):
            return str(items[0])

        def string(self, items):
            return str(items[0])

        def true(self, _):
            return "True"

        def false(self, _):
            return "False"

        def none(self, _):
            return "None"

        def var(self, items):
            return str(items[0])

    def __init__(self):
        pass

    def run(self, ast):
        try:
            print("[Transpiler] Starting conversion to python code...")
            transpiler = self.ReversePyToPython()
            python_code = transpiler.transform(ast)
            print("[Transpiler] Conversion complete.")
            return {"status": "success", "python_code": python_code}
        except Exception as e:
            print("[Transpiler] Error: {e}")
            return {"status": "error", "message": str(e)}
