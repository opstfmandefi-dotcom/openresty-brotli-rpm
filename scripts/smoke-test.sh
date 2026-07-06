#!/usr/bin/env bash
set -euo pipefail

rpm_path="${1:?RPM path is required}"
dnf install -y "$rpm_path"

config="$(mktemp)"
cat >"$config" <<'EOF'
load_module /usr/local/openresty/nginx/modules/ngx_http_brotli_filter_module.so;
load_module /usr/local/openresty/nginx/modules/ngx_http_brotli_static_module.so;
events {}
http {
    brotli on;
    brotli_static on;
}
EOF

openresty -t -c "$config"
file /usr/local/openresty/nginx/modules/ngx_http_brotli_filter_module.so
file /usr/local/openresty/nginx/modules/ngx_http_brotli_static_module.so

