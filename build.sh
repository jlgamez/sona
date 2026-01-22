#!/usr/bin/env bash
set -e
# load env variables from file
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
fi

# =========================
#  Build frozen Python app
# =========================

# 1. Activate virtualenv (adjust path if needed)
echo "🐍 Activating virtualenv..."
source .venv/bin/activate

# 2. Clean previous builds
echo "🧹 Cleaning old build/dist folders..."
rm -rf build/ dist/ *.spec

# 3. PyInstaller command (without codesign - we'll sign manually after)
echo "📦 Running PyInstaller..."
pyinstaller \
    --noconsole \
    --add-binary "./ffmpeg:." \
    --collect-all whisper \
    --name "Sona" \
    run.py

FFMPEG_PATH=$(find ./dist/Sona -name "ffmpeg" | head -n 1)
if [ -z "$FFMPEG_PATH" ]; then
    echo "❌ ERROR: ffmpeg was not found anywhere in ./dist/run"
    echo "Contents of ./dist/Sona:"
    ls ./dist/Sona
    exit 1
else
    echo "🎯 Found ffmpeg at: $FFMPEG_PATH"
fi

# 4. Code signing (ad-hoc for local use, no Apple Developer cert required)
echo "🔏 Ad-hoc signing main executable..."
codesign --force --sign - ./dist/Sona/Sona

echo "🔏 Ad-hoc signing bundled ffmpeg..."
codesign --force --sign - "$FFMPEG_PATH"
chmod +x "$FFMPEG_PATH"

# 5. Verify
echo "✅ Build finished!"
echo "📁 Executable location: ./dist/Sona"

echo "🎉 Done ✅"
