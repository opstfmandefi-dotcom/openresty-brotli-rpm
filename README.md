# OpenResty Brotli RPM

Builds the [Google `ngx_brotli`](https://github.com/google/ngx_brotli)
dynamic modules against the official OpenResty RPM and publishes installable
Rocky Linux 9 packages for:

- AMD64 (`x86_64`)
- ARM64 (`aarch64`)

The build reads the configure arguments from the installed OpenResty binary.
This keeps the dynamic modules ABI-compatible with the exact OpenResty package
used by the build.

## Install

Download the RPM for your architecture from
[Releases](../../releases), then:

```bash
sudo dnf install ./openresty-module-brotli-*.rpm
```

Add these lines at the top of
`/usr/local/openresty/nginx/conf/nginx.conf`:

```nginx
load_module modules/ngx_http_brotli_filter_module.so;
load_module modules/ngx_http_brotli_static_module.so;
```

Verify the configuration:

```bash
sudo openresty -t
```

## Release

Every Monday at 03:17 UTC, the **Release** workflow resolves the latest
`ngx_brotli` commit and discovers the two newest OpenResty versions in the
official Rocky Linux 9 repository. It builds that version/architecture matrix
and creates one release per OpenResty version. Existing releases are refreshed
in place, making weekly rebuilds idempotent.

The workflow builds and smoke-tests each architecture natively, creates
SHA-256 checksums, and publishes all RPMs and checksums in public GitHub
releases. The workflow can also be run manually. Leave the version input empty
for automatic discovery, or supply up to two comma-separated versions such as
`1.29.2.5,1.31.1.1`.

## Local build

On Rocky Linux 9 with the official OpenResty repository configured:

```bash
sudo dnf install -y rpm-build gcc gcc-c++ make git perl \
  openresty openresty-zlib-devel
# Install the PCRE/PCRE2 and OpenSSL development packages matching
# `openresty -V` for the selected OpenResty version.
./scripts/build-rpm.sh 1.31.1.1 1
```

The optional third argument pins an `ngx_brotli` commit. If omitted, the build
resolves the current upstream `HEAD`.

Packages are written to `artifacts/`.
