#!/bin/bash
set -e

IMAGE="keploy/keploy"
TAG="latest"
REGISTRY="ghcr.io"
OUTDIR="/tmp/keploy-image"
rm -rf $OUTDIR
mkdir -p $OUTDIR

echo "[1/5] Getting auth token..."
TOKEN=$(curl -s "https://${REGISTRY}/token?scope=repository:${IMAGE}:pull&service=${REGISTRY}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
if [ -z "$TOKEN" ]; then
    TOKEN=$(curl -s "https://ghcr.io/token?scope=repository:${IMAGE}:pull" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "FAIL")
fi
echo "Token: ${TOKEN:0:30}..."

echo "[2/5] Getting index manifest..."
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.oci.image.index.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v2+json" \
  "https://${REGISTRY}/v2/${IMAGE}/manifests/${TAG}" > $OUTDIR/index.json

AMD64_DIGEST=$(python3 -c "
import json, sys
idx = json.load(open('$OUTDIR/index.json'))
if 'manifests' in idx:
    for m in idx['manifests']:
        p = m.get('platform', {})
        if p.get('architecture') == 'amd64' and p.get('os') == 'linux':
            print(m['digest'])
            break
else:
    print('SINGLE')
" 2>/dev/null)

if [ "$AMD64_DIGEST" = "SINGLE" ]; then
    echo "Single manifest, using index as manifest"
    cp $OUTDIR/index.json $OUTDIR/manifest.json
else
    echo "AMD64 digest: $AMD64_DIGEST"
    echo "[2b/5] Getting amd64 manifest..."
    curl -s -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json" \
      "https://${REGISTRY}/v2/${IMAGE}/manifests/${AMD64_DIGEST}" > $OUTDIR/manifest.json
fi

echo "[3/5] Parsing layers..."
python3 << 'PYEOF'
import json, os
outdir = "/tmp/keploy-image"
m = json.load(open(os.path.join(outdir, "manifest.json")))
config = m.get("config", {}).get("digest", "")
layers = [l["digest"] for l in m.get("layers", [])]
sizes = [l.get("size", 0) for l in m.get("layers", [])]
total = sum(sizes)
print(f"Config: {config}")
print(f"Layers: {len(layers)}")
for i, (d, s) in enumerate(zip(layers, sizes)):
    print(f"  Layer {i}: {d} ({s/1024/1024:.1f} MB)")
print(f"Total: {total/1024/1024:.1f} MB")
with open(os.path.join(outdir, "config_digest"), "w") as f:
    f.write(config)
with open(os.path.join(outdir, "layer_digests"), "w") as f:
    for d in layers:
        f.write(d + "\n")
PYEOF

echo "[4/5] Downloading config + layers..."
CONFIG=$(cat $OUTDIR/config_digest)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://${REGISTRY}/v2/${IMAGE}/blobs/${CONFIG}" > $OUTDIR/config.json
echo "Config downloaded"

i=0
while IFS= read -r digest; do
    echo "Downloading layer $i: ${digest:0:20}..."
    curl -sL -H "Authorization: Bearer $TOKEN" \
      --connect-timeout 30 --max-time 600 \
      "https://${REGISTRY}/v2/${IMAGE}/blobs/${digest}" > "$OUTDIR/layer_${i}.tar.gz"
    SIZE=$(stat -c%s "$OUTDIR/layer_${i}.tar.gz" 2>/dev/null || echo 0)
    echo "  Layer $i: ${SIZE} bytes"
    i=$((i+1))
done < $OUTDIR/layer_digests

echo "[5/5] Creating Docker image tarball..."
python3 << 'PYEOF2'
import json, os
outdir = "/tmp/keploy-image"
manifest = json.load(open(os.path.join(outdir, "manifest.json")))
layers = [l["digest"] for l in manifest["layers"]]
layer_files = [f"layer_{i}.tar.gz" for i in range(len(layers))]
docker_manifest = [{
    "Config": "config.json",
    "RepoTags": ["ghcr.io/keploy/keploy:latest"],
    "Layers": layer_files,
}]
with open(os.path.join(outdir, "docker_manifest.json"), "w") as f:
    json.dump(docker_manifest, f)
config_digest = open(os.path.join(outdir, "config_digest")).read().strip()
print(f"Docker manifest created with {len(layer_files)} layers")
PYEOF2

cp $OUTDIR/docker_manifest.json $OUTDIR/manifest.json
echo '{"ghcr.io/keploy/keploy":{"latest":"'"$(cat $OUTDIR/config_digest | cut -d: -f2)"'"}}' > $OUTDIR/repositories

echo "Creating tarball..."
cd $OUTDIR && tar cf /tmp/keploy-image.tar config.json repositories manifest.json layer_*.tar.gz
echo "Tarball created: $(du -h /tmp/keploy-image.tar | cut -f1)"

echo "Loading into Docker..."
docker load -i /tmp/keploy-image.tar 2>&1
echo "Done!"
docker images | grep keploy
