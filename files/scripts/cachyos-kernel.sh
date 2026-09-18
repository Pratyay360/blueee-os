#!/usr/bin/env bash
# Swap the stock Fedora kernel for the CachyOS kernel from the
# bieszczaders/kernel-cachyos COPR.
#
# This runs inside the BlueBuild image build. rpm-ostree's kernel-install +
# dracut hooks fire during `dnf install` of the new kernel BEFORE depmod has
# populated /usr/lib/modules/<kver>/modules.dep, so they crash. We stub the
# hooks, swap the kernel with dnf5, then run depmod + dracut manually.
# Pattern adapted from https://github.com/zebcarnell/bazzite-cachyos

set -euo pipefail

echo ">>> Stubbing rpm-ostree + dracut kernel-install hooks"
cd /usr/lib/kernel/install.d
for hook in 05-rpmostree.install 50-dracut.install; do
  if [ -f "${hook}" ]; then
    mv "${hook}" "${hook}.bak"
  fi
  printf '%s\n' '#!/bin/sh' 'exit 0' > "${hook}"
  chmod +x "${hook}"
done
cd -

echo ">>> Enabling bieszczaders/kernel-cachyos COPR"
curl -fsSL -o /etc/yum.repos.d/kernel-cachyos.repo \
  "https://copr.fedorainfracloud.org/coprs/bieszczaders/kernel-cachyos/repo/fedora-rawhide/bieszczaders-kernel-cachyos-fedora-rawhide.repo"

echo ">>> Removing stock kernel packages"
STOCK_KERNELS=""
for pkg in kernel kernel-core kernel-modules kernel-modules-core kernel-modules-extra; do
  if rpm -q "${pkg}" >/dev/null 2>&1; then
    STOCK_KERNELS="${STOCK_KERNELS} ${pkg}"
  fi
done
if [ -n "${STOCK_KERNELS}" ]; then
  dnf5 -y remove ${STOCK_KERNELS}
fi

# Stale module trees (e.g. akmod leftovers) confuse depmod later.
rm -rf /lib/modules/*

echo ">>> Installing kernel-cachyos"
dnf5 -y install kernel-cachyos

echo ">>> Restoring kernel-install hooks"
cd /usr/lib/kernel/install.d
for hook in 05-rpmostree.install 50-dracut.install; do
  if [ -f "${hook}.bak" ]; then
    mv -f "${hook}.bak" "${hook}"
  fi
done
cd -

echo ">>> Generating depmod + initramfs for the new CachyOS kernel"
KVER=$(find /usr/lib/modules -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | head -n1)
echo "    Kernel version: ${KVER}"

depmod -a "${KVER}"
export DRACUT_NO_XATTR=1
/usr/bin/dracut \
  --no-hostonly \
  --kver "${KVER}" \
  --reproducible \
  -v \
  --add ostree \
  -f "/lib/modules/${KVER}/initramfs.img"
chmod 0600 "/lib/modules/${KVER}/initramfs.img"

echo ">>> CachyOS kernel ${KVER} installed"
