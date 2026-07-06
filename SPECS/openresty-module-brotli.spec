%global debug_package %{nil}

Name:           openresty-module-brotli
Version:        %{openresty_version}
Release:        %{package_release}%{?dist}
Summary:        Brotli dynamic modules for OpenResty
License:        BSD-2-Clause
URL:            https://github.com/google/ngx_brotli
Source0:        openresty-%{openresty_version}.tar.gz
Source1:        ngx_brotli.tar.gz
Source2:        brotli.tar.gz
Provides:       bundled(ngx_brotli) = %{ngx_brotli_commit}
Requires:       openresty = %{openresty_version}
BuildRequires:  gcc, gcc-c++, make, perl

%description
The ngx_brotli filter and static Brotli compression modules, built as dynamic
modules for the official OpenResty package.

%prep
%setup -q -n openresty-%{openresty_version}
tar -xzf %{SOURCE1} -C %{_builddir}
module_dir="$(find %{_builddir} -maxdepth 1 -type d -name 'ngx_brotli-*' -print -quit)"
test -n "$module_dir"
rm -rf "$module_dir/deps/brotli"
mkdir -p "$module_dir/deps/brotli"
tar -xzf %{SOURCE2} -C "$module_dir/deps/brotli" --strip-components=1

%build
module_dir="$(find %{_builddir} -maxdepth 1 -type d -name 'ngx_brotli-*' -print -quit)"
test -n "$module_dir"
test -f "$module_dir/deps/brotli/c/common/constants.c"

configure_args="$(openresty -V 2>&1 | sed -n 's/^configure arguments: //p')"
test -n "$configure_args"

# Generate OpenResty's nginx build tree, including the bundled module paths
# referenced by the official binary's nginx configure arguments.
./configure --with-compat

cd "build/nginx-%{nginx_version}"
eval "set -- $configure_args"
./configure "$@" --with-compat --add-dynamic-module="$module_dir"

make modules -j%{_smp_build_ncpus}

%install
install -d "%{buildroot}/usr/local/openresty/nginx/modules"
install -m 0755 build/nginx-%{nginx_version}/objs/ngx_http_brotli_filter_module.so \
  "%{buildroot}/usr/local/openresty/nginx/modules/"
install -m 0755 build/nginx-%{nginx_version}/objs/ngx_http_brotli_static_module.so \
  "%{buildroot}/usr/local/openresty/nginx/modules/"

%files
%license %{_builddir}/ngx_brotli-*/LICENSE
/usr/local/openresty/nginx/modules/ngx_http_brotli_filter_module.so
/usr/local/openresty/nginx/modules/ngx_http_brotli_static_module.so
