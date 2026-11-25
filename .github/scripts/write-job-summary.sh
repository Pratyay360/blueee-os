#!/usr/bin/env bash
# Append one ISO's result to the GitHub job summary.
# Inputs:  NAME, IMAGE (required); URL, QRCODE (optional)
# Outputs: lines in $GITHUB_STEP_SUMMARY (or stdout when running locally)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_env NAME IMAGE

step_summary "ISO Ready: $NAME"
step_summary "Image: \`$IMAGE\`"

if [[ -n "${URL:-}" ]]; then
  step_summary "Download: [GoFile Download Link]($URL)"
else
  step_summary "Download: pending"
fi

if [[ -n "${QRCODE:-}" ]]; then
  # Escape characters that would break the HTML attribute or inject markup.
  ESCAPED="$(printf '%s' "$QRCODE" |
    sed 's/&/\&amp;/g; s/"/\&quot;/g; s/</\&lt;/g; s/>/\&gt;/g')"
  step_summary "<img src=\"$ESCAPED\" width=\"160\" height=\"160\" alt=\"QR Code for $NAME\" />"
fi
