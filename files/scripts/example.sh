#!/usr/bin/env bash

set -euo pipefail

mkdir -p "$HOME/.local/bin"

DEVBOX_VERSION="0.17.5"
curl -o /tmp/devbox.tar.gz -fsSL "https://github.com/jetify-com/devbox/releases/download/${DEVBOX_VERSION}/devbox_${DEVBOX_VERSION}_linux_amd64.tar.gz"
tar -xzf /tmp/devbox.tar.gz -C "$HOME/.local/bin"
chmod +x "$HOME/.local/bin/devbox"

curl --proto '=https' --tlsv1.2 -fsSL https://install.determinate.systems/nix \
  | sh -s -- install linux --no-confirm --init none

curl -fsSL https://github.com/Pratyay360/toolbox-export/raw/refs/heads/main/install.sh | sh
