from dotenv import load_dotenv
import os

load_dotenv()

grammar_path = "grammar.lark"
github_token = os.getenv("GITHUB_TOKEN")

MAX_VALIDATION_ITERATIONS = 3
MAX_EVALUATION_RETRIES = 3
MAX_ORCHESTRATOR_ITERATIONS = 3

OLLAMA_LLM_MODEL = "llama3.2"
LLM_TEMPERATURE = 0.3

