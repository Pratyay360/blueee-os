#!/usr/bin/env bash
# Build an ISO for a published container image and normalize its output path.
# Inputs:  IMAGE (required), NAME (required), OUTPUT_DIR (optional, default ./output)
# Outputs: iso-output-path=<absolute path to NAME.iso>
# Fails:   if bluebuild cannot produce an ISO at the expected path.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_env IMAGE NAME

OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/output}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
ISO_PATH="$OUTPUT_DIR/${NAME}.iso"

log "Generating ISO: image=$IMAGE name=$NAME output=$OUTPUT_DIR"

# Warm-up pulls only: bluebuild can pull on demand, so a failure here is not fatal.
for tag in latest v1.4.0; do
  if ! podman pull "ghcr.io/jasonn3/build-container-installer:${tag}"; then
    warn "Warm-up pull of ${tag} failed; continuing."
  fi
done

if ! bluebuild generate-iso --iso-name "${NAME}.iso" --output-dir "$OUTPUT_DIR" image "$IMAGE"; then
  warn "bluebuild generate-iso failed; retrying once with VERSION=42 (lorax fallback)."
  VERSION=42 bluebuild generate-iso --iso-name "${NAME}.iso" --output-dir "$OUTPUT_DIR" image "$IMAGE"
fi

# bluebuild occasionally writes a different filename. Promote a single candidate
# to the exact path the rest of the workflow expects.
if [[ ! -f "$ISO_PATH" ]]; then
  mapfile -t candidates < <(find "$OUTPUT_DIR" -maxdepth 3 -type f -name '*.iso' | sort)
  if [[ ${#candidates[@]} -gt 0 ]]; then
    log "Expected $ISO_PATH; promoting ${candidates[0]} instead."
    cp -v "${candidates[0]}" "$ISO_PATH"
  fi
fi

[[ -f "$ISO_PATH" ]] || die "ISO not found at $ISO_PATH"

ls -lh "$ISO_PATH"
github_output "iso-output-path=$ISO_PATH"
