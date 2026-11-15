#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source scripts/common.sh

"${compose[@]}" run --rm --no-deps --build \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/workspace" \
  --workdir /workspace \
  app python -m scripts.generate
