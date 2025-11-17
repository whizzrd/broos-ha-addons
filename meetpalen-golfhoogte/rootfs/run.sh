#!/usr/bin/env bash
set -euo pipefail

# Load bashio if available (Home Assistant add-on base image)
if [ -f /usr/lib/bashio/bashio.sh ]; then
  # shellcheck source=/dev/null
  source /usr/lib/bashio/bashio.sh
fi

python3 /app/main.py
