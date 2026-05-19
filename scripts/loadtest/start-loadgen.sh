#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-service-desk}"
POD_NAME="${POD_NAME:-loadgen}"
BACKEND_URL="${BACKEND_URL:-http://service-desk-backend:8000}"
CONCURRENCY="${CONCURRENCY:-80}"

echo "[loadgen] namespace=${NAMESPACE} pod=${POD_NAME} backend=${BACKEND_URL} concurrency=${CONCURRENCY}"

kubectl -n "${NAMESPACE}" delete pod "${POD_NAME}" --ignore-not-found >/dev/null 2>&1 || true

kubectl -n "${NAMESPACE}" run "${POD_NAME}" \
  --image=curlimages/curl:8.7.1 \
  --restart=Never \
  --command -- sh -c "while true; do for i in \$(seq 1 ${CONCURRENCY}); do curl -s -o /dev/null ${BACKEND_URL}/tickets & curl -s -o /dev/null ${BACKEND_URL}/healthz & done; wait; done"

echo "[loadgen] started. Check with: kubectl -n ${NAMESPACE} get pod ${POD_NAME}"
