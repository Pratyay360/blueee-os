#!/usr/bin/env bash

set -euo pipefail

# Create bin directory
mkdir -p "$HOME/.local/bin"
touch "$HOME/.zshrc"
touch "$HOME/.bashrc"


# curl https://mise.run | sh
yum install -y --nogpgcheck --repofrompath 'terra,https://repos.fyralabs.com/terra$releasever' terra-release terra-gpg-keys
