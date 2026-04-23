import sys
import subprocess

import paramiko

SSH_HOST = "gitea.shabbir-dev.canopyhub.io"
SSH_PORT = 22
SSH_USER = "git"
GIT_REPO_URL = "git@gitea.shabbir-dev.canopyhub.io:sang/rbac-policies.git"


def verify_ssh_connectivity(key_path: str, host: str = SSH_HOST, port: int = SSH_PORT, user: str = SSH_USER) -> bool:
    try:
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
    except paramiko.SSHException:
        key = paramiko.RSAKey.from_private_key_file(key_path)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=user, pkey=key, timeout=10)
        print(f"[OK] SSH connectivity to {user}@{host}:{port} succeeded")
        return True
    except Exception as e:
        print(f"[FAIL] SSH connectivity to {user}@{host}:{port} failed: {e}")
        return False
    finally:
        client.close()


def verify_git_repo_access(key_path: str, repo_url: str = GIT_REPO_URL) -> bool:
    identity_flag = f"-i {key_path}"
    try:
        result = subprocess.run(
            ["git", "ls-remote", repo_url],
            env={
                **__import__("os").environ,
                "GIT_SSH_COMMAND": f"ssh {identity_flag} -o StrictHostKeyChecking=no",
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"[OK] Git repository access to {repo_url} succeeded")
            return True
        else:
            print(f"[FAIL] Git repository access to {repo_url} failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[FAIL] Git repository access to {repo_url} failed: {e}")
        return False


def main():
    key_path = 'rbac-policies-rbac-manager-key-for-gitea'

    ssh_ok = verify_ssh_connectivity(key_path)
    git_ok = verify_git_repo_access(key_path)

    if not (ssh_ok and git_ok):
        sys.exit(1)


if __name__ == "__main__":
    main()