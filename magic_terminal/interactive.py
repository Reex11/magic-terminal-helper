"""Interactive TUI for reviewing the generated command."""

import os
import select
import sys
import termios
import tty


def _read_key(fd: int) -> str:
  """Read a single keypress, handling escape sequences."""
  ch = os.read(fd, 1)
  if ch == b"\x1b":
    # Check if more bytes follow (arrow key sequence) within 50ms
    r, _, _ = select.select([fd], [], [], 0.05)
    if r:
      # Consume the rest of the escape sequence
      seq = os.read(fd, 8)
      return "escape_seq"
    return "esc"
  if ch in (b"\r", b"\n"):
    return "enter"
  if ch == b" ":
    return "space"
  return "other"


def _edit_command(command: str, tty_fd: int) -> str | None:
  """Open prompt_toolkit editor pre-filled with the command."""
  # Import here to avoid startup cost when not needed
  from prompt_toolkit import PromptSession
  from prompt_toolkit.input import create_input
  from prompt_toolkit.key_binding import KeyBindings
  from prompt_toolkit.output import create_output

  tty_in = open("/dev/tty", "r")
  tty_out = open("/dev/tty", "w")

  bindings = KeyBindings()

  @bindings.add("escape")
  def _(event):
    event.app.exit(result=None)

  session = PromptSession(
    key_bindings=bindings,
    input=create_input(tty_in),
    output=create_output(tty_out),
  )
  try:
    result = session.prompt("Edit: ", default=command)
    return result if result else None
  except (EOFError, KeyboardInterrupt):
    return None
  finally:
    tty_in.close()
    tty_out.close()


def interact(command: str) -> str | None:
  """Show the command and prompt the user to run, edit, or cancel.

  Returns the command to execute, or None if cancelled.
  """
  try:
    tty_fd = os.open("/dev/tty", os.O_RDWR)
  except OSError:
    print("Cannot open /dev/tty", file=sys.stderr)
    return None

  tty_file = os.fdopen(os.dup(tty_fd), "w")
  try:
    tty_file.write(f"\n  \033[1;32m{command}\033[0m\n\n")
    tty_file.write("  [Enter] run  [Space] edit  [Esc] cancel\n")
    tty_file.flush()

    old_attrs = termios.tcgetattr(tty_fd)
    try:
      tty.setraw(tty_fd)
      key = _read_key(tty_fd)
    finally:
      termios.tcsetattr(tty_fd, termios.TCSADRAIN, old_attrs)

    # Clear the prompt line
    tty_file.write("\n")
    tty_file.flush()

    if key == "enter":
      return command
    elif key == "space":
      return _edit_command(command, tty_fd)
    else:
      return None
  finally:
    tty_file.close()
    os.close(tty_fd)
