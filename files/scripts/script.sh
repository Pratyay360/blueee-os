#!/usr/bin/env bash

set -euo pipefail

# Create bin directory
mkdir -p "$HOME/.local/bin"
touch "$HOME/.zshrc"
touch "$HOME/.bashrc"

curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y
curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh | sh -s -- --non-interactive
curl -o /tmp/stew.tar -fSsL https://github.com/marwanhawari/stew/releases/download/v0.6.0/stew-v0.6.0-linux-amd64.tar.gz
tar -xvf /tmp/stew.tar -C "$HOME/.local/bin"

curl -fsSL https://soar.qaidvoid.dev/install.sh | sh

curl -o /tmp/cargo-binstall.tar.gz -fsSL https://github.com/cargo-bins/cargo-binstall/releases/download/v1.20.1/cargo-binstall-x86_64-unknown-linux-gnu.tgz
tar -xzvf /tmp/cargo-binstall.tar.gz -C "$HOME/.local/bin"



curl -fsSL https://github.com/Pratyay360/toolbox-export/raw/refs/heads/main/install.sh | sh

curl -fsSl https://pkg.cloudflareclient.com/cloudflare-warp-ascii.repo | sudo tee /etc/yum.repos.d/cloudflare-warp.repo
yum update -y
yum install -y --skip-unavailable cloudflare-warp
yum install -y --nogpgcheck --repofrompath 'terra,https://repos.fyralabs.com/terra$releasever' terra-release terra-gpg-keys
