from config import grammar_path
from lark import Tree
from typing import List
import streamlit_antd_components as sac

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

def parse_ast_string_to_sac(ast_string):
    """
    Converts a Lark AST string into sac.TreeItem objects for rendering in the UI.
    Each line is parsed based on indentation to reconstruct the tree hierarchy.
    """
    lines = ast_string.strip().split('\n')
    if not lines:
        return []

    items = []
    stack = []

    for line in lines:
        indent = len(line) - len(line.lstrip())  # Count indentation spaces
        name = line.strip().replace('|--', '').replace('`--', '').replace('|', '').strip()
        
        new_item = sac.TreeItem(label=name)
        
        if indent == 0:
            items.append(new_item)
            stack = [(0, new_item)]
        else:
            while stack and stack[-1][0] >= indent:
                stack.pop()
            
            if stack:
                parent = stack[-1][1]
                if parent.children is None:
                    parent.children = []
                parent.children.append(new_item)
            
            stack.append((indent, new_item))
            
    return items