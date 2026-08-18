# Kubernetes Demo App

This project is a small production-style Node.js and Express application used to learn how an application is containerized and deployed to Kubernetes.

The app listens on port `3000` and shows:

- Application name: `Kubernetes Demo App`
- Environment from a ConfigMap
- Application version from a ConfigMap
- Student name from a ConfigMap
- Pod hostname from the container runtime
- A Kubernetes running message
- Whether the sample Kubernetes Secret was loaded

It also exposes:

- `/health` for liveness checks
- `/ready` for readiness checks
- `/api/info` for runtime application information

## Docker Architecture

The Docker image uses `node:24-alpine`.

Node 24 is currently an LTS release, which makes it appropriate for a demo that should look like a production service rather than a short-lived experiment. The `alpine` variant keeps the image small. The container runs as the built-in non-root `node` user, which is safer than running the application as root.

Build the image:

```bash
docker build -t kubernetes-demo:1.0.0 .
```

Run it locally:

```bash
docker run --rm -p 3000:3000 \
  -e APP_NAME="Kubernetes Demo App" \
  -e APP_ENV=development \
  -e APP_VERSION=1.0.0 \
  -e STUDENT_NAME=Stecy \
  -e DEMO_SECRET=super-secret-value \
  kubernetes-demo:1.0.0
```

Test it locally:

```bash
curl http://localhost:3000
curl http://localhost:3000/health
curl http://localhost:3000/ready
```

Run the Express app directly during development:

```bash
cd app
npm install
npm start
```

Then open:

```text
http://localhost:3000
```

Do not open `app/public/index.html` directly in the browser for the live demo. Opening the file with `file://` only loads the static HTML. It does not start Express, so `/api/info`, `/health`, and `/ready` will fail.

## Kubernetes Architecture

The Kubernetes manifests live in `k8s/`.

```text
                    User
                      |
                      v
              ClusterIP Service
                      |
             +--------+--------+
             |        |        |
             v        v        v
           Pod 1    Pod 2    Pod 3
             |        |        |
             +--------+--------+
                      |
                 Deployment
                      |
                     HPA
                      |
              CPU / Memory Metrics
```

## Kubernetes Objects

### Namespace

File: `k8s/namespace.yaml`

What are we creating?

A namespace named `kubernetes-demo`.

Why are we creating it?

A namespace keeps this demo separate from other workloads in the cluster. It is like a folder inside Kubernetes.

How does it connect?

All other manifests use `namespace: kubernetes-demo`, so they are created inside this namespace.

How can you verify it?

```bash
kubectl get namespace kubernetes-demo
```

### ConfigMap

File: `k8s/configmap.yaml`

What are we creating?

A ConfigMap named `kubernetes-demo-config` containing:

```text
APP_NAME=Kubernetes Demo App
APP_ENV=development
APP_VERSION=1.0.0
STUDENT_NAME=Stecy
```

Why are we creating it?

A ConfigMap stores non-sensitive configuration outside the application image. This means the same Docker image can run in development, staging, or production with different values.

How does it connect?

The Deployment injects the ConfigMap values into the container as environment variables using `envFrom`.

How can you verify it?

```bash
kubectl get configmap kubernetes-demo-config -n kubernetes-demo
kubectl describe configmap kubernetes-demo-config -n kubernetes-demo
```

### Secret

File: `k8s/secret.yaml`

What are we creating?

A Secret named `kubernetes-demo-secret` containing `DEMO_SECRET`.

Why are we creating it?

A Secret is used for sensitive values, such as tokens, passwords, and API keys. The application reads the value from the environment but does not hard-code it in source code.

Important: Kubernetes Secrets are not automatically the same as strong encryption. By default, they are base64 encoded, and cluster-level encryption depends on the Kubernetes configuration. In production, use a proper secret-management solution such as HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, Google Secret Manager, or sealed/external secrets.

How does it connect?

The Deployment injects the Secret into the container as an environment variable. The page only shows whether the secret was loaded; it does not print the secret value.

How can you verify it?

```bash
kubectl get secret kubernetes-demo-secret -n kubernetes-demo
kubectl describe secret kubernetes-demo-secret -n kubernetes-demo
```

### Deployment

File: `k8s/deployment.yaml`

What are we creating?

A Deployment named `kubernetes-demo` with `3` replicas.

Why are we creating it?

A Deployment manages identical Pods and keeps the desired number running. If a Pod crashes, the Deployment creates a replacement. If the image changes, the Deployment can roll out the new version safely.

How does it connect?

The Deployment creates Pods with the label `app.kubernetes.io/name: kubernetes-demo`. The Service uses that label to send traffic to the Pods. The HPA uses the Deployment as its scaling target.

Resource choices:

```yaml
requests:
  cpu: "100m"
  memory: "128Mi"
limits:
  cpu: "500m"
  memory: "256Mi"
```

These are sensible demo values for a small Express app. Requests reserve enough CPU and memory for scheduling. Limits prevent the container from using too much of the node.

How can you verify it?

```bash
kubectl get deployment kubernetes-demo -n kubernetes-demo
kubectl describe deployment kubernetes-demo -n kubernetes-demo
kubectl get pods -n kubernetes-demo
```

### Readiness Probe

The readiness probe calls `/ready`.

What does it do?

It tells Kubernetes when the container is ready to receive traffic.

Why does it matter?

If a Pod is running but not ready, the Service should not route traffic to it yet.

How can you verify it?

```bash
kubectl describe pod <pod-name> -n kubernetes-demo
```

### Liveness Probe

The liveness probe calls `/health`.

What does it do?

It tells Kubernetes whether the container is still alive.

Why does it matter?

If the liveness probe fails repeatedly, Kubernetes restarts the container.

How can you verify it?

```bash
kubectl describe pod <pod-name> -n kubernetes-demo
```

### Service

File: `k8s/service.yaml`

What are we creating?

A ClusterIP Service named `kubernetes-demo`.

Why are we creating it?

Pods are temporary and their IP addresses can change. A Service gives the Pods a stable internal network name and IP.

Why ClusterIP?

ClusterIP is appropriate because this demo does not need to expose the app publicly with a LoadBalancer or NodePort. It keeps the application internal to the cluster. For local testing, use `kubectl port-forward`.

How does it connect?

The Service selects Pods by label and forwards traffic from port `80` to container port `3000`.

How can you verify it?

```bash
kubectl get service kubernetes-demo -n kubernetes-demo
kubectl describe service kubernetes-demo -n kubernetes-demo
```

### Horizontal Pod Autoscaler

File: `k8s/hpa.yaml`

What are we creating?

An HPA that keeps at least `3` replicas, can scale to `10`, and targets `70%` average CPU utilization.

Why are we creating it?

The HPA automatically adjusts the number of Pods when CPU usage changes.

How does it connect?

The HPA points to the Deployment. It reads CPU metrics from the cluster metrics API and changes the Deployment replica count.

Important: CPU-based HPA requires Metrics Server or another metrics provider. If Metrics Server is not installed, the HPA object can exist, but it will not scale correctly.

How can you verify metrics availability?

```bash
kubectl top nodes
kubectl top pods -n kubernetes-demo
kubectl get hpa -n kubernetes-demo
```

Do not install Metrics Server automatically on a shared or production cluster. Ask first.

## Pre-Deployment Checks

Before applying anything, check your tools and cluster:

```bash
kubectl version --client
kubectl config current-context
kubectl cluster-info
kubectl get namespace kubernetes-demo
docker version
```

Do not deploy automatically if the context looks like production or an unknown remote cluster. Stop and confirm first.

Local development contexts are usually named something like:

- `docker-desktop`
- `minikube`
- `kind-*`

## Image Handling by Cluster Type

### Docker Desktop Kubernetes

Docker Desktop Kubernetes can usually use the local image directly:

```bash
docker build -t kubernetes-demo:1.0.0 .
kubectl apply -f k8s/
```

### Minikube

Build inside Minikube's Docker environment:

```bash
minikube docker-env
eval $(minikube docker-env)
docker build -t kubernetes-demo:1.0.0 .
kubectl apply -f k8s/
```

On PowerShell, Minikube prints a PowerShell-specific command:

```powershell
minikube docker-env | Invoke-Expression
docker build -t kubernetes-demo:1.0.0 .
kubectl apply -f k8s/
```

### Kind

Build locally, then load the image into the Kind cluster:

```bash
docker build -t kubernetes-demo:1.0.0 .
kind load docker-image kubernetes-demo:1.0.0
kubectl apply -f k8s/
```

## Deploy

Apply the manifests:

```bash
kubectl apply -f k8s/
```

This works because every namespaced manifest already declares `namespace: kubernetes-demo`, and the namespace manifest is included.

## Verify Deployment

Check all objects:

```bash
kubectl get namespaces
kubectl get pods -n kubernetes-demo
kubectl get deployments -n kubernetes-demo
kubectl get services -n kubernetes-demo
kubectl get hpa -n kubernetes-demo
kubectl get all -n kubernetes-demo
```

Expected Pods:

```text
READY 1/1
STATUS Running
```

There should be `3` Pods because the Deployment starts with `replicas: 3`.

## Access the Application

Because the Service is ClusterIP, use port-forwarding from your machine:

```bash
kubectl port-forward service/kubernetes-demo 8080:80 -n kubernetes-demo
```

Then open:

```text
http://localhost:8080
http://localhost:8080/health
http://localhost:8080/ready
```

Test with curl:

```bash
curl http://localhost:8080
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

To confirm the Service routes traffic to Pods, call `/api/info` multiple times and watch the hostname. You should eventually see different Pod hostnames:

```bash
curl http://localhost:8080/api/info
```

## Logs

Follow logs from the Deployment:

```bash
kubectl logs -f deployment/kubernetes-demo -n kubernetes-demo
```

Show logs from one Pod:

```bash
kubectl logs <pod-name> -n kubernetes-demo
```

## Manual Scaling

Scale to 5 replicas:

```bash
kubectl scale deployment kubernetes-demo --replicas=5 -n kubernetes-demo
kubectl get pods -n kubernetes-demo
```

Scale back to 3 replicas:

```bash
kubectl scale deployment kubernetes-demo --replicas=3 -n kubernetes-demo
```

## HPA Scaling Test

Watch the HPA:

```bash
kubectl get hpa -n kubernetes-demo
kubectl get pods -n kubernetes-demo -w
```

To generate traffic without installing a load-testing tool, run a temporary curl Pod:

```bash
kubectl run curl-load \
  --image=curlimages/curl \
  --rm -it \
  --restart=Never \
  -n kubernetes-demo \
  -- sh -c 'while true; do curl -s http://kubernetes-demo/health >/dev/null; done'
```

This creates request load, but it may not generate enough CPU pressure to trigger HPA for a lightweight Express app. For real HPA testing, use a controlled CPU-heavy endpoint or a proper load generator after confirming it is safe for the cluster.

## Troubleshooting

Start by identifying the real problem:

```bash
kubectl get pods -n kubernetes-demo
kubectl describe pod <pod-name> -n kubernetes-demo
kubectl logs <pod-name> -n kubernetes-demo
kubectl get events -n kubernetes-demo --sort-by=.lastTimestamp
kubectl describe deployment kubernetes-demo -n kubernetes-demo
kubectl describe service kubernetes-demo -n kubernetes-demo
```

Common issues:

- `ImagePullBackOff`: the cluster cannot find `kubernetes-demo:1.0.0`. Build the image for Docker Desktop, build inside Minikube, or load it into Kind.
- HPA shows unknown metrics: Metrics Server is missing or not working.
- Pods not ready: check `/ready`, container logs, and readiness probe events.
- Service not routing: check that the Service selector matches the Pod labels.

## Remove the Application

Delete the namespace:

```bash
kubectl delete namespace kubernetes-demo
```

This removes all objects in the demo namespace.

## Commands to Memorize

```bash
kubectl config current-context
kubectl cluster-info
kubectl apply -f k8s/
kubectl get all -n kubernetes-demo
kubectl describe pod <pod-name> -n kubernetes-demo
kubectl logs -f deployment/kubernetes-demo -n kubernetes-demo
kubectl port-forward service/kubernetes-demo 8080:80 -n kubernetes-demo
kubectl scale deployment kubernetes-demo --replicas=5 -n kubernetes-demo
kubectl get hpa -n kubernetes-demo
kubectl delete namespace kubernetes-demo
```

## Current Verification Status

These checks were attempted in this workspace:

- `kubectl version --client`: failed because `kubectl` is not installed or not on `PATH`.
- `docker version`: failed because Docker CLI is not installed or not on `PATH`.

Because of that, the image was not built and the manifests were not deployed from this session.
