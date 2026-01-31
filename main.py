from orchestrator import Orchestrator
from helpers.enums import LLMClientType

def main():
    
    orchestrator = Orchestrator(LLMClientType.GITHUB_MODELS)
    result = orchestrator.run(
        "Write a function that calculates the factorial of a number."
    )
    print(result["code"])


if __name__ == "__main__":
    main()
