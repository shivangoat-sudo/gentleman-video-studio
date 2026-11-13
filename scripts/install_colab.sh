#!/usr/bin/env bash
set -euo pipefail

WAN_GP_DIR="${1:-/content/WanGP}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_SRC="$REPO_DIR/plugins/wan2gp-gentleman-studio"
PLUGIN_DST="$WAN_GP_DIR/plugins/wan2gp-gentleman-studio"

if [ ! -d "$WAN_GP_DIR" ]; then
  echo "WanGP folder not found: $WAN_GP_DIR"
  echo "Clone the official repository first:"
  echo "git clone --depth 1 https://github.com/deepbeepmeep/WanGP.git $WAN_GP_DIR"
  exit 1
fi

mkdir -p "$WAN_GP_DIR/plugins"
rm -rf "$PLUGIN_DST"
cp -R "$PLUGIN_SRC" "$PLUGIN_DST"

python -m pip install -r "$PLUGIN_DST/requirements.txt"

echo
echo "Gentleman Studio installed into: $PLUGIN_DST"
echo "Start WanGP from its folder with:"
echo "  cd $WAN_GP_DIR"
echo "  python wgp.py --listen --server-port 7860 --profile 4"
echo "Then enable Gentleman Studio in Apps & PlugIn Manager."
