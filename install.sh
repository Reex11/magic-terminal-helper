#!/usr/bin/env zsh
# Install magic-terminal

set -euo pipefail

SCRIPT_DIR="${0:a:h}"
MARKER="# magic-terminal zsh function"

echo "Installing magic-terminal via pipx..."
pipx install "$SCRIPT_DIR" || pipx install "$SCRIPT_DIR" --force

# Append zsh function to ~/.zshrc (idempotent)
if ! grep -qF "$MARKER" ~/.zshrc 2>/dev/null; then
  cat >> ~/.zshrc << 'ZSHFUNC'

# magic-terminal zsh function
magic() {
  local _magic_tmp
  _magic_tmp=$(mktemp /tmp/magic_cmd.XXXXXX)
  magic-run --output "$_magic_tmp" "$@"
  local _magic_exit=$?
  if [[ $_magic_exit -eq 0 && -s "$_magic_tmp" ]]; then
    local _magic_cmd
    _magic_cmd=$(cat "$_magic_tmp")
    echo "+ $_magic_cmd"
    eval "$_magic_cmd"
  fi
  rm -f "$_magic_tmp"
}
ZSHFUNC
  echo "Added magic() function to ~/.zshrc"
else
  echo "magic() function already in ~/.zshrc"
fi

echo ""
echo "Done! Run: source ~/.zshrc"
