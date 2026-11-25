#!/usr/bin/env bash
# Derive a short ISO name from a fully qualified image reference.
# Inputs:  IMAGE (required), e.g. quay.io/pratyay360/catchy-sway:44
# Outputs: name=<basename without tag>
# Fails:   if IMAGE is unset or the derived name is empty.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_env IMAGE

BASENAME="${IMAGE##*/}"
NAME="${BASENAME%:*}"

[[ -n "$NAME" ]] || die "Could not derive a name from IMAGE=$IMAGE"

log "Image: $IMAGE -> name: $NAME"
github_output "name=$NAME"
