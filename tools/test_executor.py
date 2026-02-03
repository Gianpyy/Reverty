from helpers.utils import build_errors_string
from helpers.enums import Status
import sys
import subprocess
import os
from helpers.enums import ExecutionResult
import tempfile

class TestExecutor:
    """
    Runs tests in a sandboxed environment (subprocess) and parses results.
    """
    def __init__(self, work_dir: str = "."):
        self.work_dir = work_dir

    def run_tests(self, python_code: str, tests: str) -> ExecutionResult:
        """
        Writes code and tests to disk, runs pytest, and returns the result.
        """

        print("[EXECUTOR] Running tests...\n", tests)
        print("[EXECUTOR] Python code...\n", python_code)

        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Write files
            impl_path = os.path.join(temp_dir, "implementation.py")
            test_path = os.path.join(temp_dir, "tests.py")
            
            with open(impl_path, "w") as f:
                f.write(python_code)
            
            with open(test_path, "w") as f:
                f.write(tests)
                
            # 2. Run Pytest
            try:
                # Run pytest on the test file
                # -q: quiet
                # --tb=short: shorter traceback
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_path, "-q", "--tb=short"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )
                
                # Check if pytest was actually found/run
                #if "No module named pytest" in result.stderr:
                #   return self._mock_run_tests(code, tests)
                
                success = result.returncode == 0
                output = result.stdout + result.stderr

                print("[EXECUTOR] stdout:", result.stdout)
                print("[EXECUTOR] output:", result.stderr)
                print("[EXECUTOR] return code:", result.returncode)

                
                failed_tests = self._parse_failures(output) if not success else []
                
                return ExecutionResult(
                    status=Status.SUCCESS if success else Status.ERROR,
                    code_failures=output,
                    failed_tests=failed_tests
                )
            
            except Exception as e:
                #return self._mock_run_tests(code, tests)
                raise e
    
    def _parse_failures(self, output: str) -> str:
        """
        Parses pytest output to find names of failed tests.
        Simple heuristic: looks for 'F' or 'FAILED' lines.
        """
        failures = []
        for line in output.splitlines():
            if "FAILED" in line and "::" in line:
                # Example: tests.py::test_factorial_negative FAILED
                parts = line.split("::")
                if len(parts) > 1:
                    test_name = parts[1].split(" ")[0]
                    failures.append(test_name)
        
        return build_errors_string(failures)