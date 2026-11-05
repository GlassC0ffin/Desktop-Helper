#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if [ "$(uname -s)" != "Darwin" ]; then
    echo "Prepare the model archive on a Mac with Ollama installed." >&2
    exit 1
fi

PYTHON=${PYTHON:-python3}
OLLAMA=${OLLAMA:-/Applications/Ollama.app/Contents/Resources/ollama}
MODEL_STORE=${OLLAMA_MODELS:-"$HOME/.ollama/models"}
MANIFEST="$MODEL_STORE/manifests/registry.ollama.ai/library/llama3.2/latest"
MODEL_ARCHIVE="$PROJECT_DIR/dist/DesktopFox-llama3.2-model.tar"

if [ ! -x "$OLLAMA" ]; then
    echo "Ollama not found at $OLLAMA. Install Ollama for macOS first." >&2
    exit 1
fi

if [ ! -f "$MANIFEST" ]; then
    echo "llama3.2 was not found in $MODEL_STORE." >&2
    echo "Run: ollama pull llama3.2" >&2
    exit 1
fi

if [ "$(basename "$MODEL_STORE")" != "models" ]; then
    echo "OLLAMA_MODELS must point to a directory named 'models'." >&2
    echo "Current model directory: $MODEL_STORE" >&2
    exit 1
fi

mkdir -p "$PROJECT_DIR/licenses" "$PROJECT_DIR/dist"
"$OLLAMA" show llama3.2 --license > "$PROJECT_DIR/licenses/LLAMA3.2_LICENSE.txt"

"$PYTHON" - "$MANIFEST" "$MODEL_STORE" <<'PY'
import json
import os
import sys

manifest_path, model_store = sys.argv[1:]
with open(manifest_path, encoding="utf-8") as manifest_file:
    manifest = json.load(manifest_file)

models = [
    layer
    for layer in manifest["layers"]
    if layer.get("mediaType") == "application/vnd.ollama.image.model"
]
if not models:
    raise SystemExit("The llama3.2 manifest does not contain a model layer.")

for layer in models:
    digest = layer["digest"].removeprefix("sha256:")
    blob = os.path.join(model_store, "blobs", f"sha256-{digest}")
    if not os.path.isfile(blob) or os.path.getsize(blob) != layer["size"]:
        raise SystemExit(f"The model blob is missing or has the wrong size: {blob}")
PY

rm -f "$MODEL_ARCHIVE"
tar -cf "$MODEL_ARCHIVE" \
    --exclude=models/manifests-v2 \
    -C "$(dirname "$MODEL_STORE")" \
    models

archive_size=$(/usr/bin/stat -f '%z' "$MODEL_ARCHIVE")
github_asset_limit=2147483648
if [ "$archive_size" -ge "$github_asset_limit" ]; then
    echo "Model archive exceeds GitHub's 2 GiB per-asset limit." >&2
    rm -f "$MODEL_ARCHIVE"
    exit 1
fi

echo "Model archive: $MODEL_ARCHIVE"
echo "Size: $archive_size bytes"
shasum -a 256 "$MODEL_ARCHIVE"
