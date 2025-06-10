import os
import subprocess
from subprocess import CompletedProcess
from typing import List, Tuple


class FileTypeMismatchError(Exception):
    """Raised when a path exists but is not a regular file."""
    pass


class FileAccessError(Exception):
    """Raised when a file cannot be accessed."""
    pass


def set_conversion(obj):
    """
    Recursively convert sets to lists for JSON serialization.
    """
    if isinstance(obj, dict):
        return {k: set_conversion(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [set_conversion(i) for i in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj


def check_file_access(path: str) -> None:
    """
    Checks is a given path is a file, exists, and is accessible.

    Args:
        path: The path to check

    Raises:
        FileTypeMismatchError: If the path exists but is not a file.
        FileNotFoundError: If the file does not exist.
        FileAccessError: If the file exists but is not readable.
    """
    if not os.path.isfile(path):
        raise FileTypeMismatchError(f"The path '{path}' is not a file.")
    elif not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist or could not be located.")
    elif not os.access(path, os.R_OK):
        raise FileAccessError(f"The file '{path}' is not accessible.")


def run_command(cmd: List[str]) -> Tuple[int, str]:
    """
    Runs a shell command using an argument list.

    Args:
        cmd: A list of command line arguments.

    Returns:
        The process's exit code and stdout.
    """
    result: CompletedProcess[str] = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return result.returncode, result.stdout
