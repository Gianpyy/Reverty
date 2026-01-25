from lark import Tree


def print_ast(node, indent="", last=True):
    prefix = "└── " if last else "├── "
    if isinstance(node, Tree):
        print(indent + prefix + node.data)
        indent += "    " if last else "│   "
        for i, child in enumerate(node.children):
            print_ast(child, indent, last=(i == len(node.children) - 1))
    else:
        print(indent + prefix + str(node))
