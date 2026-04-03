{{/*
Expand the name of the chart.
*/}}
{{- define "autoaudit.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "autoaudit.fullname" -}}
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

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "autoaudit.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "autoaudit.labels" -}}
helm.sh/chart: {{ include "autoaudit.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/part-of: autoaudit
{{- end }}

{{/*
Selector labels for a specific component.
Usage: {{ include "autoaudit.selectorLabels" (dict "context" . "component" "backend-api") }}
*/}}
{{- define "autoaudit.selectorLabels" -}}
app.kubernetes.io/name: {{ include "autoaudit.name" .context }}
app.kubernetes.io/instance: {{ .context.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Component labels (common + selector).
Usage: {{ include "autoaudit.componentLabels" (dict "context" . "component" "backend-api") }}
*/}}
{{- define "autoaudit.componentLabels" -}}
{{ include "autoaudit.labels" .context }}
{{ include "autoaudit.selectorLabels" (dict "context" .context "component" .component) }}
{{- end }}

{{/*
Service account name.
*/}}
{{- define "autoaudit.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "autoaudit.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Secret name. Uses an externally-created secret if specified, otherwise
falls back to a conventional name based on the release.
*/}}
{{- define "autoaudit.secretName" -}}
{{- if .Values.secrets.existingSecret }}
{{- .Values.secrets.existingSecret }}
{{- else }}
{{- printf "%s-secrets" (include "autoaudit.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Image pull secrets.
*/}}
{{- define "autoaudit.imagePullSecrets" -}}
{{- with .Values.global.imagePullSecrets }}
imagePullSecrets:
  {{- toYaml . | nindent 2 }}
{{- end }}
{{- end }}

{{/*
Resolve a full image reference including registry prefix.
Usage: {{ include "autoaudit.image" (dict "registry" .Values.global.imageRegistry "repository" .Values.backendApi.image.repository "tag" (.Values.backendApi.image.tag | default .Chart.AppVersion)) }}
*/}}
{{- define "autoaudit.image" -}}
{{- if .registry }}
{{- printf "%s/%s:%s" .registry .repository .tag }}
{{- else }}
{{- printf "%s:%s" .repository .tag }}
{{- end }}
{{- end }}

{{/*
PostgreSQL host (internal service name).
*/}}
{{- define "autoaudit.postgresql.host" -}}
{{- printf "%s-postgresql" (include "autoaudit.fullname" .) }}
{{- end }}

{{/*
Redis host (internal service name).
*/}}
{{- define "autoaudit.redis.host" -}}
{{- printf "%s-redis" (include "autoaudit.fullname" .) }}
{{- end }}

{{/*
OPA URL (internal service).
*/}}
{{- define "autoaudit.opa.url" -}}
{{- printf "http://%s-opa:%d" (include "autoaudit.fullname" .) (.Values.opa.service.port | int) }}
{{- end }}

{{/*
PowerShell service URL (internal service).
*/}}
{{- define "autoaudit.powershellService.url" -}}
{{- printf "http://%s-powershell-service:%d" (include "autoaudit.fullname" .) (.Values.powershellService.service.port | int) }}
{{- end }}

{{/*
DATABASE_URL for backend-api (async driver).
The password is injected via $(POSTGRESQL_PASSWORD) env var interpolation.
*/}}
{{- define "autoaudit.databaseUrl.async" -}}
{{- printf "postgresql+asyncpg://%s:$(POSTGRESQL_PASSWORD)@%s:5432/%s" .Values.postgresql.user (include "autoaudit.postgresql.host" .) .Values.postgresql.database }}
{{- end }}

{{/*
DATABASE_URL for worker (sync driver).
*/}}
{{- define "autoaudit.databaseUrl.sync" -}}
{{- printf "postgresql://%s:$(POSTGRESQL_PASSWORD)@%s:5432/%s" .Values.postgresql.user (include "autoaudit.postgresql.host" .) .Values.postgresql.database }}
{{- end }}

{{/*
Redis URL.
Uses $(REDIS_PASSWORD) env var interpolation for the password.
*/}}
{{- define "autoaudit.redis.url" -}}
{{- printf "redis://:$(REDIS_PASSWORD)@%s:6379" (include "autoaudit.redis.host" .) }}
{{- end }}

{{/*
Common environment variables for backend-api (also used by migration job).
*/}}
{{- define "autoaudit.backendApi.env" -}}
- name: POSTGRESQL_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: postgresql-password
- name: REDIS_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: redis-password
- name: DATABASE_URL
  value: {{ include "autoaudit.databaseUrl.async" . | quote }}
- name: REDIS_URL
  value: {{ include "autoaudit.redis.url" . | quote }}
- name: OPA_URL
  value: {{ include "autoaudit.opa.url" . | quote }}
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: jwt-secret-key
- name: ENCRYPTION_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: encryption-key
- name: POLICIES_DIR
  value: /app/policies
{{- range $key, $value := .Values.backendApi.env }}
- name: {{ $key }}
  value: {{ $value | quote }}
{{- end }}
{{- end }}

{{/*
Common environment variables for worker.
*/}}
{{- define "autoaudit.worker.env" -}}
- name: POSTGRESQL_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: postgresql-password
- name: REDIS_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: redis-password
- name: DATABASE_URL
  value: {{ include "autoaudit.databaseUrl.sync" . | quote }}
- name: REDIS_URL
  value: {{ include "autoaudit.redis.url" . | quote }}
- name: OPA_URL
  value: {{ include "autoaudit.opa.url" . | quote }}
- name: ENCRYPTION_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "autoaudit.secretName" . }}
      key: encryption-key
- name: POWERSHELL_SERVICE_URL
  value: {{ include "autoaudit.powershellService.url" . | quote }}
{{- end }}
