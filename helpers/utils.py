from config import grammar_path
from lark import Tree

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
