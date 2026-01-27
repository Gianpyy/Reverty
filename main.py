from orchestrator import Orchestrator


def main():
    orchestrator = Orchestrator(use_mock=True)
    orchestrator.run("Write a function that calculates the factiorial of a number.")


if __name__ == "__main__":
    main()
