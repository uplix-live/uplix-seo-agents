#!/usr/bin/env bash
# Installation des agents SEO Uplix pour Claude Code (macOS / Linux)
# Usage : ./install.sh            -> installe dans ~/.claude/skills (global)
#         ./install.sh --project  -> installe dans .claude/skills du dossier courant
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skills"

if [[ "${1:-}" == "--project" ]]; then
  DEST="$(pwd)/.claude/skills"
else
  DEST="$HOME/.claude/skills"
fi

echo "Installation des skills vers $DEST ..."
mkdir -p "$DEST"
for d in "$SRC"/*/; do
  name="$(basename "$d")"
  rm -rf "${DEST:?}/$name"
  cp -r "$d" "$DEST/$name"
  echo "  + $name"
done

echo
echo "Installation des dependances Python ..."
python3 -m pip install -r "$(dirname "$0")/requirements.txt"
python3 -m playwright install chromium

echo
echo "Termine."
echo "1. Copier .mcp.json.example -> .mcp.json a la racine de votre projet et renseigner vos cles."
echo "2. Copier .env.example -> .env pour les scripts Python."
echo "3. Relancer Claude Code puis tester : /agent-technique example.fr"
