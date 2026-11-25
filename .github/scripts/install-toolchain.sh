#!/usr/bin/env bash
# Install OS packages, Rust and a pinned BlueBuild CLI.
# Inputs:  BLUEBUILD_VERSION (required, e.g. 0.9.42)
# Outputs: none
# Fails:   on any package/tool installation error.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_env BLUEBUILD_VERSION

log "Installing build packages..."
sudo apt-get update
sudo apt-get install -y \
  git cargo gcc \
  podman \
  qemu-system buildah \
  libssl-dev jq curl

# A recent rustc is required by current blue-build releases; the distro cargo
# is often too old, so install a minimal stable toolchain with rustup.
if ! command -v rustup >/dev/null 2>&1; then
  log "Installing the stable Rust toolchain..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |
    sh -s -- -y --profile minimal --default-toolchain stable
fi
# shellcheck source=/dev/null
source "$HOME/.cargo/env"

log "Installing blue-build ${BLUEBUILD_VERSION}..."
cargo install --locked blue-build --version "$BLUEBUILD_VERSION"

bluebuild --version
