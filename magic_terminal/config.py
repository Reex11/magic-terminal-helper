"""Load configuration from ~/.config/magic/config.toml or environment variables."""

import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
  model: str
  ollama_url: str
  num_gpu: int | None = None


_CONFIG_PATH = Path.home() / ".config" / "magic" / "config.toml"

_EXAMPLE = """\
Configuration required. Create ~/.config/magic/config.toml:

  [ollama]
  model = "qwen2.5-coder:7b"
  url   = "http://localhost:11434"

Or set environment variables:

  export MAGIC_MODEL="qwen2.5-coder:7b"
  export MAGIC_OLLAMA_URL="http://localhost:11434"
"""


def load_config() -> Config:
  model: str | None = None
  ollama_url: str | None = None

  num_gpu: int | None = None

  if _CONFIG_PATH.exists():
    with open(_CONFIG_PATH, "rb") as f:
      data = tomllib.load(f)
    ollama = data.get("ollama", {})
    model = ollama.get("model")
    ollama_url = ollama.get("url")
    num_gpu = ollama.get("num_gpu")

  # Env vars override file values
  model = os.environ.get("MAGIC_MODEL", model)
  ollama_url = os.environ.get("MAGIC_OLLAMA_URL", ollama_url)
  if "MAGIC_NUM_GPU" in os.environ:
    num_gpu = int(os.environ["MAGIC_NUM_GPU"])

  if not model or not ollama_url:
    print(_EXAMPLE, file=sys.stderr)
    sys.exit(2)

  return Config(model=model, ollama_url=ollama_url, num_gpu=num_gpu)
