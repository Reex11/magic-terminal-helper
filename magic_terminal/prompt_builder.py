"""Build the message list for the Ollama chat API."""

from magic_terminal.context import get_context

_SYSTEM_TEMPLATE = """\
You are a zsh command generator. Convert natural language to a single zsh command.
Rules:
- Output ONLY the raw command. Nothing else.
- No backticks, no markdown, no explanation, no comments.
- If ambiguous, use the most common reasonable interpretation.
- Valid zsh syntax required.

Shell context:
  cwd: {cwd}  home: {home}  user: {user}  shell: {shell}  PATH: {path}"""


def build_messages(natural_language: str) -> list[dict[str, str]]:
  ctx = get_context()
  system = _SYSTEM_TEMPLATE.format(**ctx)
  return [
    {"role": "system", "content": system},
    {"role": "user", "content": natural_language},
  ]
