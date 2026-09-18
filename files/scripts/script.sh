#!/usr/bin/env bash

set -euo pipefail

# Create bin directory
mkdir -p "$HOME/.local/bin"
touch "$HOME/.zshrc"
touch "$HOME/.bashrc"

# curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y
# curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh | sh -s -- --non-interactive
# curl -o /tmp/stew.tar -fSsL https://github.com/marwanhawari/stew/releases/download/v0.6.0/stew-v0.6.0-linux-amd64.tar.gz
# tar -xvf /tmp/stew.tar -C "$HOME/.local/bin"

# curl -fsSL https://soar.qaidvoid.dev/install.sh | sh

yum install -y --nogpgcheck --repofrompath 'terra,https://repos.fyralabs.com/terra$releasever' terra-release terra-gpg-keys
