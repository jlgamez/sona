#!/usr/bin/env bash
# Build a minimal, LGPL, arm64 FFmpeg for Sona and place it at ./ffmpeg.
#
# Why: ./ffmpeg is gitignored, so this script is the recipe for producing it.
# Only what Sona needs is compiled in: AVFoundation mic capture, WAV / raw
# s16le PCM in and out, resampling. No external libraries, no GPL code.
#
# Usage: scripts/build_ffmpeg.sh
# Needs: Xcode command line tools (clang, make), curl, shasum.

set -euo pipefail

FFMPEG_VERSION="7.1.1"
FFMPEG_SHA256="733984395e0dbbe5c046abda2dc49a5544e7e0e1e2366bba849222ae9e3a03b1"
TARBALL="ffmpeg-${FFMPEG_VERSION}.tar.xz"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

if [[ "$(uname -m)" != "arm64" ]]; then
  echo "This script builds an arm64 binary and must run on an Apple Silicon Mac." >&2
  exit 1
fi

cd "${WORK_DIR}"
curl -fsSLO "https://ffmpeg.org/releases/${TARBALL}"
echo "${FFMPEG_SHA256}  ${TARBALL}" | shasum -a 256 -c -
tar xf "${TARBALL}"
cd "ffmpeg-${FFMPEG_VERSION}"

./configure \
  --arch=arm64 \
  --cc=clang \
  --disable-everything \
  --disable-autodetect \
  --disable-doc \
  --disable-ffplay \
  --disable-ffprobe \
  --enable-ffmpeg \
  --enable-avdevice \
  --enable-avfoundation \
  --enable-indev=avfoundation \
  --enable-demuxer=wav,pcm_s16le \
  --enable-muxer=wav,pcm_s16le \
  --enable-decoder=pcm_s16le,pcm_f32le,pcm_s32le \
  --enable-encoder=pcm_s16le \
  --enable-protocol=file,pipe \
  --enable-filter=aresample,aformat,anull \
  --extra-ldflags="-framework AVFoundation -framework CoreMedia -framework CoreAudio -framework CoreFoundation -framework Foundation"

make -j"$(sysctl -n hw.ncpu)"

cp ffmpeg "${REPO_ROOT}/ffmpeg"
chmod +x "${REPO_ROOT}/ffmpeg"

file "${REPO_ROOT}/ffmpeg"
"${REPO_ROOT}/ffmpeg" -version | head -1
