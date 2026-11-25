#!/usr/bin/env bash
# Upload an ISO to GoFile and emit a download URL plus QR code URL.
# Inputs:  FILE (required), NAME (required), IMAGE (required),
#          GOFILE_TOKEN (optional; anonymous upload is used when absent)
# Outputs: url=<download page>, qrcode=<QR image URL>
# Fails:   if the file is missing or no URL can be parsed from the response.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_env FILE NAME IMAGE
[[ -f "$FILE" ]] || die "ISO file not found: $FILE"

# Extract a usable download URL from a GoFile API response.
response_url() {
  local url
  url="$(printf '%s' "$1" | jq -r '.data.downloadPage // .data.directLink // empty' 2>/dev/null || true)"
  if [[ -n "$url" && "$url" != "null" ]]; then
    printf '%s' "$url"
  fi
  return 0
}

TOKEN="${GOFILE_TOKEN:-${TOKEN:-}}"
log "Uploading $FILE ($(du -h "$FILE" | cut -f1)) to GoFile..."

RESPONSE=""
if [[ -n "$TOKEN" ]]; then
  RESPONSE="$(curl -sS --fail-with-body -X POST -F "file=@$FILE" -F "token=$TOKEN" \
    https://upload.gofile.io/uploadFile 2>&1)" || RESPONSE=""
  if [[ -z "$(response_url "$RESPONSE")" ]]; then
    RESPONSE="$(curl -sS --fail-with-body -X POST -F "file=@$FILE" \
      -H "Authorization: Bearer $TOKEN" https://upload.gofile.io/uploadFile 2>&1)" || RESPONSE=""
  fi
fi
if [[ -z "$(response_url "$RESPONSE")" ]]; then
  RESPONSE="$(curl -sS --fail-with-body -X POST -F "file=@$FILE" \
    https://upload.gofile.io/uploadFile 2>&1)" || RESPONSE=""
fi

log "GoFile response: $RESPONSE"
URL="$(response_url "$RESPONSE")"
[[ -n "$URL" ]] || die "Could not parse a download URL from the GoFile response."

QR_DATA="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$URL")"
QRCODE="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${QR_DATA}"

github_output "url=$URL"
github_output "qrcode=$QRCODE"
log "GoFile URL: $URL"
log "GoFile QR:  $QRCODE"
