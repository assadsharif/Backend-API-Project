# Helm Template Examples Reference

Core template files for multi-component Helm charts.

---

## _helpers.tpl

Template helpers for naming conventions, labels, and common functions.

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "myapp.fullname" -}}
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
{{- define "myapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "myapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "myapp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend fullname
*/}}
{{- define "myapp.backend.fullname" -}}
{{- printf "%s-backend" (include "myapp.fullname" .) }}
{{- end }}

{{/*
Frontend fullname
*/}}
{{- define "myapp.frontend.fullname" -}}
{{- printf "%s-frontend" (include "myapp.fullname" .) }}
{{- end }}

{{/*
Image tag - defaults to Chart.appVersion
*/}}
{{- define "myapp.imageTag" -}}
{{- .tag | default $.Chart.AppVersion }}
{{- end }}
```

---

## deployment.yaml

Deployment template for backend component.

```yaml
{{- if .Values.backend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.backend.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      {{- with .Values.backend.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      {{- with .Values.global.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.backend.podSecurityContext | nindent 8 }}
      containers:
        - name: backend
          securityContext:
            {{- toYaml .Values.backend.securityContext | nindent 12 }}
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.backend.service.targetPort }}
              protocol: TCP
          {{- with .Values.backend.env }}
          env:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.backend.envFrom }}
          envFrom:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          livenessProbe:
            {{- toYaml .Values.backend.livenessProbe | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.backend.readinessProbe | nindent 12 }}
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
      {{- with .Values.backend.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.backend.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.backend.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
{{- end }}
```

### Frontend Deployment

```yaml
{{- if .Values.frontend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.frontend.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: frontend
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: frontend
    spec:
      {{- with .Values.global.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.frontend.service.targetPort }}
              protocol: TCP
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
{{- end }}
```

---

## service.yaml

Service templates for backend and frontend.

```yaml
{{- if .Values.backend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "myapp.backend.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: {{ .Values.backend.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "myapp.selectorLabels" . | nindent 4 }}
    app.kubernetes.io/component: backend
{{- end }}
---
{{- if .Values.frontend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "myapp.frontend.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: {{ .Values.frontend.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "myapp.selectorLabels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
{{- end }}
```

---

## ingress.yaml

Ingress template with multi-service routing.

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                {{- if eq .service "backend" }}
                name: {{ include "myapp.backend.fullname" $ }}
                port:
                  number: {{ $.Values.backend.service.port }}
                {{- else if eq .service "frontend" }}
                name: {{ include "myapp.frontend.fullname" $ }}
                port:
                  number: {{ $.Values.frontend.service.port }}
                {{- end }}
          {{- end }}
    {{- end }}
{{- end }}
```

---

## NOTES.txt

Post-install instructions template.

```
{{- $backendEnabled := .Values.backend.enabled -}}
{{- $frontendEnabled := .Values.frontend.enabled -}}
{{- $ingressEnabled := .Values.ingress.enabled -}}

Thank you for installing {{ .Chart.Name }}!

Your release is named: {{ .Release.Name }}
Chart version: {{ .Chart.Version }}
App version: {{ .Chart.AppVersion }}

{{- if $ingressEnabled }}

=== Ingress Access ===

Your application is accessible via:
{{- range .Values.ingress.hosts }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ .host }}
{{- end }}

Make sure to add the following to your /etc/hosts (on Linux/macOS):
  $(minikube ip) {{ (index .Values.ingress.hosts 0).host }}

{{- else }}

=== Service Access ===

{{- if $backendEnabled }}

Backend API:
{{- if eq .Values.backend.service.type "NodePort" }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "myapp.backend.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if eq .Values.backend.service.type "LoadBalancer" }}
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  You can watch the status with: kubectl get svc -w {{ include "myapp.backend.fullname" . }}
{{- else }}
  kubectl port-forward svc/{{ include "myapp.backend.fullname" . }} {{ .Values.backend.service.port }}:{{ .Values.backend.service.port }}
  Then visit: http://localhost:{{ .Values.backend.service.port }}
{{- end }}
{{- end }}

{{- if $frontendEnabled }}

Frontend:
{{- if eq .Values.frontend.service.type "NodePort" }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "myapp.frontend.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if eq .Values.frontend.service.type "LoadBalancer" }}
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  You can watch the status with: kubectl get svc -w {{ include "myapp.frontend.fullname" . }}
{{- else }}
  kubectl port-forward svc/{{ include "myapp.frontend.fullname" . }} {{ .Values.frontend.service.port }}:{{ .Values.frontend.service.port }}
  Then visit: http://localhost:{{ .Values.frontend.service.port }}
{{- end }}
{{- end }}

{{- end }}

=== Useful Commands ===

# View all deployed resources
kubectl get all -l app.kubernetes.io/instance={{ .Release.Name }}

# View logs
kubectl logs -l app.kubernetes.io/instance={{ .Release.Name }} -f

# Upgrade the release
helm upgrade {{ .Release.Name }} ./{{ .Chart.Name }} -f values.yaml

# Uninstall the release
helm uninstall {{ .Release.Name }}
```

---

## Template Best Practices

### Conditional Resource Creation

```yaml
{{- if .Values.backend.enabled }}
# Only create if component is enabled
{{- end }}
```

### Default Values

```yaml
# With default helper
replicas: {{ .Values.backend.replicaCount | default 1 }}

# With coalesce for multiple fallbacks
image: {{ coalesce .Values.backend.image.tag .Values.global.image.tag .Chart.AppVersion }}
```

### Required Values

```yaml
# Fail if required value missing
image: {{ required "backend.image.repository is required" .Values.backend.image.repository }}
```

### Include vs Template

```yaml
# include - captures output as string, can be piped
{{- include "myapp.labels" . | nindent 4 }}

# template - outputs directly, cannot be piped
{{- template "myapp.labels" . }}
```
