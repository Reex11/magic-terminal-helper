"""CLI entry point for magic-run."""

import argparse
import re
import sys
from pathlib import Path

from magic_terminal.config import load_config
from magic_terminal.interactive import interact
from magic_terminal.ollama_client import generate
from magic_terminal.prompt_builder import build_messages


def _strip_markdown(text: str) -> str:
  """Remove markdown code fences or inline backticks if the LLM added them."""
  # Remove ```lang\n...\n``` blocks
  m = re.search(r"```\w*\n(.+?)```", text, re.DOTALL)
  if m:
    return m.group(1).strip()
  # Remove inline backticks
  if text.startswith("`") and text.endswith("`"):
    return text.strip("`").strip()
  return text


def main() -> None:
  parser = argparse.ArgumentParser(
    prog="magic-run",
    description="Convert natural language to a zsh command via Ollama",
  )
  parser.add_argument("--output", required=True, type=Path, help="Tmpfile path for the resulting command")
  parser.add_argument("query", nargs="+", help="Natural language description")
  args = parser.parse_args()

  config = load_config()
  query = " ".join(args.query)
  messages = build_messages(query)
  command = generate(messages, config.model, config.ollama_url, config.num_gpu)
  command = _strip_markdown(command)

  chosen = interact(command)
  if chosen:
    args.output.write_text(chosen + "\n")


if __name__ == "__main__":
  main()
