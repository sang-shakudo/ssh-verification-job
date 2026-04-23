import os
import sys
import subprocess
from pathlib import Path

import paramiko

SSH_HOST = "gitea-ssh.hyperplane-gitea.svc.cluster.local"
SSH_PORT = 22
SSH_USER = "git"
GIT_REPO_URL = "git@gitea-ssh.hyperplane-gitea.svc.cluster.local:sang/rbac-policies.git"
KNOWN_HOSTS_FILE = f"{SSH_HOST}.known-hosts"
PARAMIKO_KNOWN_HOSTS_FILE = f"{SSH_HOST}.paramiko-known-hosts"


def scan_ssh_host_keys(host: str = SSH_HOST, output_path: str = KNOWN_HOSTS_FILE) -> str | None:
    try:
        result = subprocess.run(
            ["ssh-keyscan", "-t", "ed25519,rsa", host],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 or not result.stdout.strip():
            print(f"[FAIL] ssh-keyscan for {host} failed: {result.stderr.strip()}")
            return None
        Path(output_path).write_text(result.stdout)
        print(f"[OK] Wrote host keys for {host} to {output_path}")
        return result.stdout
    except Exception as e:
        print(f"[FAIL] ssh-keyscan for {host} failed: {e}")
        return None


def verify_ssh_connectivity(key_path: str, host: str = SSH_HOST, port: int = SSH_PORT, user: str = SSH_USER, known_hosts_path: str = PARAMIKO_KNOWN_HOSTS_FILE) -> bool:
    try:
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
    except paramiko.SSHException:
        key = paramiko.RSAKey.from_private_key_file(key_path)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=user, pkey=key, timeout=10)
        transport = client.get_transport()
        if transport is None:
            raise paramiko.SSHException("No transport after connect")
        remote_key = transport.get_remote_server_key()
        host_keys = paramiko.HostKeys(known_hosts_path)
        host_keys.add(host, remote_key.get_name(), remote_key)
        host_keys.save(known_hosts_path)
        print(f"[OK] SSH connectivity to {user}@{host}:{port} succeeded")
        print(f"[OK] Wrote paramiko host key for {host} to {known_hosts_path}")
        return True
    except Exception as e:
        print(f"[FAIL] SSH connectivity to {user}@{host}:{port} failed: {e}")
        return False
    finally:
        client.close()


def verify_git_repo_access(key_path: str, known_hosts_file: str = KNOWN_HOSTS_FILE, repo_url: str = GIT_REPO_URL) -> bool:
    identity_flag = f"-i {key_path}"
    known_hosts_flag = f"-o UserKnownHostsFile={known_hosts_file} -o StrictHostKeyChecking=yes"
    try:
        result = subprocess.run(
            ["git", "ls-remote", repo_url],
            env={
                **os.environ,
                "GIT_SSH_COMMAND": f"ssh {identity_flag} {known_hosts_flag}",
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

    host_keys = scan_ssh_host_keys()
    ssh_ok = verify_ssh_connectivity(key_path)
    git_ok = verify_git_repo_access(key_path) if host_keys else False

    if not (ssh_ok and git_ok):
        sys.exit(1)


if __name__ == "__main__":
    main()