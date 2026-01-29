from orchestrator import Orchestrator


def main():
    orchestrator = Orchestrator(use_mock=True)
    result = orchestrator.run(
        "Write a function that calculates the factiorial of a number."
    )
    print(result["code"])


if __name__ == "__main__":
    main()
