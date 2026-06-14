#!/usr/bin/env bash
# Lab 4 bootstrap: minikube + Argo CD + workloads in service-desk namespace.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change-me}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-change-me}"

echo "==> Starting minikube"
minikube start --driver=docker

echo "==> Enabling metrics-server"
minikube addons enable metrics-server

echo "==> Installing Argo CD (namespace argocd)"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply --server-side --force-conflicts -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

echo "==> Creating application namespace and backend secret"
kubectl create namespace service-desk --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic service-desk-backend-env \
  --namespace service-desk \
  --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Bootstrapping GitOps from ${ROOT_DIR}/argocd"
kubectl apply -f "${ROOT_DIR}/argocd/project.yaml"
kubectl apply -f "${ROOT_DIR}/argocd/root-application.yaml"

echo "==> Waiting for workloads in service-desk"
kubectl wait --for=condition=available deployment/service-desk-sonarqube -n service-desk --timeout=900s || true
kubectl wait --for=condition=available deployment/service-desk-backend -n service-desk --timeout=600s || true
kubectl wait --for=condition=available deployment/service-desk-frontend -n service-desk --timeout=600s || true

echo
echo "Argo CD admin password:"
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo
echo
kubectl get applications -n argocd
kubectl get pods,svc,hpa -n service-desk
echo
echo "Frontend:  http://$(minikube ip):30081"
echo "Grafana:   http://$(minikube ip):30300  (admin / ${GRAFANA_PASSWORD})"
echo "SonarQube: http://$(minikube ip):30090  (admin / admin on first login)"
echo "Argo CD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
