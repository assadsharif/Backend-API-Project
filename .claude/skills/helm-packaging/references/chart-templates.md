# Helm Chart Templates Reference

Complete template patterns for common Kubernetes resources.

---

## ConfigMap Template

### configmap.yaml

```yaml
{{- if .Values.configMap.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "myapp.fullname" . }}-config
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
data:
  {{- range $key, $value := .Values.configMap.data }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
{{- end }}
```

### ConfigMap with File Content

```yaml
{{- if .Values.configMap.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "myapp.fullname" . }}-config
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
data:
  {{- /* Inline data */}}
  {{- range $key, $value := .Values.configMap.data }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
  {{- /* File content */}}
  {{- if .Values.configMap.files }}
  {{- range $name, $content := .Values.configMap.files }}
  {{ $name }}: |
    {{- $content | nindent 4 }}
  {{- end }}
  {{- end }}
{{- end }}
```

### values.yaml for ConfigMap

```yaml
configMap:
  enabled: true
  data:
    LOG_LEVEL: "info"
    APP_NAME: "myapp"
    MAX_CONNECTIONS: "100"
  files:
    nginx.conf: |
      server {
        listen 80;
        location / {
          proxy_pass http://backend:8000;
        }
      }
```

---

## Secret Template

### secret.yaml (External Reference)

```yaml
{{- /* This template creates references to external secrets */}}
{{- /* Never store actual secret values in Helm charts */}}
{{- if .Values.externalSecrets.enabled }}
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ include "myapp.fullname" . }}-secrets
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  refreshInterval: {{ .Values.externalSecrets.refreshInterval | default "1h" }}
  secretStoreRef:
    name: {{ .Values.externalSecrets.secretStoreRef.name }}
    kind: {{ .Values.externalSecrets.secretStoreRef.kind | default "ClusterSecretStore" }}
  target:
    name: {{ include "myapp.fullname" . }}-secrets
  data:
    {{- range .Values.externalSecrets.data }}
    - secretKey: {{ .secretKey }}
      remoteRef:
        key: {{ .remoteRef.key }}
        property: {{ .remoteRef.property }}
    {{- end }}
{{- end }}
```

### Secret from Sealed Secrets

```yaml
{{- if .Values.sealedSecrets.enabled }}
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: {{ include "myapp.fullname" . }}-secrets
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  encryptedData:
    {{- range $key, $value := .Values.sealedSecrets.encryptedData }}
    {{ $key }}: {{ $value }}
    {{- end }}
{{- end }}
```

### values.yaml for Secrets

```yaml
# External Secrets Operator pattern
externalSecrets:
  enabled: false
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: myapp/database
        property: url
    - secretKey: API_KEY
      remoteRef:
        key: myapp/api
        property: key

# Sealed Secrets pattern (values are pre-encrypted)
sealedSecrets:
  enabled: false
  encryptedData:
    DATABASE_URL: "AgByzKGC..."
```

---

## PersistentVolumeClaim Template

### pvc.yaml

```yaml
{{- if .Values.persistence.enabled }}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ include "myapp.fullname" . }}-data
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  {{- with .Values.persistence.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  accessModes:
    - {{ .Values.persistence.accessMode | default "ReadWriteOnce" }}
  {{- if .Values.persistence.storageClass }}
  {{- if (eq "-" .Values.persistence.storageClass) }}
  storageClassName: ""
  {{- else }}
  storageClassName: {{ .Values.persistence.storageClass | quote }}
  {{- end }}
  {{- end }}
  resources:
    requests:
      storage: {{ .Values.persistence.size | default "1Gi" }}
{{- end }}
```

### Multiple PVCs

```yaml
{{- range $name, $config := .Values.persistence.volumes }}
{{- if $config.enabled }}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ include "myapp.fullname" $ }}-{{ $name }}
  labels:
    {{- include "myapp.labels" $ | nindent 4 }}
spec:
  accessModes:
    - {{ $config.accessMode | default "ReadWriteOnce" }}
  {{- if $config.storageClass }}
  storageClassName: {{ $config.storageClass | quote }}
  {{- end }}
  resources:
    requests:
      storage: {{ $config.size | default "1Gi" }}
{{- end }}
{{- end }}
```

### values.yaml for Persistence

```yaml
persistence:
  enabled: true
  storageClass: ""  # Empty uses default
  accessMode: ReadWriteOnce
  size: 10Gi
  annotations: {}

# Multiple volumes pattern
persistence:
  volumes:
    data:
      enabled: true
      size: 10Gi
      accessMode: ReadWriteOnce
    cache:
      enabled: true
      size: 5Gi
      accessMode: ReadWriteMany
    logs:
      enabled: false
      size: 2Gi
```

---

## HorizontalPodAutoscaler Template

### hpa.yaml

```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "myapp.backend.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "myapp.backend.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
    {{- with .Values.autoscaling.customMetrics }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- with .Values.autoscaling.behavior }}
  behavior:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
```

### values.yaml for HPA

```yaml
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
  customMetrics: []
```

---

## ServiceAccount Template

### serviceaccount.yaml

```yaml
{{- if .Values.serviceAccount.create -}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "myapp.serviceAccountName" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
```

### RBAC Resources

```yaml
{{- if .Values.rbac.create -}}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
rules:
  {{- toYaml .Values.rbac.rules | nindent 2 }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: {{ include "myapp.fullname" . }}
subjects:
  - kind: ServiceAccount
    name: {{ include "myapp.serviceAccountName" . }}
    namespace: {{ .Release.Namespace }}
{{- end }}
```

### values.yaml for ServiceAccount/RBAC

```yaml
serviceAccount:
  create: true
  annotations:
    # AWS IAM role for service account
    # eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/myapp-role
  name: ""

rbac:
  create: false
  rules:
    - apiGroups: [""]
      resources: ["configmaps", "secrets"]
      verbs: ["get", "list", "watch"]
    - apiGroups: [""]
      resources: ["pods"]
      verbs: ["get", "list"]
```

---

## NetworkPolicy Template

### networkpolicy.yaml

```yaml
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    {{- if .Values.networkPolicy.allowExternal }}
    - {}
    {{- else }}
    - from:
        # Allow from same namespace
        - podSelector: {}
        # Allow from ingress controller
        {{- if .Values.networkPolicy.ingressController }}
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: {{ .Values.networkPolicy.ingressController.namespace | default "ingress-nginx" }}
          podSelector:
            matchLabels:
              {{- toYaml .Values.networkPolicy.ingressController.podSelector | nindent 14 }}
        {{- end }}
      ports:
        - protocol: TCP
          port: {{ .Values.backend.service.targetPort }}
    {{- end }}
  egress:
    # Allow DNS
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
    # Allow external egress
    {{- if .Values.networkPolicy.allowExternalEgress }}
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8
              - 172.16.0.0/12
              - 192.168.0.0/16
    {{- end }}
    # Custom egress rules
    {{- with .Values.networkPolicy.egress }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
{{- end }}
```

### values.yaml for NetworkPolicy

```yaml
networkPolicy:
  enabled: false
  allowExternal: false
  allowExternalEgress: true
  ingressController:
    namespace: ingress-nginx
    podSelector:
      app.kubernetes.io/name: ingress-nginx
  egress: []
```

---

## PodDisruptionBudget Template

### pdb.yaml

```yaml
{{- if .Values.podDisruptionBudget.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "myapp.backend.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if .Values.podDisruptionBudget.minAvailable }}
  minAvailable: {{ .Values.podDisruptionBudget.minAvailable }}
  {{- else if .Values.podDisruptionBudget.maxUnavailable }}
  maxUnavailable: {{ .Values.podDisruptionBudget.maxUnavailable }}
  {{- else }}
  minAvailable: 1
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
{{- end }}
```

### values.yaml for PDB

```yaml
podDisruptionBudget:
  enabled: false
  minAvailable: 1
  # OR
  # maxUnavailable: 1
```

---

## CronJob Template

### cronjob.yaml

```yaml
{{- if .Values.cronJobs }}
{{- range $name, $job := .Values.cronJobs }}
{{- if $job.enabled }}
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ include "myapp.fullname" $ }}-{{ $name }}
  labels:
    {{- include "myapp.labels" $ | nindent 4 }}
spec:
  schedule: {{ $job.schedule | quote }}
  concurrencyPolicy: {{ $job.concurrencyPolicy | default "Forbid" }}
  successfulJobsHistoryLimit: {{ $job.successfulJobsHistoryLimit | default 3 }}
  failedJobsHistoryLimit: {{ $job.failedJobsHistoryLimit | default 1 }}
  {{- if $job.startingDeadlineSeconds }}
  startingDeadlineSeconds: {{ $job.startingDeadlineSeconds }}
  {{- end }}
  jobTemplate:
    spec:
      {{- if $job.activeDeadlineSeconds }}
      activeDeadlineSeconds: {{ $job.activeDeadlineSeconds }}
      {{- end }}
      {{- if $job.backoffLimit }}
      backoffLimit: {{ $job.backoffLimit }}
      {{- end }}
      template:
        metadata:
          labels:
            {{- include "myapp.selectorLabels" $ | nindent 12 }}
            app.kubernetes.io/component: {{ $name }}
        spec:
          restartPolicy: {{ $job.restartPolicy | default "OnFailure" }}
          {{- with $.Values.global.imagePullSecrets }}
          imagePullSecrets:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          containers:
            - name: {{ $name }}
              image: "{{ $job.image.repository }}:{{ $job.image.tag | default $.Chart.AppVersion }}"
              imagePullPolicy: {{ $job.image.pullPolicy | default "IfNotPresent" }}
              {{- with $job.command }}
              command:
                {{- toYaml . | nindent 16 }}
              {{- end }}
              {{- with $job.args }}
              args:
                {{- toYaml . | nindent 16 }}
              {{- end }}
              {{- with $job.env }}
              env:
                {{- toYaml . | nindent 16 }}
              {{- end }}
              {{- with $job.resources }}
              resources:
                {{- toYaml . | nindent 16 }}
              {{- end }}
{{- end }}
{{- end }}
{{- end }}
```

### values.yaml for CronJobs

```yaml
cronJobs:
  cleanup:
    enabled: false
    schedule: "0 2 * * *"  # Daily at 2 AM
    concurrencyPolicy: Forbid
    successfulJobsHistoryLimit: 3
    failedJobsHistoryLimit: 1
    activeDeadlineSeconds: 3600
    backoffLimit: 3
    image:
      repository: myapp/cleanup
      tag: ""
      pullPolicy: IfNotPresent
    command: ["python", "cleanup.py"]
    args: ["--days", "30"]
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: myapp-secrets
            key: DATABASE_URL
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 512Mi

  backup:
    enabled: false
    schedule: "0 3 * * 0"  # Weekly on Sunday at 3 AM
    image:
      repository: myapp/backup
      tag: ""
    command: ["backup.sh"]
```

---

## Job (One-Time) Template

### job.yaml

```yaml
{{- if .Values.jobs }}
{{- range $name, $job := .Values.jobs }}
{{- if $job.enabled }}
---
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" $ }}-{{ $name }}
  labels:
    {{- include "myapp.labels" $ | nindent 4 }}
  annotations:
    "helm.sh/hook": {{ $job.hook | default "post-install,post-upgrade" }}
    "helm.sh/hook-weight": {{ $job.hookWeight | default "0" | quote }}
    "helm.sh/hook-delete-policy": {{ $job.hookDeletePolicy | default "before-hook-creation" }}
spec:
  {{- if $job.ttlSecondsAfterFinished }}
  ttlSecondsAfterFinished: {{ $job.ttlSecondsAfterFinished }}
  {{- end }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" $ | nindent 8 }}
    spec:
      restartPolicy: {{ $job.restartPolicy | default "Never" }}
      containers:
        - name: {{ $name }}
          image: "{{ $job.image.repository }}:{{ $job.image.tag | default $.Chart.AppVersion }}"
          {{- with $job.command }}
          command:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with $job.args }}
          args:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with $job.env }}
          env:
            {{- toYaml . | nindent 12 }}
          {{- end }}
{{- end }}
{{- end }}
{{- end }}
```

### values.yaml for Jobs (Hooks)

```yaml
jobs:
  migrate:
    enabled: true
    hook: "post-install,post-upgrade"
    hookWeight: "-5"  # Run before main app
    hookDeletePolicy: "before-hook-creation,hook-succeeded"
    ttlSecondsAfterFinished: 600
    image:
      repository: myapp/backend
      tag: ""
    command: ["python", "manage.py", "migrate"]
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: myapp-secrets
            key: DATABASE_URL
```

---

## InitContainer Pattern

### deployment.yaml with InitContainers

```yaml
spec:
  template:
    spec:
      initContainers:
        {{- if .Values.backend.initContainers.waitForDb.enabled }}
        - name: wait-for-db
          image: {{ .Values.backend.initContainers.waitForDb.image | default "busybox:1.36" }}
          command: ['sh', '-c', 'until nc -z {{ .Values.backend.initContainers.waitForDb.host }} {{ .Values.backend.initContainers.waitForDb.port }}; do echo waiting for database; sleep 2; done;']
        {{- end }}
        {{- if .Values.backend.initContainers.migrate.enabled }}
        - name: migrate
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
          command: {{ .Values.backend.initContainers.migrate.command | toYaml | nindent 12 }}
          {{- with .Values.backend.envFrom }}
          envFrom:
            {{- toYaml . | nindent 12 }}
          {{- end }}
        {{- end }}
        {{- with .Values.backend.extraInitContainers }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      containers:
        # ... main containers
```

### values.yaml for InitContainers

```yaml
backend:
  initContainers:
    waitForDb:
      enabled: true
      image: busybox:1.36
      host: postgres
      port: 5432
    migrate:
      enabled: false
      command: ["python", "manage.py", "migrate"]
  extraInitContainers: []
```

---

## Sidecar Pattern

### deployment.yaml with Sidecars

```yaml
spec:
  template:
    spec:
      containers:
        - name: backend
          # ... main container spec
        {{- if .Values.backend.sidecars.cloudSqlProxy.enabled }}
        - name: cloud-sql-proxy
          image: {{ .Values.backend.sidecars.cloudSqlProxy.image }}
          command:
            - "/cloud_sql_proxy"
            - "-instances={{ .Values.backend.sidecars.cloudSqlProxy.instances }}"
          securityContext:
            runAsNonRoot: true
          resources:
            {{- toYaml .Values.backend.sidecars.cloudSqlProxy.resources | nindent 12 }}
        {{- end }}
        {{- with .Values.backend.extraContainers }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
```

### values.yaml for Sidecars

```yaml
backend:
  sidecars:
    cloudSqlProxy:
      enabled: false
      image: gcr.io/cloudsql-docker/gce-proxy:1.33.0
      instances: "project:region:instance=tcp:5432"
      resources:
        requests:
          cpu: 10m
          memory: 32Mi
        limits:
          cpu: 100m
          memory: 128Mi
  extraContainers: []
```

---

## Template Best Practices

### Conditional Resource Creation

```yaml
{{- if and .Values.backend.enabled (not .Values.backend.useExternalService) }}
# Create internal service only if backend is enabled and not using external
{{- end }}
```

### Default Value Patterns

```yaml
# With default helper
replicas: {{ .Values.backend.replicaCount | default 1 }}

# With coalesce for multiple fallbacks
image: {{ coalesce .Values.backend.image.tag .Values.global.image.tag .Chart.AppVersion }}

# With ternary for boolean
pullPolicy: {{ ternary "Always" "IfNotPresent" .Values.global.development }}
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
