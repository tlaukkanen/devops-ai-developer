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
            return result.stdout.strip() or "Command executed successfully with no output."
        else:
            return f"Error (code {result.returncode}): {result.stderr.strip()}"
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
