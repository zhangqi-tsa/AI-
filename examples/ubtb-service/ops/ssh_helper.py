#!/usr/bin/env python3
"""SSH helper for remote command execution and file upload.

All credentials are read from environment variables.
See .env.example for required variables.
"""
import paramiko
import sys
import os


def _require_env(name):
    val = os.environ.get(name, "")
    if not val:
        print(f"ERROR: Required environment variable {name} is not set.")
        sys.exit(1)
    return val


HOST = _require_env("DEPLOY_HOST")
USER = _require_env("DEPLOY_USER")
PASS = _require_env("DEPLOY_PASSWORD")

def ssh_exec(cmd, timeout=30):
    """Execute a command on the remote server and return output."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=10,
                   look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    exit_code = stdout.channel.recv_exit_status()
    client.close()
    return out, err, exit_code

def sftp_upload(local_path, remote_path):
    """Upload a file via SFTP."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=10)
    sftp = client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    client.close()

def sftp_mkdir_p(remote_dir):
    """Create remote directory recursively."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=10)
    sftp = client.open_sftp()
    dirs = []
    d = remote_dir
    while d and d != '/':
        try:
            sftp.stat(d)
            break
        except FileNotFoundError:
            dirs.append(d)
            d = os.path.dirname(d)
    for d in reversed(dirs):
        try:
            sftp.mkdir(d)
        except IOError:
            pass
    sftp.close()
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ssh_helper.py exec <command>")
        print("       ssh_helper.py upload <local> <remote>")
        sys.exit(1)

    action = sys.argv[1]

    if action == "exec":
        cmd = " ".join(sys.argv[2:])
        out, err, code = ssh_exec(cmd)
        if out: print(out, end="")
        if err: print(err, end="", file=sys.stderr)
        sys.exit(code)

    elif action == "upload":
        local = sys.argv[2]
        remote = sys.argv[3]
        sftp_mkdir_p(os.path.dirname(remote))
        sftp_upload(local, remote)
        print(f"Uploaded {local} -> {remote}")
