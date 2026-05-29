#!/usr/bin/env python3
"""Deploy UBTB project to WSL and run the full MVP flow."""
import paramiko
import os
import sys
import time

HOST = "172.29.162.248"
USER = "shc"
PASS = "938729131"
SUDO_PASS = "938729131"
REMOTE_BASE = "/home/shc/ubtb-project"
LOCAL_PROJECT = r"C:\Users\13794\Desktop\workspace\工作\2026\轨迹认证（claude）"
LOCAL_TEST_ASSETS = r"C:\Users\13794\Desktop\workspace\工作\2026\AI 辅助生成和维护接口回归测试资产\ai-keploy-test-assets"

def get_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=10, look_for_keys=False, allow_agent=False)
    return client

def exec_cmd(cmd, timeout=60, use_sudo=False):
    client = get_client()
    if use_sudo:
        cmd = f"echo {SUDO_PASS} | sudo -S bash -c '{cmd}'"
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    client.close()
    return out, err, code

def exec_cmd_print(cmd, timeout=120, use_sudo=False):
    out, err, code = exec_cmd(cmd, timeout, use_sudo)
    if out.strip():
        print(out.strip())
    if err.strip() and "[sudo]" not in err:
        print(f"STDERR: {err.strip()}")
    print(f"[exit: {code}]")
    return code

def upload_dir(local_dir, remote_dir):
    """Upload a directory tree via SFTP."""
    client = get_client()
    sftp = client.open_sftp()

    def ensure_dir(d):
        try:
            sftp.stat(d)
        except FileNotFoundError:
            ensure_dir(os.path.dirname(d))
            try:
                sftp.mkdir(d)
            except IOError:
                pass

    count = 0
    for root, dirs, files in os.walk(local_dir):
        # Skip hidden dirs, __pycache__, node_modules, target
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', 'target', '.git')]
        rel = os.path.relpath(root, local_dir)
        remote_root = os.path.join(remote_dir, rel).replace('\\', '/')

        ensure_dir(remote_root)

        for f in files:
            if f.startswith('.') or f == '.DS_Store':
                continue
            local_file = os.path.join(root, f)
            remote_file = os.path.join(remote_root, f).replace('\\', '/')
            sftp.put(local_file, remote_file)
            count += 1

    sftp.close()
    client.close()
    return count

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "help"

    if action == "upload":
        print("=== Uploading UBTB project ===")
        n = upload_dir(LOCAL_PROJECT, REMOTE_BASE)
        print(f"Uploaded {n} files to {REMOTE_BASE}")

    elif action == "upload-test-assets":
        print("=== Uploading test assets ===")
        n = upload_dir(LOCAL_TEST_ASSETS, f"{REMOTE_BASE}/test-assets")
        print(f"Uploaded {n} files to {REMOTE_BASE}/test-assets")

    elif action == "exec":
        cmd = " ".join(sys.argv[2:])
        exec_cmd_print(cmd)

    elif action == "sudo":
        cmd = " ".join(sys.argv[2:])
        exec_cmd_print(cmd, use_sudo=True)

    elif action == "setup-docker":
        print("=== Setting up Docker compose ===")
        # Fix port conflict - use 8081 instead of 8080
        cmd = f"""cd {REMOTE_BASE} &&
sed -i 's/8080:8080/8081:8080/g' docker/docker-compose.yml &&
cat docker/docker-compose.yml | grep '8081'"""
        exec_cmd_print(cmd)

        print("\n=== Starting Docker compose ===")
        cmd = f"cd {REMOTE_BASE}/docker && echo {SUDO_PASS} | sudo -S docker compose up -d --build 2>&1"
        exec_cmd_print(cmd, timeout=300)

    elif action == "health-check":
        print("=== Checking health ===")
        for i in range(30):
            out, err, code = exec_cmd("curl -sf http://127.0.0.1:8081/actuator/health 2>&1 || echo NOT_READY", timeout=5)
            if "UP" in out or "status" in out.lower():
                print(f"App is healthy: {out.strip()}")
                break
            print(f"Attempt {i+1}/30: waiting...")
            time.sleep(5)
        else:
            print("App did not become healthy")
            exec_cmd_print(f"echo {SUDO_PASS} | sudo -S docker compose -f {REMOTE_BASE}/docker/docker-compose.yml logs --tail 20 backend 2>&1")

    elif action == "run-flow":
        print("=== Running UBTB flow script ===")
        cmd = f"""cd {REMOTE_BASE}/test-assets &&
export BASE_URL=http://127.0.0.1:8081 &&
export TEST_EMAIL=admin@ubtb.com &&
export TEST_PASSWORD=123456 &&
python3 generated/ubtb-service/core-flow.py 2>&1"""
        exec_cmd_print(cmd, timeout=30)

    elif action == "install-keploy":
        print("=== Installing Keploy ===")
        cmd = "curl -sL -o keploy.sh https://keploy.io/install.sh && bash keploy.sh 2>&1"
        exec_cmd_print(cmd, timeout=120)

    elif action == "keploy-record":
        print("=== Running Keploy record ===")
        compose_file = f"{REMOTE_BASE}/docker/docker-compose.yml"
        app_cmd = f"echo {SUDO_PASS} | sudo -S docker compose -f {compose_file} up"
        cmd = (
            f"cd {REMOTE_BASE}/test-assets && "
            f"export BASE_URL=http://127.0.0.1:8081 && "
            f"export TEST_EMAIL=admin@ubtb.com && "
            f"export TEST_PASSWORD=123456 && "
            f"export ENVIRONMENT=test && "
            f'export APP_CMD="{app_cmd}" && '
            f"export HEALTH_URL=http://127.0.0.1:8081/actuator/health && "
            f"export FLOW_SCRIPT=generated/ubtb-service/core-flow.py && "
            f"export SERVICE_NAME=ubtb-service && "
            f"export STARTUP_TIMEOUT_SECONDS=120 && "
            f"export KEPLOY_READY_WAIT_SECONDS=8 && "
            f"export KEPLOY_DIR=keploy && "
            f"echo {SUDO_PASS} | sudo -S bash scripts/record-keploy.sh 2>&1"
        )
        exec_cmd_print(cmd, timeout=300)

    elif action == "review":
        print("=== Running review ===")
        cmd = f"""cd {REMOTE_BASE}/test-assets &&
python3 scripts/review-keploy-assets.py --service ubtb-service --keploy-dir keploy --output reports/ubtb-service/keploy-review.md 2>&1 &&
echo '=== Report ===' &&
cat reports/ubtb-service/keploy-review.md"""
        exec_cmd_print(cmd, timeout=30)

    elif action == "sanitize":
        print("=== Running sanitize check ===")
        cmd = f"""cd {REMOTE_BASE}/test-assets &&
python3 scripts/sanitize-check.py --dir keploy/ 2>&1"""
        exec_cmd_print(cmd, timeout=30)

    else:
        print("Usage: python deploy.py <action>")
        print("  upload           - Upload UBTB project")
        print("  upload-test-assets - Upload test assets")
        print("  setup-docker     - Fix port + start docker compose")
        print("  health-check     - Wait for app health")
        print("  run-flow         - Run flow script directly")
        print("  install-keploy   - Install Keploy CLI")
        print("  keploy-record    - Run Keploy record")
        print("  review           - Run asset review")
        print("  sanitize         - Run sanitize check")
        print("  exec <cmd>       - Run arbitrary command")
        print("  sudo <cmd>       - Run with sudo")
