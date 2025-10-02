This repository contains the configuration for my personal Kubernetes cluster.

To bootstrap anew:
1. provision a cluster (I used [k3s](https://k3s.io/)
2. install [Argo CD](https://argo-cd.readthedocs.io/en/stable/getting_started/)
3. sign in and click "new app" then "edit as YAML"
4. paste in the contents of [apps.yaml](apps/apps.yaml)
