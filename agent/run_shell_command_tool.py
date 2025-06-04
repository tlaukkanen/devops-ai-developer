import subprocess
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class RunShellCommandInput(BaseModel):
    command: str = Field(..., description="The shell command to execute.")
    cwd: str | None = Field(None, description="Optional working directory to run the command in.")

def run_shell_command(command: str, cwd: str | None = None) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            # Make sure that the output doesn't exceed 20k characters
            # Display first 20k characters if it does
            if len(result.stdout) > 20000:
                return f"Output too long to display (exceeds 20,000 characters). First 20,000 characters:\n{result.stdout[:20000]}"
            return result.stdout.strip() or "Command executed successfully with no output."
        else:
            # Make sure that the error output doesn't exceed 20k characters
            # Display first 20k characters if it does
            if len(result.stderr) > 20000:
                return f"Error output too long to display (exceeds 20,000 characters). First 20,000 characters:\n{result.stderr[:20000]}"
            return f"Error (code {result.returncode}): {result.stdout.strip()}\n{result.stderr.strip()}"
    except Exception as e:
        return f"Exception while running command: {e}"

class RunShellCommandTool(StructuredTool):
    def __init__(self):
        super().__init__(
            func=run_shell_command,
            name="run_shell_command",
            description="Run a shell command on the local system. Accepts 'command' (str) and optional 'cwd' (str) for working directory.",
            args_schema=RunShellCommandInput,
        )
