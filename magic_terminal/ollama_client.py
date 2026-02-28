"""Call Ollama and stream the response."""

import sys

import ollama


def generate(
  messages: list[dict[str, str]],
  model: str,
  url: str,
  num_gpu: int | None = None,
) -> str:
  client = ollama.Client(host=url)
  chunks: list[str] = []
  kwargs: dict = {"model": model, "messages": messages, "stream": True}
  if num_gpu is not None:
    kwargs["options"] = {"num_gpu": num_gpu}
  try:
    stream = client.chat(**kwargs)
    for chunk in stream:
      token = chunk["message"]["content"]
      chunks.append(token)
      sys.stderr.write(token)
      sys.stderr.flush()
    sys.stderr.write("\n")
  except ollama.ResponseError as e:
    if e.status_code == 404:
      print(f"Model not found. Run: ollama pull {model}", file=sys.stderr)
    else:
      print(f"Ollama error: {e}", file=sys.stderr)
    sys.exit(1)
  except Exception as e:
    msg = str(e)
    if "Connection refused" in msg or "ConnectError" in msg:
      print("Cannot connect to Ollama. Is it running?", file=sys.stderr)
    else:
      print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

  return "".join(chunks).strip()
