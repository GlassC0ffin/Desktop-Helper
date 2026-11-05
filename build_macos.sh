#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if [ "$(uname -s)" != "Darwin" ]; then
    echo "Build this macOS app on a Mac." >&2
    exit 1
fi

PYTHON=${PYTHON:-python3}
VENV_DIR="$PROJECT_DIR/.venv-build"
ICONSET_DIR="$PROJECT_DIR/build/macos/DesktopFox.iconset"
ICON_PATH="$PROJECT_DIR/build/macos/DesktopFox.icns"
OLLAMA_RESOURCES=${OLLAMA_RESOURCES:-/Applications/Ollama.app/Contents/Resources}

if [ ! -x "$OLLAMA_RESOURCES/ollama" ]; then
    echo "Install the official Ollama macOS app before building Desktop Fox." >&2
    echo "Expected Ollama runtime at: $OLLAMA_RESOURCES/ollama" >&2
    exit 1
fi

for license_file in \
    "$PROJECT_DIR/licenses/LLAMA3.2_LICENSE.txt" \
    "$PROJECT_DIR/licenses/LLAMA3.2_NOTICE.txt" \
    "$PROJECT_DIR/licenses/OLLAMA_MIT_LICENSE.txt"
do
    if [ ! -f "$license_file" ]; then
        echo "Missing required third-party license: $license_file" >&2
        echo "Run ./prepare_model_archive.sh first." >&2
        exit 1
    fi
done

if [ ! -x "$VENV_DIR/bin/python" ]; then
    "$PYTHON" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements-desktop.txt

mkdir -p "$ICONSET_DIR" "$PROJECT_DIR/dist"
for size in 16 32 64 128 256 512; do
    sips -z "$size" "$size" assets/chibi_fox.png \
        --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
done
for size in 16 32 64 128 256; do
    doubled=$((size * 2))
    sips -z "$doubled" "$doubled" assets/chibi_fox.png \
        --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET_DIR" -o "$ICON_PATH"

"$VENV_DIR/bin/python" -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --onedir \
    --name DesktopFox \
    --icon "$ICON_PATH" \
    --osx-bundle-identifier com.desktophelper.desktopfox \
    --add-data "$PROJECT_DIR/assets/chibi_fox.png:assets" \
    --add-data "$OLLAMA_RESOURCES:ollama_runtime" \
    --add-data "$PROJECT_DIR/licenses:licenses" \
    --specpath "$PROJECT_DIR/build/macos" \
    --workpath "$PROJECT_DIR/build/macos/pyinstaller" \
    --distpath "$PROJECT_DIR/dist" \
    desktop_pet.py

chmod +x "$PROJECT_DIR/dist/DesktopFox.app/Contents/Resources/ollama_runtime/ollama"
"$VENV_DIR/bin/python" - "$OLLAMA_RESOURCES" \
    "$PROJECT_DIR/dist/DesktopFox.app/Contents/Resources/ollama_runtime" <<'PY'
import os
import sys

source_root, bundle_root = sys.argv[1:]
for current, _, filenames in os.walk(source_root):
    for filename in filenames:
        source = os.path.join(current, filename)
        if os.stat(source).st_mode & 0o111:
            relative = os.path.relpath(source, source_root)
            bundled = os.path.join(bundle_root, relative)
            os.chmod(bundled, os.stat(bundled).st_mode | 0o111)
PY

ditto -c -k --sequesterRsrc --keepParent \
    "$PROJECT_DIR/dist/DesktopFox.app" \
    "$PROJECT_DIR/dist/DesktopFox-macOS.zip"

echo "App built: $PROJECT_DIR/dist/DesktopFox.app"
echo "Shareable archive: $PROJECT_DIR/dist/DesktopFox-macOS.zip"
