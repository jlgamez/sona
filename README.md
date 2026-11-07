# Sona

Push-to-talk speech-to-text for macOS. Hold a hotkey, speak, release: the audio is transcribed locally with OpenAI Whisper and pasted at your cursor. This repo is the backend (hotkeys, recording, transcription, and a Flask config API for a separate UI).

> Developed and tested on **macOS** only.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**FFmpeg:** place the binary at `./ffmpeg` in the project root (gitignored).

## Run

```bash
source .venv/bin/activate
python run.py
```

This starts the hotkey listener and the Flask API server on `127.0.0.1:5000`. Change the port with `--port 5055` or `SONA_PORT`. Allowed UI origins are set with `SONA_ALLOWED_ORIGINS` (comma-separated, default: Vite dev server and Electron). The selected Whisper model downloads on first use to `~/.cache/whisper/`.

Hold the hotkey (default: Left Control) to record, release to transcribe. The text is pasted at the cursor and, depending on settings, kept in the clipboard.

## macOS Permissions

Grant your terminal/IDE (or the packaged app) in **System Settings > Privacy & Security**:

- **Accessibility** and **Input Monitoring**: global hotkeys and paste
- **Microphone**: recording

## Configuration

Settings live in `~/.sona/user_config.json` and are edited through the API: hotkey, microphone, Whisper model, and clipboard behaviour (auto-paste, keep output in clipboard). Saving a config reloads the runtime automatically.

API (`/api/...`): `user-config` (GET/POST), `models`, `hot-keys`, `audio-devices`, `download-model`, `model-download-state`, `delete-model`.

## Troubleshooting

- **Hotkey does nothing:** check Accessibility / Input Monitoring permissions.
- **No audio or wrong mic:** pick a microphone via the `mic_device` config field (`GET /api/audio-devices` lists the names). Unset uses the system default.
- **FFmpeg not found:** make sure `./ffmpeg` exists and is executable.
- **Slow first run:** the Whisper model is downloading.
- **Remove cached models:** `rm -rf ~/.cache/whisper`

## Structure

`src/audio` (recording), `src/core` (hotkeys, transcription), `src/runtime` (lifecycle), `src/server` (Flask API), `src/event_management` (pub/sub), `src/utils`. See `CLAUDE.md` for details.
