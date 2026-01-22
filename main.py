from agents.lexer_agent import Agent1Lexer


def main():


    test_code = open('test_code.txt').read()
    agent_lexer = Agent1Lexer()
    result = agent_lexer.run(test_code)
    print(result['ast_debug'])


if __name__ == "__main__":
    main()
