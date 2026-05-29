#!/usr/bin/env python3
"""Retry downloading incomplete Keploy image layers from ghcr.io."""
import json, os, subprocess, sys, urllib.request

OUTDIR = "/tmp/keploy-image"
IMAGE = "keploy/keploy"
REGISTRY = "ghcr.io"

# Get auth token
print("Getting auth token...")
token_url = f"https://{REGISTRY}/token?scope=repository:{IMAGE}:pull&service={REGISTRY}"
req = urllib.request.Request(token_url)
with urllib.request.urlopen(req, timeout=30) as resp:
    token = json.loads(resp.read())["token"]
print(f"Token OK: {token[:30]}...")

# Read manifest
with open(os.path.join(OUTDIR, "manifest.json")) as f:
    manifest = json.load(f)

config_digest = manifest["config"]["digest"]
layers = manifest["layers"]

# Check and retry each layer
for i, l in enumerate(layers):
    path = os.path.join(OUTDIR, f"layer_{i}.tar.gz")
    actual = os.path.getsize(path) if os.path.exists(path) else 0
    expected = l.get("size", 0)

    if actual == expected:
        print(f"Layer {i}: OK ({actual} bytes)")
        continue

    print(f"\nLayer {i}: RETRY ({actual}/{expected} bytes, missing {expected-actual} bytes)")
    url = f"https://{REGISTRY}/v2/{IMAGE}/blobs/{l['digest']}"

    # Use curl with retry, no max-time limit
    # Use -C - to resume if possible
    cmd = [
        "curl", "-sL", "--retry", "5", "--retry-delay", "5",
        "-H", f"Authorization: Bearer {token}",
        "--connect-timeout", "60",
        "-o", path,
        url,
    ]
    print(f"  Downloading (no timeout limit)...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    new_size = os.path.getsize(path) if os.path.exists(path) else 0
    if new_size == expected:
        print(f"  OK: {new_size} bytes")
    else:
        print(f"  WARNING: {new_size}/{expected} bytes")
        if result.stderr:
            print(f"  stderr: {result.stderr[:200]}")

# Verify config
config_path = os.path.join(OUTDIR, "config.json")
config_size = manifest["config"].get("size", 0)
config_actual = os.path.getsize(config_path) if os.path.exists(config_path) else 0
if config_actual != config_size or config_actual == 0:
    print(f"\nRetrying config download ({config_size} bytes)...")
    url = f"https://{REGISTRY}/v2/{IMAGE}/blobs/{config_digest}"
    cmd = ["curl", "-sL", "-H", f"Authorization: Bearer {token}", "-o", config_path, url]
    subprocess.run(cmd, capture_output=True, timeout=60)
    print(f"  Config: {os.path.getsize(config_path)} bytes")

# Final check
print("\n=== Final verification ===")
all_ok = True
for i, l in enumerate(layers):
    path = os.path.join(OUTDIR, f"layer_{i}.tar.gz")
    actual = os.path.getsize(path) if os.path.exists(path) else 0
    expected = l.get("size", 0)
    status = "OK" if actual == expected else f"INCOMPLETE ({actual}/{expected})"
    print(f"Layer {i}: {status}")
    if actual != expected:
        all_ok = False

config_actual = os.path.getsize(config_path) if os.path.exists(config_path) else 0
if config_actual == 0:
    all_ok = False
    print("Config: MISSING")
else:
    print(f"Config: {config_actual} bytes")

if all_ok:
    print("\n=== All complete! Creating Docker image... ===")

    # Create docker manifest
    docker_manifest = [{
        "Config": "config.json",
        "RepoTags": ["ghcr.io/keploy/keploy:latest"],
        "Layers": [f"layer_{i}.tar.gz" for i in range(len(layers))],
    }]
    manifest_out = os.path.join(OUTDIR, "manifest.json")
    # Backup original manifest
    os.rename(manifest_out, os.path.join(OUTDIR, "oci_manifest.json"))
    with open(manifest_out, "w") as f:
        json.dump(docker_manifest, f)

    # Create repositories
    config_short = config_digest.split(":")[1] if ":" in config_digest else config_digest
    repos = json.dumps({"ghcr.io/keploy/keploy": {"latest": config_short}})
    with open(os.path.join(OUTDIR, "repositories"), "w") as f:
        f.write(repos)

    # Create tarball
    os.chdir(OUTDIR)
    files = "config.json repositories manifest.json " + " ".join(f"layer_{i}.tar.gz" for i in range(len(layers)))
    print(f"Creating tarball...")
    os.system(f"tar cf /tmp/keploy-image.tar {files}")
    size_mb = os.path.getsize("/tmp/keploy-image.tar") / 1024 / 1024
    print(f"Tarball: {size_mb:.1f} MB")

    # Load into Docker
    print("Loading into Docker...")
    os.system("docker load -i /tmp/keploy-image.tar 2>&1")
    print("\n=== RESULT ===")
    os.system("docker images | grep keploy")
else:
    print("\nERROR: Some layers still incomplete. Cannot create image.")
    sys.exit(1)
