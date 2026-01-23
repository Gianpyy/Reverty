from agents.lexer_agent import Agent1Lexer
from agents.transpiler_agent import AgentTranspiler

def main():


    test_code = open('test_code.txt').read()
    agent_lexer = Agent1Lexer()
    result = agent_lexer.run(test_code)
    ast = result['ast']

    print(ast.pretty())  

    agent_transpiler = AgentTranspiler()
    result_python_code = agent_transpiler.run(ast)
    print(result_python_code['python_code'])


if __name__ == "__main__":
    main()
