#!/usr/bin/env python3
"""
Render cloud-init-template.yaml and apply it as the hcloud-init-data secret.

By default, substitution values are read from the existing secret (useful when
re-rendering after a template change). Pass --authkey and/or --token to override.

Usage:
    python3 update-cloud-init-secret.py
    python3 update-cloud-init-secret.py --authkey tskey-auth-... --token K10...
    python3 update-cloud-init-secret.py --dry-run
"""
import argparse, base64, re, subprocess, sys
from pathlib import Path

TEMPLATE = Path(__file__).parent / "cloud-init-template.yaml"
SECRET_NAME = "hcloud-init-data"
SECRET_NS = "kube-system"


def kubectl(*args):
    r = subprocess.run(["kubectl", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"kubectl error: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return r.stdout.strip()


def get_existing_values():
    raw = kubectl("get", "secret", "-n", SECRET_NS, SECRET_NAME,
                  "-o", "jsonpath={.data.cloud-init}")
    existing = base64.b64decode(base64.b64decode(raw)).decode()
    ts_match = re.search(r'--authkey=(tskey-\S+)', existing)
    k3s_match = re.search(r'K3S_TOKEN=(\S+)', existing)
    if not ts_match or not k3s_match:
        print("ERROR: could not extract values from existing secret", file=sys.stderr)
        sys.exit(1)
    return ts_match.group(1), k3s_match.group(1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--authkey", help="Tailscale auth key (default: read from existing secret)")
    p.add_argument("--token", help="k3s node token (default: read from existing secret)")
    p.add_argument("--dry-run", action="store_true", help="Print rendered cloud-init without applying")
    args = p.parse_args()

    if args.authkey and args.token:
        ts_key, k3s_token = args.authkey, args.token
    else:
        print("Reading existing values from secret...")
        existing_ts, existing_k3s = get_existing_values()
        ts_key = args.authkey or existing_ts
        k3s_token = args.token or existing_k3s

    template = TEMPLATE.read_text()
    rendered = template.replace("__TAILSCALE_AUTH_KEY__", ts_key).replace("__K3S_TOKEN__", k3s_token)

    if args.dry_run:
        print(rendered)
        return

    value = base64.b64encode(rendered.encode()).decode()
    patch = f'[{{"op":"replace","path":"/data/cloud-init","value":"{value}"}}]'

    print(f"Patching {SECRET_NS}/{SECRET_NAME}...")
    kubectl("patch", "secret", "-n", SECRET_NS, SECRET_NAME,
            "--type=json", f"--patch={patch}")
    print("Done.")


if __name__ == "__main__":
    main()
