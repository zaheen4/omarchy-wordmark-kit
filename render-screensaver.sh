#!/bin/bash
#
# render-screensaver.sh "WORD" [--apply]
#
# Render WORD as ASCII art for the Omarchy screensaver / About screen.
#
#   WORD      letters and spaces only
#   --apply   install to ~/.config/omarchy/branding/screensaver.txt
#             (honors XDG_CONFIG_HOME) and preview it immediately.
#             Without --apply the art goes to stdout.
#
# Examples:
#   ./render-screensaver.sh "COSMOS" > art.txt
#   ./render-screensaver.sh "COSMOS" --apply
#
# Revert with: omarchy branding screensaver reset
# Dependencies: bash, awk.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_ASCII="$SCRIPT_DIR/lib/omarchy-ascii-vendor"

usage() {
  sed -n '2,17p' "$SCRIPT_DIR/render-screensaver.sh" | sed 's/^# \{0,1\}//'
}

APPLY=0
ARGS=()
while (($# > 0)); do
  case "$1" in
  --apply)
    APPLY=1
    shift
    ;;
  -h | --help)
    usage
    exit 0
    ;;
  *)
    ARGS+=("$1")
    shift
    ;;
  esac
done

if ((${#ARGS[@]} != 1)); then
  usage >&2
  exit 1
fi

WORD="${ARGS[0]}"
if [[ -z ${WORD//[[:space:]]/} ]]; then
  echo "Nothing to render." >&2
  exit 1
fi

if command -v omarchy >/dev/null 2>&1 && omarchy ascii --help >/dev/null 2>&1; then
  ASCII_CMD=(omarchy ascii)
else
  ASCII_CMD=(bash "$VENDOR_ASCII")
fi

if ((APPLY)); then
  DEST="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/branding/screensaver.txt"
  mkdir -p "$(dirname "$DEST")"
  if ! "${ASCII_CMD[@]}" "$WORD" >"$DEST" 2>"$DEST.err"; then
    cat "$DEST.err" >&2
    rm -f "$DEST.err"
    exit 1
  fi
  if [[ -s $DEST.err ]]; then
    cat "$DEST.err" >&2
  fi
  rm -f "$DEST.err"
  echo "Screensaver set: $DEST"
  if command -v omarchy >/dev/null 2>&1; then
    omarchy launch screensaver force >/dev/null 2>&1 || true
  fi
else
  "${ASCII_CMD[@]}" "$WORD"
fi
