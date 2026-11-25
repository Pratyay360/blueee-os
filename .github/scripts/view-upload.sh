#!/usr/bin/env bash
# Log the ISO path and upload results. Runs even when earlier steps fail.
# Inputs:  ISO_FILE, URL, QRCODE (all optional)
# Outputs: log lines only

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

log "File:       ${ISO_FILE:-(none)}"
log "GoFile URL: ${URL:-(none)}"
log "GoFile QR:  ${QRCODE:-(none)}"
