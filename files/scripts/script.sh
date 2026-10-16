#!/usr/bin/env bash

set -euo pipefail

# Seed default shell dotfiles for new users via /etc/skel.
# NOTE: $HOME is /root at build time, so never write user dotfiles there.

# Prefer dnf over yum on current Fedora.
yum install -y --nogpgcheck --repofrompath "terra,https://repos.fyralabs.com/terra$(rpm -E %fedora)" terra-release terra-gpg-keys
