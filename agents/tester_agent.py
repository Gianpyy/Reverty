from helpers.enums import Status, ExecutionResult
from typing import Dict, Any
from agents.agent import Agent
from helpers.system_prompts import TESTER_SYSTEM_PROMPT
from helpers.prompt_generator import generate_tester_request
from tools.test_executor import TestExecutor

class TesterAgent(Agent):
    """
    Analyzes test failures and refines either the code or tests.
    """

    def __init__(self, client):
        super().__init__(client)
        self.executor = TestExecutor()

    def test(self, contract: Dict[str, Any], python_code: str, reverty_code: str, tests: str) -> Dict[str, Any]:
        """
        Analyzes test failures and notifies issues with either the code or tests.
        """

        self.log("[Tester Agent] Testing...")
        self.log(f"[Tester Agent] Python code: \n{python_code}")
        self.log(f"[Tester Agent] Tests: \n{tests}")

        # Run tests
        test_result: ExecutionResult = self.executor.run_tests(python_code, tests)

        self.log(f"[Tester Agent] Test result in run tests: {test_result.status.value}")
        if test_result.status == Status.SUCCESS:
            return {
                "status": Status.SUCCESS.value,
                "message": "Tests passed successfully.",
            }
        else:
            error_output: str = test_result.code_failures
            failed_tests: str = test_result.failed_tests

            tester_prompt: str = generate_tester_request(
                contract, python_code, reverty_code, tests, failed_tests, error_output
            )

            response_raw: str = self.client.generate(
                user_prompt=tester_prompt, system_prompt=TESTER_SYSTEM_PROMPT
            )

            response: Dict[str, Any] = self.extract_response(response_raw)

            final_result: Dict[str, Any] = {
                "status": Status.ERROR.value,
                "code_failures": response.get("code_failures") if response.get("code_failures") != "" else None,
                "test_failures": response.get("test_failures") if response.get("test_failures") != "" else None,
            }

        return final_result
