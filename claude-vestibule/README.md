# claude-vestibule

Generic HTTP proxy for authenticated upstream APIs. See
[github.com/zuzak/vestibule](https://github.com/zuzak/vestibule).

## Prerequisites before this app will run

Two things must happen out-of-band, because they cannot live in this
public repo.

### 1. Apply the `vestibule-config` Secret

The proxy reads its YAML config from the file path `VESTIBULE_CONFIG`
(set to `/etc/vestibule/config.yaml` in the Deployment). The config is
mounted from the `vestibule-config` Secret, key `config.yaml`.

Prepare the config locally using the schema in the vestibule repo's
`example.yaml`, with real credentials substituted in, then apply:

```
kubectl create secret generic vestibule-config \
  --namespace claude-vestibule \
  --from-file=config.yaml=./config.yaml
```

The pod remounts the Secret on rotation; rolling the Deployment
(`kubectl rollout restart deployment/vestibule -n claude-vestibule`)
picks up the new contents immediately.

Do not commit the real config to any repo — public or private. The
credentials live in the cluster's secret store and nowhere else.

### 2. Fix the ingress IP allowlist

`ingress.yaml` ships with
`nginx.ingress.kubernetes.io/whitelist-source-range: "127.0.0.1/32"`
as a safety default: nothing outside the pod network can reach the
service until this annotation is edited to include the real client
CIDRs. The primary security layer is the IP allowlist, not the inbound
apikey check — the apikey is visible in logs and is not a secret.

The intended ranges are Anthropic's `web_fetch` egress ranges (for
Claude Chat) plus the operator's Tailscale network. Update the
annotation once those ranges are confirmed, then commit the change via
PR.

### 3. Make the GHCR package public (first deploy only)

The image lives at `ghcr.io/zuzak/vestibule`. GHCR packages inherit the
source repository's visibility on first publish; until the vestibule
repo is made public, the package needs to be set to public explicitly
(GitHub → vestibule → Packages → vestibule → Package settings → Change
visibility → Public) or an `imagePullSecret` added to the Deployment.
Other Claude-facing apps in this cluster (`claude-grocy`,
`router-mcp`) rely on public packages, so this follows the existing
pattern.

## Endpoints

- `https://vestibule.mcp.k3s.fluv.net/<upstream>/<endpoint>?apikey=…` —
  proxied upstream call (behind the ingress IP allowlist).
- `vestibule.claude-vestibule.svc.cluster.local:8080/healthz` —
  in-cluster liveness/readiness endpoint.
- `vestibule.claude-vestibule.svc.cluster.local:9090/metrics` —
  Prometheus scrape target, pod-network only; not exposed via ingress.

## Why `claude-vestibule` (namespace) and not `vestibule`

The `claude` Argo CD project permits destinations in namespaces
matching `claude` or `claude-*`. Naming the namespace
`claude-vestibule` keeps the app under that project without widening
its destination allowlist.
