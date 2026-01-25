from orchestrator import Orchestrator


def main():
    test_code = open("test_code.txt").read()
    orchestrator = Orchestrator()
    orchestrator.run(test_code)


if __name__ == "__main__":
    main()
