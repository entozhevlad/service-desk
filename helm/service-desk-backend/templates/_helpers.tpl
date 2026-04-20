{{/* Expand the name of the chart. */}}
{{- define "service-desk-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Create a default fully qualified app name. */}}
{{- define "service-desk-backend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/* Create chart name and version as used by the chart label. */}}
{{- define "service-desk-backend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels. */}}
{{- define "service-desk-backend.labels" -}}
helm.sh/chart: {{ include "service-desk-backend.chart" . }}
{{ include "service-desk-backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels. */}}
{{- define "service-desk-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "service-desk-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Service account name. */}}
{{- define "service-desk-backend.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "service-desk-backend.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* ConfigMap name. */}}
{{- define "service-desk-backend.configMapName" -}}
{{- printf "%s-env" (include "service-desk-backend.fullname" .) }}
{{- end }}

{{/* Secret name. */}}
{{- define "service-desk-backend.secretName" -}}
{{- printf "%s-secret-env" (include "service-desk-backend.fullname" .) }}
{{- end }}
