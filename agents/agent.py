from toon_format import DecodeOptions, decode
from typing import Dict, Any
import json
from textwrap import dedent

class Agent:
    """
    Base class for all agents.
    """

    def __init__(self, client):
        self.client = client

    def extract_response(self, response: str) -> Dict[str, Any]:
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
                return self._extract_toon(response)
            elif "```" in response:
                block = response.split("```")[1].split("```")[0].strip()
                return json.loads(block)
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

        # If all fails, return raw response as code
        return {"code": response}

    def _extract_toon(self, response: str) -> Dict[str, Any]:
        """
        Extracts and parses TOON content, handling indentation and whitespace safely.
        """
        try:
            # Isolate toon block
            raw_block = response.split("```toon")[1].split("```")[0]
            
            # Remove common line indentation
            clean_block = dedent(raw_block).strip()
            
            # Pass the clean block to the decoder
            return decode(clean_block, DecodeOptions(indent=4, strict=False))
            
        except Exception as e:
            print(f"[Evaluator Agent] Error decoding TOON: {e}")
            raise json.JSONDecodeError("Failed to parse TOON", response, 0)
