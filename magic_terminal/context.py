"""Gather shell context for the LLM prompt."""

import os
from pathlib import Path


def get_context() -> dict[str, str]:
  return {
    "cwd": os.getcwd(),
    "home": str(Path.home()),
    "user": os.environ.get("USER", "unknown"),
    "shell": os.environ.get("SHELL", "/bin/zsh"),
    "path": os.environ.get("PATH", ""),
  }
