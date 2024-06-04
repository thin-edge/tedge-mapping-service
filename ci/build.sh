
#!/bin/bash
# -------------------------------------------
# Build linux packages
# -------------------------------------------
set -e

# clean dist
if [ -d dist ]; then
    rm -rf dist
fi

mkdir -p dist

if [ $# -gt 0 ]; then
    export SEMVER="$1"
fi

if [ -n "$SEMVER" ]; then
    echo "Using version: $SEMVER"
fi

packages=(
    rpm
    deb
    apk
)

for package_type in "${packages[@]}"; do
    nfpm package --packager "$package_type" --target ./dist/
done

echo "Created all linux packages"
