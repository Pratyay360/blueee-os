#!/usr/bin/env bash
# One-time activation for the Blueee OS GRUB theme on Fedora Atomic.
#
# Why this exists: GRUB can only load themes from /boot at boot time, and
# /boot is managed by ostree/rpm-ostree, not by the image. So the theme ships
# in the image at /usr/share/grub/themes/blueee/ and this script copies it
# into place and regenerates grub.cfg. Safe to re-run.
#
# Usage: sudo /usr/share/blueee/enable-grub-theme.sh
#
# OEM install mode:
#   Uses alternate paths if they exist (for OEM ISO installs).
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

SRC="/usr/share/grub/themes/blueee"
DST="/boot/grub2/themes/blueee"

if [[ ! -f "${SRC}/theme.txt" ]]; then
  echo "Theme not found at ${SRC} - are you on a Blueee OS deployment?" >&2
  exit 1
fi

mkdir -p "${DST}"
cp -f "${SRC}/theme.txt" "${SRC}/background.png" "${DST}/"

# Update GRUB config to point to the theme
GRUB_CFG="/etc/default/grub"
if [[ -f "${GRUB_CFG}" ]]; then
  if grep -q '^GRUB_THEME=' "${GRUB_CFG}"; then
    sed -i 's|^GRUB_THEME=.*|GRUB_THEME="/boot/grub2/themes/blueee/theme.txt"|' "${GRUB_CFG}"
  else
    echo 'GRUB_THEME="/boot/grub2/themes/blueee/theme.txt"' >> "${GRUB_CFG}"
  fi

  # Ensure OEM-friendly GRUB settings
  if grep -q '^GRUB_TIMEOUT=' "${GRUB_CFG}"; then
    sed -i 's|^GRUB_TIMEOUT=.*|GRUB_TIMEOUT="10"|' "${GRUB_CFG}"
  fi
fi

# Regenerate grub.cfg
if command -v grub2-mkconfig &>/dev/null; then
  grub2-mkconfig -o /boot/grub2/grub.cfg
elif command -v grub-mkconfig &>/dev/null; then
  grub-mkconfig -o /boot/grub/grub.cfg
fi

echo "Blueee GRUB theme installed. Reboot to see it."
