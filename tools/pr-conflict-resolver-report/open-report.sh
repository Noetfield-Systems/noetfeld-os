#!/bin/bash
# Open the repo-bundled PR Conflict Resolver eval report (chromeless window).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_PATH="$DIR/report.html"
HTML_URL="file://$HTML_PATH"

launch_app_mode() {
  local app_path="$1"
  if [ -d "$app_path" ]; then
    open -na "$app_path" --args --new-window "--app=$HTML_URL" \
      --window-size=1280,900 --window-position=120,80
    return 0
  fi
  return 1
}

if launch_app_mode "/Applications/Google Chrome.app"; then exit 0; fi
if launch_app_mode "/Applications/Microsoft Edge.app"; then exit 0; fi
if launch_app_mode "/Applications/Brave Browser.app"; then exit 0; fi
open "$HTML_PATH"
