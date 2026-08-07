to install this

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
