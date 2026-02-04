from helpers.enums import Status
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

        print("[Tester] Testing...")
        print("[Tester] Python code: \n", python_code)
        print("[Tester] Tests: \n", tests)

        # Run tests
        test_result = self.executor.run_tests(python_code, tests)

        print("[Tester] Test result in run tests: ", test_result)
        if test_result.status == Status.SUCCESS:
            return {
                "status": Status.SUCCESS.value,
                "message": "Tests passed successfully.",
            }
        else:
            error_output = test_result.code_failures
            failed_tests = test_result.failed_tests

            tester_prompt = generate_tester_request(
                contract, python_code, reverty_code, tests, failed_tests, error_output
            )

            response = self.client.generate(
                user_prompt=tester_prompt, system_prompt=TESTER_SYSTEM_PROMPT
            )

            response_json = self._extract_json(response)

            final_result = {
                "status": Status.ERROR.value,
                "code_failures": response_json.get("code_failures")
                if response_json.get("code_failures") != ""
                else None,
                "test_failures": response_json.get("test_failures")
                if response_json.get("test_failures") != ""
                else None,
            }

        return final_result
