#!/usr/bin/env bash
# Build the store packages. One manifest in the repo, two browser-clean variants out:
#   dist/stripe-dark-mode-chrome-v<version>.zip   (Chrome / Brave / Edge: service worker only, no gecko block)
#   dist/stripe-dark-mode-firefox-v<version>.zip  (Firefox MV3: background.scripts + gecko id)
#   dist/SHA256SUMS
# Staged trees stay in dist/build/<target>/ so the smoke test can load the exact bytes that ship.
set -euo pipefail
cd "$(dirname "$0")"
V=$(python3 -c "import json;print(json.load(open('manifest.json'))['version'])")
rm -rf dist; mkdir -p dist/build
for target in chrome firefox; do
  out="dist/build/$target"; mkdir -p "$out"
  cp -R theme.css content.js background.js popup icons LICENSE "$out/"
  rm -f "$out"/icons/icon256.png "$out"/icons/icon512.png; find "$out" -name .DS_Store -delete
  python3 - "$target" "$out/manifest.json" <<'PY'
import json, sys
target, dst = sys.argv[1:]
m = json.load(open("manifest.json"))
if target == "chrome":
    m["background"] = {"service_worker": m["background"]["service_worker"]}
    m.pop("browser_specific_settings", None)
else:
    m["background"] = {"scripts": m["background"]["scripts"]}
json.dump(m, open(dst, "w"), indent=2); open(dst, "a").write("\n")
PY
  (cd "$out" && zip -qrX "../../stripe-dark-mode-$target-v$V.zip" .)
done
(cd dist && shasum -a 256 *.zip > SHA256SUMS)
for z in dist/*.zip; do echo "built $z ($(du -h "$z" | cut -f1), $(unzip -l "$z" | tail -1 | awk '{print $2}') files)"; done
cat dist/SHA256SUMS
