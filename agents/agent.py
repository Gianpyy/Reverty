from pprint import pprint
from toon_format import DecodeOptions
from typing import Dict, Any
import json
from toon_format import encode, decode

class Agent:
    """
    Base class for all agents.
    """

    def __init__(self, client):
        self.client = client
        self.on_log = None

    def set_logger(self, on_log):
        """
        Sets the logging callback.
        """
        self.on_log = on_log

    def log(self, message: str):
        """
        Logs a message using the callback if available, otherwise prints it.
        """
        if self.on_log:
            self.on_log(message)
        print(message)

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Robustly extracts JSON from a string, handling markdown and extra text."""

        print(f"[EXTRACT JSON] Response: {response}")

        # 1. Try direct parsing a JSON object
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 2. Try extracting from markdown code blocks
        try:
            if "```json" in response:
                block = response.split("```json")[1].split("```")[0].strip()
                return json.loads(block)
            elif "```reverty" in response:
                block = response.split("```reverty")[1].split("```")[0].strip()
                json_block = {"code": block}
                return json_block
            elif "```python" in response:
                block = response.split("```python")[1].split("```")[0].strip()
                json_block = {"code": block}
                return json_block
            elif "```toon" in response:
                block = response.split("```toon")[1].split("```")[0].strip()
                object = decode(block, DecodeOptions(indent=4, strict=False)) # TODO: extract function
                return object
            elif "```" in response:
                block = response.split("```")[1].split("```")[0].strip()
                return json.loads(block)
            else:
                json_block = {"code": response}
                return json_block
        except json.JSONDecodeError:
            pass
            
        # 3. Try finding the first '{' and last '}' (greedy)
        try:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                json_str = response[start : end + 1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # 4. Try finding the largest valid JSON object (nested braces)
        # This is a heuristic for when the model outputs multiple JSON-like things
        try:
            stack = []
            start_idx = -1
            for i, char in enumerate(response):
                if char == "{":
                    if not stack:
                        start_idx = i
                    stack.append(char)
                elif char == "}":
                    if stack:
                        stack.pop()
                        if not stack:
                            # Found a complete top-level object
                            try:
                                return json.loads(response[start_idx : i + 1])
                            except json.JSONDecodeError:
                                continue  # Keep looking
        except Exception:
            pass

        # If all fails, raise error to be handled by caller
        raise json.JSONDecodeError("Could not extract JSON from response", response, 0)
