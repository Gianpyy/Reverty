import tempfile
import subprocess
import sys
import os
from helpers.enums import AnalysisResult, Status
from helpers.utils import build_errors_string


class Linter:
    """
    Wrapper class for Flake8.
    """

    def run(self, code: str) -> AnalysisResult:
        """Runs flake8 on the provided code string."""
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            print(f"[Linter] Running flake8 on {tmp_path}...", flush=True)
            # Run flake8 using current python interpreter
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    tmp_path,
                    "--ignore=E501",
                ],  # Ignore line length for generated code
                capture_output=True,
                text=True,
                timeout=120,
            )
            print(f"[Linter] Flake8 finished with code {result.returncode}", flush=True)

            # Return critical errors and package not installed error
            if result.stderr:
                if "No module named flake8" in result.stderr:
                    print(
                        "[Linter] Flake8 is not installed, run pip install flake8: ",
                        result.stderr,
                    )
                    return AnalysisResult(Status.ERROR, message="Flake8 not installed")
                print("[Linter] Critical error: ", result.stderr)
                return AnalysisResult(Status.ERROR, message="Critical error")

            # No errors
            if result.returncode == 0:
                return AnalysisResult(
                    status=Status.SUCCESS, message="No linting errors found."
                )

            # Parse errors (strip filename)
            errors = [
                line.replace(f"{tmp_path}:", "Line ")
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            print(f"[Linter] Errors: {errors}")
            return AnalysisResult(
                status=Status.ERROR, message=build_errors_string(errors)
            )

        except subprocess.TimeoutExpired:
            print("[Linter] Flake8 timed out", flush=True)
            return AnalysisResult(status=Status.ERROR, message="Flake8 timed out")
        finally:
            os.unlink(tmp_path)
