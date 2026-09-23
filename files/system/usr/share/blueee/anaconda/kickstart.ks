# Blueee OS OEM Install Kickstart
# Used for automated OEM installations via Anaconda.
# Customized for Blueee OS branding and defaults.

lang en_US.UTF-8
keyboard us
timezone UTC --utc

# Network
network --bootproto=dhcp --activateonboot --device=link

# Bootloader
bootloader --location=mbr --timeout=10

# Partitioning - use whole disk
zerombr
clearpart --all --initlabel
autopart --type=lvm

# Root account (locked by default, OEM can set password)
rootpw --lock

# Services
services --enabled=ostree-prepare

# Post-install script to finalize OEM setup
%post --log=/var/log/anaconda/oem-post.log
#!/bin/bash
set -euo pipefail

# Enable OEM setup service on first boot
systemctl enable blueee-oem-setup.service

# Set hostname
hostnamectl set-hostname blueee

# Clean up
rm -f /var/log/anaconda/oem-post.log
%end

# Package selection
%packages
@core
@base-x
ostree
rpm-ostree
flatpak
%end
