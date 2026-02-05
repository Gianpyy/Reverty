from config import grammar_path
from lark import Tree
from typing import List


def load_grammar():
    """Loads the grammar from the configured file."""

    with open(grammar_path, "r") as file:
        return file.read()


def print_ast(node, indent="", last=True):
    """
    Prints the Abstract Syntax Tree (AST) in a human-readable format.

    Args:
        node: The AST node to print.
        indent: The indentation level.
        last: Whether the node is the last child of its parent.
    """
    prefix = "└── " if last else "├── "
    if isinstance(node, Tree):
        print(indent + prefix + node.data)
        indent += "    " if last else "│   "
        for i, child in enumerate(node.children):
            print_ast(child, indent, last=(i == len(node.children) - 1))
    else:
        print(indent + prefix + str(node))

def print_ast_string(ast_tree: Tree) -> str:
    """
    Prints the Abstract Syntax Tree (AST) as String.
    """
    ast_string = ast_tree.pretty()
    return ast_string


def build_errors_string(errors: List[str]) -> str:
    """Builds a string from a list of errors."""
    return "\n".join(errors)
