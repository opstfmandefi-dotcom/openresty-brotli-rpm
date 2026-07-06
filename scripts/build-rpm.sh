#!/usr/bin/env bash
set -euo pipefail

openresty_version="${1:-1.31.1.1}"
package_release="${2:-1}"
ngx_brotli_commit="${3:-}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
topdir="${repo_root}/.rpmbuild"
artifacts="${repo_root}/artifacts"

if [[ -z "$ngx_brotli_commit" ]]; then
  ngx_brotli_commit="$(
    git ls-remote https://github.com/google/ngx_brotli.git HEAD |
      awk 'NR == 1 { print $1 }'
  )"
fi
[[ "$ngx_brotli_commit" =~ ^[0-9a-f]{40}$ ]]

rm -rf "$topdir"
mkdir -p "$topdir"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} "$artifacts"

nginx_version="$(openresty -V 2>&1 | sed -n 's|^nginx version: openresty/||p' | cut -d. -f1-3)"
installed_version="$(rpm -q --qf '%{VERSION}' openresty)"

if [[ "$installed_version" != "$openresty_version" ]]; then
  echo "Expected OpenResty ${openresty_version}, found ${installed_version}" >&2
  exit 1
fi

curl -fsSL "https://openresty.org/download/openresty-${openresty_version}.tar.gz" \
  -o "$topdir/SOURCES/openresty-${openresty_version}.tar.gz"
curl -fsSL --retry 3 \
  "https://github.com/google/ngx_brotli/archive/${ngx_brotli_commit}.tar.gz" \
  -o "$topdir/SOURCES/ngx_brotli.tar.gz"
curl -fsSL --retry 3 \
  "https://github.com/google/brotli/archive/refs/tags/v1.1.0.tar.gz" \
  -o "$topdir/SOURCES/brotli.tar.gz"

cp "$repo_root/SPECS/openresty-module-brotli.spec" "$topdir/SPECS/"

rpmbuild -bb \
  --define "_topdir $topdir" \
  --define "openresty_version $openresty_version" \
  --define "nginx_version $nginx_version" \
  --define "package_release $package_release" \
  --define "ngx_brotli_commit $ngx_brotli_commit" \
  "$topdir/SPECS/openresty-module-brotli.spec"

find "$topdir/RPMS" -type f -name '*.rpm' -exec cp {} "$artifacts/" \;
rpm -qip "$artifacts"/*.rpm
