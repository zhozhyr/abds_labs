#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source scripts/common.sh

if [[ ! -d data ]]; then
  echo "data/ is missing; run 'make gen' first" >&2
  exit 1
fi

tables=(dim_realty dim_gauges dim_tariffs dim_users fact_gauge_bindings fact_meter_readings fact_invoice)
for table in "${tables[@]}"; do
  "${client[@]}" --query "TRUNCATE TABLE ${CLICKHOUSE_DATABASE}.${table}"
done
for table in "${tables[@]}"; do
  echo "Loading ${table}..."
  "${client[@]}" --query "INSERT INTO ${CLICKHOUSE_DATABASE}.${table} FORMAT CSV" < "data/${table}.csv"
done
