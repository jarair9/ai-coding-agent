import os
from pathlib import Path
import sys
import asyncio
import signal
import fnmatch

# Safety: List of blocked patterns
BLOCKED_COMMANDS = {
    "rm -rf /", "rm -rf ~", "rm -rf /*", "dd if=/dev/zero",
    "dd if=/dev/random", "mkfs", "fdisk", "parted",
    ":(){ :|:& };:", "chmod 777 /", "chmod -R 777",
    "shutdown", "reboot", "halt", "poweroff", "init 0", "init 6",
}

def is_dangerous(command: str) -> bool:
    cmd_lower = command.lower()
    return any(blocked in cmd_lower for blocked in BLOCKED_COMMANDS)

def _build_safe_env() -> dict[str, str]:
    env = os.environ.copy()
    # Patterns to exclude from the environment for security
    exclude_patterns = ["*KEY*", "*SECRET*", "*API_KEY*", "*TOKEN*"]
    
    keys_to_remove = [
        k for k in env.keys() 
        if any(fnmatch.fnmatch(k.upper(), pattern) for pattern in exclude_patterns)
    ]
    
    for k in keys_to_remove:
        del env[k]
    return env

async def shell(command: str, timeout: int = 120, cwd: str = "."):
    if is_dangerous(command):
        return {
            "success": False,
            "output": f"Blocked dangerous command: {command}",
            "error": "Dangerous command blocked",
            "exit_code": -1
        }

    cwd_path = Path(cwd).resolve()
    if not cwd_path.exists():
        return {
            "success": False,
            "output": f"Folder does not exist: {cwd}",
            "error": "Path error",
            "exit_code": -1
        }

    env = _build_safe_env()

    # Determine shell based on OS
    if sys.platform == "win32":
        shell_cmd = ["cmd.exe", "/c", command]
    else:
        shell_cmd = ["/bin/bash", "-c", command]

    # Spawn process
    process = await asyncio.create_subprocess_exec(
        *shell_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd_path,
        env=env,
        start_new_session=(sys.platform != "win32") # Only use on POSIX
    )

    try:
        stdout_data, stderr_data = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        if sys.platform != "win32":
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()
        await process.wait()
        return {
            "success": False,
            "output": f"Command timed out after {timeout}s",
            "error": "Timeout",
            "exit_code": -1
        }

    stdout = stdout_data.decode("utf-8", errors="replace").strip()
    stderr = stderr_data.decode("utf-8", errors="replace").strip()
    exit_code = process.returncode

    # Build structured output
    output = ""
    if stdout:
        output += stdout
    if stderr:
        output += f"\n--- stderr ---\n{stderr}"
    if exit_code != 0:
        output += f"\nExit code: {exit_code}"

    # Truncate if necessary (100 KB)
    if len(output) > 100 * 1024:
        output = output[: 100 * 1024] + "\n... [output truncated]"

    return {
        "success": exit_code == 0,
        "output": output,
        "error": stderr if exit_code != 0 else None,
        "exit_code": exit_code,
    }
# async def main():
#     # Use keyword argument 'cwd=' to explicitly assign the path
#     result = await shell("dir", cwd=r"C:\Users\JarairAhmad\Desktop\AI coding agent")
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())