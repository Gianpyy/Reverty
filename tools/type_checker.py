from helpers.enums import AnalysisResult, Status
from helpers.utils import build_errors_string
import tempfile
import subprocess
import os
import sys


class TypeChecker:
    """
    Wrapper class for Mypy.
    """

    def run(self, code: str) -> AnalysisResult:
        """Runs mypy on the provided code string."""

        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            print(f"[TypeChecker] Running mypy on {tmp_path}...", flush=True)
            # Run mypy using current python interpreter
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    tmp_path,
                    "--ignore-missing-imports",
                    "--no-strict-optional",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            print(
                f"[TypeChecker] MyPy finished with code {result.returncode}", flush=True
            )

            # Return critical errors and package not installed error
            if result.stderr:
                if "No module named mypy" in result.stderr:
                    print(
                        "[TypeChecker] MyPy is not installed, run pip install mypy: ",
                        result.stderr,
                    )
                    return AnalysisResult(Status.ERROR, message="MyPy not installed")
                print("[TypeChecker] Critical error: ", result.stderr)
                return AnalysisResult(Status.ERROR, message="Critical error")

            # Mypy returns 0 on success
            if result.returncode == 0:
                return AnalysisResult(Status.SUCCESS, message="No errors found")

            errors = [
                line.replace(f"{tmp_path}:", "Line ")
                for line in result.stdout.splitlines()
                if "error" in line
            ]
            return AnalysisResult(Status.ERROR, message=build_errors_string(errors))

        except subprocess.TimeoutExpired:
            print("[TypeChecker] MyPy timed out")
            return AnalysisResult(Status.ERROR, message="MyPy timed out")
        finally:
            os.unlink(tmp_path)
