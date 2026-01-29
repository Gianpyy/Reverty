from typing import List
import tempfile
import subprocess
import sys
import os
from helpers.enums import AnalysisResult, Status


class Linter:
    """
    Wrapper class for Flake8.
    """

    def _build_errors_string(self, errors: List[str]) -> str:
        """Builds a string from a list of errors."""
        return "\n".join(errors)

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
            return AnalysisResult(
                status=Status.ERROR, message=self._build_errors_string(errors)
            )

        except FileNotFoundError:
            return AnalysisResult(
                status=Status.ERROR,
                message="Flake8 not installed, run pip install flake8",
            )
        except subprocess.TimeoutExpired:
            return AnalysisResult(status=Status.ERROR, message="Flake8 timed out")
        finally:
            os.unlink(tmp_path)
