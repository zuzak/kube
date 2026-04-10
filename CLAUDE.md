# Claude Code guide for this repo

This is a GitOps repository for a personal two-node k3s cluster managed by Argo CD.

## Cluster layout

| Node | Role | Notes |
|------|------|-------|
| `saraneth` | VPS (Bitfolk), amd64, 4GB RAM | Edge/ingress node; runs non-k8s services (PostgreSQL, Node.js, Tailscale) alongside k3s |
| `pi.home.arpa` | Raspberry Pi 5, arm64, 8GB RAM | Primary workload node |

Nodes are connected via Tailscale. The k3s datastore is PostgreSQL on `saraneth`.

## Node configuration (manual, outside Argo CD)

`saraneth` has two taints applied manually via `kubectl`:
- `CriticalAddonsOnly=true:PreferNoSchedule`
- `node-role=edge:NoSchedule`

Kubelet reservations are configured on `saraneth` in
`/etc/rancher/k3s/config.yaml.d/kubelet-reservations.yaml` (leaving ~1670Mi
allocatable for pods). See README for the file contents.

## Repository structure

- `apps/` — Argo CD Application manifests (the "app of apps" pattern)
- `kube/` — raw Kubernetes manifests applied directly (storage classes, cluster issuers, etc.)
- `oauthproxy/` — oauth2-proxy deployment for Prometheus auth

## Making changes

All application configuration goes through Argo CD. Push to `main` and Argo CD
will sync automatically. To apply immediately, trigger a sync in the Argo CD UI.

When adding helm values to an Application manifest, place them under
`spec.source.helm.values`.

## Pre-commit hooks

The repo uses pre-commit hooks (`k8svalidate`, `check-yaml`, whitespace fixes).
These run automatically on commit. To run manually: `pre-commit run --all-files`.

## Applying node-level changes

Changes to node taints or kubelet config on `saraneth` must be applied manually
via `ssh z` — they are not managed by Argo CD. Document any such changes in
the README.

## Outstanding work

- Add Pi node affinity (`preferredDuringSchedulingIgnoredDuringExecution`) and
  `node-role=edge` taint toleration to workload helm charts for Pi-first
  scheduling with saraneth fallback
- Deploy the Descheduler so pods rebalance back to Pi after a Pi outage
- Debug Tailscale MagicDNS on the Pi (currently disabled)
