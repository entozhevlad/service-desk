#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-service-desk}"
POD_NAME="${POD_NAME:-loadgen}"

kubectl -n "${NAMESPACE}" delete pod "${POD_NAME}" --ignore-not-found
echo "[loadgen] stopped"
