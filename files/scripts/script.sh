#!/usr/bin/env bash

set -euo pipefail

# Install starship (not available in Fedora 44 repos)
curl -sS https://starship.rs/install.sh | sh -s -- -y -b /usr/local/bin

# Seed default shell dotfiles for new users via /etc/skel.
# NOTE: $HOME is /root at build time, so never write user dotfiles there.
mkdir -p /etc/skel/.local/bin
touch /etc/skel/.zshrc
touch /etc/skel/.bashrc


# Install Terra repo (releasever must expand, so use double quotes).
# Prefer dnf over yum on current Fedora.
dnf install -y --nogpgcheck --repofrompath "terra,https://repos.fyralabs.com/terra$(rpm -E %fedora)" terra-release terra-gpg-keys
