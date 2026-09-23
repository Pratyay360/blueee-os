#!/usr/bin/env bash
# Blueee OS OEM ISO Builder
# Prepares an ISO with OEM kickstart for automated installation.
# Usage: ./build-oem-iso.sh <image-name> <output-name>
#
# Example:
#   ./build-oem-iso.sh ghcr.io/pratyay360/kinoite:latest Blueee-OS-Kinoite-OEM.iso

set -euo pipefail

IMAGE="${1:?Usage: $0 <image> <output-name>}"
OUTPUT_NAME="${2:?Usage: $0 <image> <output-name>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Blueee OS OEM ISO Builder ==="
echo "Image: ${IMAGE}"
echo "Output: ${OUTPUT_NAME}.iso"

# Create temporary working directory
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "Working directory: ${WORK_DIR}"

# Copy kickstart
cp /usr/share/blueee/anaconda/kickstart.ks "${WORK_DIR}/"

# Build ISO with OEM kickstart
if command -v bluebuild &>/dev/null; then
  echo "Building ISO with bluebuild..."
  bluebuild generate-iso \
    --iso-name "${OUTPUT_NAME}.iso" \
    --output-dir "$(pwd)" \
    --kickstart "${WORK_DIR}/kickstart.ks" \
    image "${IMAGE}"
elif command -v podman &>/dev/null; then
  echo "Building ISO with build-container-installer..."
  podman run --rm \
    -v "$(pwd):/output" \
    -v "${WORK_DIR}:/ks:ro" \
    --entrypoint /bin/sh \
    ghcr.io/jasonn3/build-container-installer:latest \
    -c "
      cd /build-container-installer
      exec anaconda \
        --kickstart /ks/kickstart.ks \
        --image ${IMAGE} \
        --iso-name ${OUTPUT_NAME}.iso
    "
else
  echo "::error::Neither bluebuild nor podman found. Install one to build ISOs."
  exit 1
fi

echo "=== Done ==="
ls -lh "$(pwd)/${OUTPUT_NAME}.iso" 2>/dev/null || echo "ISO not found, check build output above."
