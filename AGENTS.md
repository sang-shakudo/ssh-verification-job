# AGENTS.md

## Project

SSH verification job — a Python CLI/script for verifying SSH connectivity. Currently a skeleton.

## Runtime

- **Python 3.14** required (`.python-version` and `requires-python` define this; don't default to an older version)
- Package manager: **uv**

## Commands

```sh
uv run main.py            # run the job
uv add <package>          # add a dependency
uv run pytest             # run tests (once test deps are added)
```

## Structure

- Single-module project; entry point is `main.py:main()`
- No tests, CI, or linting configured yet

## Constraints

- `pyproject.toml` uses `requires-python = ">=3.14"` — don't suggest code incompatible with 3.14