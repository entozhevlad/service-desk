#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-service-desk}"
APP_LABEL="${APP_LABEL:-app.kubernetes.io/name=service-desk-backend}"
HPA_NAME="${HPA_NAME:-service-desk-backend}"
INTERVAL="${INTERVAL:-5}"

while true; do
  clear
  date
  echo
  echo "== HPA =="
  kubectl -n "${NAMESPACE}" get hpa "${HPA_NAME}" || true
  echo
  echo "== Backend pods =="
  kubectl -n "${NAMESPACE}" get pods -l "${APP_LABEL}" || true
  echo
  echo "== Backend CPU/Memory =="
  kubectl -n "${NAMESPACE}" top pod -l "${APP_LABEL}" || true
  sleep "${INTERVAL}"
done
