# claude-waitrose-mcp

Namespace hosting a single service:

- **waitrose-mcp** — public-facing MCP server exposing Waitrose product
  search (anonymous). Source in [zuzak/waitrose-mcp](https://github.com/zuzak/waitrose-mcp).

Tools exposed: `search_products`, `browse_products`,
`get_products_by_line_numbers`, `get_promotion_products`. All anonymous —
the upstream API accepts an `Authorization: Bearer unauthenticated` token
for product browsing without login.

## Auth extension point

Authenticated tools (trolley, orders, slots) are not yet implemented. When
added, the pattern is: set `WAITROSE_USERNAME` and `WAITROSE_PASSWORD` as
a Secret-backed env pair on the Deployment, and the server will log in at
startup and enable the authenticated tools. See the server README for the
extension point.

## No ingress basic auth

Unlike `claude-grocy` and `claude-vestibule`, this ingress is unauthenticated
— the upstream Waitrose data is public, and there is no write surface to
gate. Leave the `nginx.ingress.kubernetes.io/auth-*` annotations off.

## Prerequisites before this app will run

The `ghcr.io/zuzak/waitrose-mcp` package must be public for the cluster to
pull it without an `imagePullSecret`. GHCR packages inherit the source
repository's visibility on first publish; if the `zuzak/waitrose-mcp`
repo is still private when the first image is pushed, the package needs
to be set to public explicitly (GitHub → Packages → *waitrose-mcp* →
Package settings → Change visibility → Public). Same pattern as
`claude-grocy`, `claude-vestibule`, `router-mcp`.

## Endpoints

- `https://waitrose.mcp.k3s.fluv.net/mcp` — MCP streamable HTTP endpoint
- `https://waitrose.mcp.k3s.fluv.net/healthz` — liveness endpoint

## Why `claude-waitrose-mcp` (namespace)

The `claude` Argo CD project permits destinations in namespaces matching
`claude` or `claude-*`. Naming the namespace `claude-waitrose-mcp` keeps
the app under that project without widening its destination allowlist.
