#!/usr/bin/env bash
# One-time activation for the Blueee OS GRUB theme on Fedora Atomic.
#
# Why this exists: GRUB can only load themes from /boot at boot time, and
# /boot is managed by ostree/rpm-ostree, not by the image. So the theme ships
# in the image at /usr/share/grub/themes/blueee/ and this script copies it
# into place and regenerates grub.cfg. Safe to re-run.
#
# Usage: sudo /usr/share/blueee/enable-grub-theme.sh
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

if grep -q '^GRUB_THEME=' /etc/default/grub; then
  sed -i 's|^GRUB_THEME=.*|GRUB_THEME="/boot/grub2/themes/blueee/theme.txt"|' /etc/default/grub
else
  echo 'GRUB_THEME="/boot/grub2/themes/blueee/theme.txt"' >> /etc/default/grub
fi

grub2-mkconfig -o /boot/grub2/grub.cfg
echo "Blueee GRUB theme installed. Reboot to see it."
