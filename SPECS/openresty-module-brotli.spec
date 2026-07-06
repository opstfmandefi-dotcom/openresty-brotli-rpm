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
BuildRequires:  cmake, gcc, gcc-c++, make, perl

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

cmake \
    -S "$module_dir/deps/brotli" \
    -B "$module_dir/deps/brotli/out" \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF
cmake \
    --build "$module_dir/deps/brotli/out" \
    --config Release \
    --target brotlienc \
    --parallel %{_smp_build_ncpus}

configure_args="$(openresty -V 2>&1 | sed -n 's/^configure arguments: //p')"
test -n "$configure_args"

# Generate OpenResty's build tree. The explicit paths match the official
# package dependencies and allow this bootstrap configure to find PCRE2.
./configure \
    --with-cc=gcc \
    --with-cc-opt="-I/usr/local/openresty/zlib/include -I/usr/local/openresty/pcre2/include -I/usr/local/openresty/openssl3/include" \
    --with-ld-opt="-L/usr/local/openresty/zlib/lib -L/usr/local/openresty/pcre2/lib -L/usr/local/openresty/openssl3/lib" \
    --with-pcre-jit \
    --with-compat

cd "build/nginx-%{nginx_version}"
eval "set -- $configure_args"
# The official package may record ccache as its compiler wrapper, but ccache is
# not available in the standard Rocky Linux repositories. Keep the compiler
# and all ABI-relevant flags while removing that build-time-only dependency.
arg_count=$#
while [ "$arg_count" -gt 0 ]; do
    arg="$1"
    shift
    case "$arg" in
        --with-cc=*) arg="--with-cc=gcc" ;;
        --add-module=*)
            arg_count=$((arg_count - 1))
            continue
            ;;
    esac
    set -- "$@" "$arg"
    arg_count=$((arg_count - 1))
done

./configure "$@" --with-compat --add-dynamic-module="$module_dir"
make modules -j%{_smp_build_ncpus}

%install
install -d "%{buildroot}/usr/local/openresty/nginx/modules"
install -d "%{buildroot}%{_licensedir}/%{name}"
install -m 0755 build/nginx-%{nginx_version}/objs/ngx_http_brotli_filter_module.so \
  "%{buildroot}/usr/local/openresty/nginx/modules/"
install -m 0755 build/nginx-%{nginx_version}/objs/ngx_http_brotli_static_module.so \
  "%{buildroot}/usr/local/openresty/nginx/modules/"
install -m 0644 %{_builddir}/ngx_brotli-*/LICENSE \
  "%{buildroot}%{_licensedir}/%{name}/LICENSE"

%files
%license %{_licensedir}/%{name}/LICENSE
/usr/local/openresty/nginx/modules/ngx_http_brotli_filter_module.so
/usr/local/openresty/nginx/modules/ngx_http_brotli_static_module.so
