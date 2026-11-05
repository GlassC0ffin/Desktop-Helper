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
    --specpath "$PROJECT_DIR/build/macos" \
    --workpath "$PROJECT_DIR/build/macos/pyinstaller" \
    --distpath "$PROJECT_DIR/dist" \
    desktop_pet.py

ditto -c -k --sequesterRsrc --keepParent \
    "$PROJECT_DIR/dist/DesktopFox.app" \
    "$PROJECT_DIR/dist/DesktopFox-macOS.zip"

echo "App built: $PROJECT_DIR/dist/DesktopFox.app"
echo "Shareable archive: $PROJECT_DIR/dist/DesktopFox-macOS.zip"
