from orchestrator import Orchestrator
from helpers.enums import LLMClientType

def main():
    
    orchestrator = Orchestrator(LLMClientType.OLLAMA)
    result = orchestrator.run(
        "Write a function that calculates the factiorial of a number."
    )
    print(result["code"])


if __name__ == "__main__":
    main()
