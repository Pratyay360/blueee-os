#!/usr/bin/env bash
# Blueee OS OEM Setup Script
# Runs on first boot after OEM installation to finalize configuration.
# This service is enabled by the Anaconda kickstart %post section.

set -euo pipefail

LOGFILE="/var/log/blueee-oem-setup.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "=== Blueee OS OEM Setup - $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

# --- GRUB Theme Activation ---
echo "[1/4] Activating GRUB theme..."
if [[ -x /usr/share/blueee/enable-grub-theme.sh ]]; then
  /usr/share/blueee/enable-grub-theme.sh || true
fi


# --- System Tweaks ---
echo "[3/4] Applying system tweaks..."

# Set default wallpaper if KDE is present
if command -v plasma-apply-desktoptheme &>/dev/null; then
  mkdir -p /home/*/Desktop 2>/dev/null || true
fi

# Enable common services
systemctl enable --now flatpak-update.timer 2>/dev/null || true

# --- Cleanup ---
echo "[4/4] Cleaning up..."
rpm-ostree cleanup -m 2>/dev/null || true
rm -f "$LOGFILE" 2>/dev/null || true

echo "=== OEM setup complete ==="
