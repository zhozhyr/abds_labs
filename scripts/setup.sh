#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source scripts/common.sh

"${client[@]}" --multiquery < sql/schema.sql
poetry run python -m scripts.generate
scripts/load.sh
