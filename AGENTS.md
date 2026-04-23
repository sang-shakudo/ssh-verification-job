# AGENTS.md

## Project

SSH verification job — checks SSH connectivity and Git repo access to an in-cluster Gitea server. Runs inside a Kubernetes pod.

## Runtime

- **Python 3.14** required (`requires-python = ">=3.14"`)
- Package manager: **uv**

## Commands

```sh
uv run main.py            # run locally (requires cluster network access)
uv sync                   # install dependencies
uv add <package>          # add a dependency
```

Production run uses `run.sh`, which bootstraps uv, creates venv, syncs deps, `chmod 400` the SSH key, then runs the job.

## Architecture

- Single-module project; entry point is `main.py:main()`
- `main.py` does two checks:
  1. SSH connectivity via **paramiko** (Ed25519 key, falls back to RSA)
  2. Git repo access via `git ls-remote` (uses `GIT_SSH_COMMAND` override)
- Both target `gitea-ssh.hyperplane-gitea.svc.cluster.local` — will **fail outside a cluster**

## Gotchas

- The SSH private key file `rbac-policies-rbac-manager-key-for-gitea` is committed to the repo by design. **Do not log, print, or expose its contents.**
- Key file must be `chmod 400` before use (handled in `run.sh`; manual runs need it too)
- No `.gitignore` — `.venv` and the key are untracked in git but present on disk. Branch default is `main`.
- No tests, CI, or linting configured