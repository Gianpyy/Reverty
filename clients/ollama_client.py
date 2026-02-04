import requests
from clients.llm_client_abstract import LLMClient
from pprint import pprint
from config import LLM_TEMPERATURE


class OllamaClient(LLMClient):
    """
    LLM client using Ollama (local models).
    Requires Ollama to be installed and running.
    """

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.2"
    ):
        """
        Initialize Ollama client.
        """

        self.base_url = base_url
        self.model = model
        self.requests = requests

    def generate(
        self, user_prompt: str, system_prompt: str = None, model: str = None
    ) -> str:
        """
        Generate a response using Ollama.
        """

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": user_prompt})

            # Ollama API format
            payload = {
                "model": model or self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": LLM_TEMPERATURE,
                },
            }

            response = self.requests.post(
                f"{self.base_url}/api/chat", json=payload, timeout=120
            )

            if response.status_code != 200:
                error_msg = f"Ollama API error {response.status_code}: {response.text}"
                print(f"[OllamaClient] {error_msg}")
                raise Exception(error_msg)

            result = response.json()
            pprint(result)
            return result.get("message", {}).get("content", "")

        except Exception as e:
            error_msg = f"Error calling Ollama API: {e}"
            print(f"[OllamaClient] {error_msg}")
            raise Exception(error_msg)
