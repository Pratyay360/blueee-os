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

curl -o /tmp/host-spawn -fsSL https://github.com/1player/host-spawn/releases/download/v1.6.2/host-spawn-x86_64
install -D /tmp/host-spawn "$HOME/.local/bin/host-spawn"


curl -fsSl https://pkg.cloudflareclient.com/cloudflare-warp-ascii.repo | sudo tee /etc/yum.repos.d/cloudflare-warp.repo
yum update -y
yum install -y --skip-unavailable cloudflare-warp



# curl https://mise.run | sh




# unable to find a solution for this

# curl -fsSL -o /tmp/arch-grub.tar.gz \
#   https://github.com/TomorrowX6/arch-grub/archive/refs/heads/main.tar.gz
# mkdir -p /tmp/arch-grub /usr/share/grub2/themes/blackice
# tar -xzf /tmp/arch-grub.tar.gz -C /tmp/arch-grub --strip-components=1
# cp -r /tmp/arch-grub/blackice/. /usr/share/grub2/themes/blackice/
# rm -rf /tmp/arch-grub /tmp/arch-grub.tar.gz
