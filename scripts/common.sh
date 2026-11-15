#!/usr/bin/env bash
set -euo pipefail

set -a
# shellcheck disable=SC1091
source .env.local
set +a

compose=(docker compose --env-file .env.local)
client=("${compose[@]}" exec -T clickhouse clickhouse-client
  --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD")
