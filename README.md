# Blueee OS

Custom Fedora Atomic desktop images with CachyOS BORE Kernel and standard Fedora kernels. Built with [BlueBuild](https://blue-build.org).

## 💿 ISO Downloads & Live Web Portal

All bootable ISOs are automatically uploaded to GoFile with embedded QR codes for mobile scanning and instant direct downloads:

👉 **[Blueee OS ISO Downloads Portal](https://pratyay360.github.io/blueee-os/)**

### Local Static Site Tasks
- **Build static site**: `mise run build-site`
- **Preview static site**: `mise run preview-site` (serves at `http://localhost:8080`)

---

## to install this


``` bash
sudo  rpm-ostree rebase ostree-unverified-registry:ghcr.io/pratyay360/catchy-kinoite:latest

```

# using quay.io

```bash
sudo  rpm-ostree rebase ostree-unverified-registry:quay.io/pratyay360/catchy-kinoite:latest
```

to verify image

```sh
cosign verify --key cosign.pub ghcr.io/pratyay360/catchy-kinoite:latest

```

# how to inspect

```sh
skopeo inspect docker://ghcr.io/pratyay360/catchy-kinoite:latest

```



to generate cosign key pair with skopeo

```sh

skopeo generate-sigstore-key --output-prefix cosign
```




<!--![Made with VHS](https://vhs.charm.sh/vhs-6CLRQccErvA9j4gIuYsTDw.gif)-->

[![asciicast](https://asciinema.org/a/76aMc7dy4B6cGtTG.svg)](https://asciinema.org/a/76aMc7dy4B6cGtTG)
