import requests
from config import github_token
from clients.llm_client_abstract import LLMClient


class GitHubModelsClient(LLMClient):
    """
    LLM client using GitHub Models API.
    """

    def __init__(self, temperature: float = 0.3, api_key: str = None):
        self.github_token = api_key
        self.base_url = "https://models.github.ai"
        self.requests = requests
        self.temperature = temperature

    def generate(
        self, user_prompt: str, system_prompt: str = None, model: str = "gpt-4o"
    ) -> str:
        """
        Generate a response using GitHub Models API.
        """

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": user_prompt})

            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            payload = {
                "model": model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": 4000,
            }

            response = self.requests.post(
                f"{self.base_url}/inference/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code != 200:
                error_msg = (
                    f"GitHub Models API error {response.status_code}: {response.text}"
                )
                print(f"[GitHubModelsClient] {error_msg}")
                raise Exception(error_msg)

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"[GitHubModelsClient] Error calling GitHub Models API: {e}")
            raise
