#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source scripts/common.sh

"${client[@]}" --multiquery < sql/schema.sql
scripts/gen.sh
scripts/load.sh
