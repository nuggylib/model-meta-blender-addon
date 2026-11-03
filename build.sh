#!/bin/sh
set -eu

cd "$(dirname "$0")"

fail() {
  echo "build.sh: $*" >&2
  exit 1
}

version_of() {
  "$1" --version 2>/dev/null | sed -n 's/^Blender \([0-9][0-9.]*\).*/\1/p' | head -n 1
}

version_ge() {
  awk -v a="$1" -v b="$2" 'BEGIN {
    split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) if (x[i] + 0 != y[i] + 0) exit !(x[i] + 0 > y[i] + 0)
  }'
}

candidates() {
  if [ -n "${BLENDER:-}" ]; then
    printf '%s\n' "$BLENDER"
    return
  fi
  if command -v mdfind >/dev/null 2>&1; then
    mdfind "kMDItemCFBundleIdentifier == 'org.blenderfoundation.blender'" |
      sed 's|$|/Contents/MacOS/Blender|'
  fi
  command -v blender || true
}

required=$(sed -n 's/^blender_version_min = "\(.*\)"$/\1/p' src/blender_manifest.toml)
[ -n "$required" ] || fail "no blender_version_min in src/blender_manifest.toml"

if [ -n "${BLENDER:-}" ] && [ ! -x "$BLENDER" ]; then
  fail "BLENDER is set to '$BLENDER', which is not an executable."
fi

blender=
installed=
while IFS= read -r candidate; do
  [ -n "$candidate" ] && [ -x "$candidate" ] || continue
  version=$(version_of "$candidate")
  [ -n "$version" ] || continue
  if [ -z "$installed" ] || ! version_ge "$installed" "$version"; then
    blender=$candidate
    installed=$version
  fi
done <<EOF
$(candidates)
EOF

[ -n "$blender" ] ||
  fail "Blender not found. Install Blender $required or later, or set BLENDER to its executable."

version_ge "$installed" "$required" ||
  fail "newest Blender found is $installed ($blender); $required or later is required."

echo "Using Blender $installed ($blender)"
mkdir -p build
exec "$blender" --factory-startup --command extension build --source-dir src --output-dir build
