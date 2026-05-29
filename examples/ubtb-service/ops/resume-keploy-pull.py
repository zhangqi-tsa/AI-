#!/usr/bin/env python3
"""Check keploy image download status and resume missing layers."""
import json, os, subprocess, sys

OUTDIR = "/tmp/keploy-image"
IMAGE = "keploy/keploy"
REGISTRY = "ghcr.io"

# Get token
import urllib.request
token_url = f"https://{REGISTRY}/token?scope=repository:{IMAGE}:pull&service={REGISTRY}"
req = urllib.request.Request(token_url)
with urllib.request.urlopen(req, timeout=15) as resp:
    token = json.loads(resp.read())["token"]

# Read manifest
with open(os.path.join(OUTDIR, "manifest.json")) as f:
    manifest = json.load(f)

config_digest = manifest["config"]["digest"]
config_size = manifest["config"].get("size", 0)
layers = manifest["layers"]

print(f"Config: {config_digest[:30]}... expected={config_size}")
for i, l in enumerate(layers):
    path = os.path.join(OUTDIR, f"layer_{i}.tar.gz")
    actual = os.path.getsize(path) if os.path.exists(path) else 0
    expected = l.get("size", 0)
    status = "OK" if actual == expected else f"INCOMPLETE ({actual}/{expected})"
    print(f"Layer {i}: {l['digest'][:30]}... {status}")

# Download config if missing
config_path = os.path.join(OUTDIR, "config.json")
config_actual = os.path.getsize(config_path) if os.path.exists(config_path) else 0
if config_actual != config_size or config_actual == 0:
    print(f"\nDownloading config ({config_size} bytes)...")
    url = f"https://{REGISTRY}/v2/{IMAGE}/blobs/{config_digest}"
    cmd = f'curl -sL -H "Authorization: Bearer {token}" "{url}" > {config_path}'
    os.system(cmd)
    print(f"Config: {os.path.getsize(config_path)} bytes")

# Download missing/incomplete layers
for i, l in enumerate(layers):
    path = os.path.join(OUTDIR, f"layer_{i}.tar.gz")
    actual = os.path.getsize(path) if os.path.exists(path) else 0
    expected = l.get("size", 0)
    if actual != expected:
        print(f"\nDownloading layer {i} ({expected/1024/1024:.1f} MB)...")
        url = f"https://{REGISTRY}/v2/{IMAGE}/blobs/{l['digest']}"
        cmd = f'curl -sL -H "Authorization: Bearer {token}" --connect-timeout 30 --max-time 900 "{url}" > {path}'
        os.system(cmd)
        new_size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"Layer {i}: {new_size} bytes (expected {expected})")
        if new_size != expected:
            print(f"WARNING: Layer {i} download may be incomplete!")

# Check all layers are complete
all_ok = True
for i, l in enumerate(layers):
    path = os.path.join(OUTDIR, f"layer_{i}.tar.gz")
    actual = os.path.getsize(path) if os.path.exists(path) else 0
    expected = l.get("size", 0)
    if actual != expected:
        print(f"\nERROR: Layer {i} incomplete ({actual}/{expected})")
        all_ok = False

config_actual = os.path.getsize(config_path) if os.path.exists(config_path) else 0
if config_actual == 0:
    print("ERROR: Config download failed")
    all_ok = False

if all_ok:
    print("\n=== All layers complete! Creating Docker image tarball... ===")
    # Create docker manifest.json
    docker_manifest = [{
        "Config": "config.json",
        "RepoTags": ["ghcr.io/keploy/keploy:latest"],
        "Layers": [f"layer_{i}.tar.gz" for i in range(len(layers))],
    }]
    with open(os.path.join(OUTDIR, "docker_manifest.json"), "w") as f:
        json.dump(docker_manifest, f)

    # Copy as manifest.json for docker load
    import shutil
    shutil.copy(os.path.join(OUTDIR, "docker_manifest.json"), os.path.join(OUTDIR, "manifest.json"))

    # Create repositories
    config_short = config_digest.split(":")[1] if ":" in config_digest else config_digest
    repos = json.dumps({"ghcr.io/keploy/keploy": {"latest": config_short}})
    with open(os.path.join(OUTDIR, "repositories"), "w") as f:
        f.write(repos)

    # Create tarball
    os.chdir(OUTDIR)
    files = "config.json repositories manifest.json " + " ".join(f"layer_{i}.tar.gz" for i in range(len(layers)))
    os.system(f"tar cf /tmp/keploy-image.tar {files}")

    size_mb = os.path.getsize("/tmp/keploy-image.tar") / 1024 / 1024
    print(f"Tarball: {size_mb:.1f} MB")

    # Load into Docker
    print("Loading into Docker...")
    os.system("docker load -i /tmp/keploy-image.tar 2>&1")
    print("Done!")
    os.system("docker images | grep keploy")
else:
    print("\nSome layers incomplete. Cannot create image.")
