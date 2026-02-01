from dotenv import load_dotenv
import os

load_dotenv()

grammar_path = "grammar.lark"
github_token = os.getenv("GITHUB_TOKEN")
