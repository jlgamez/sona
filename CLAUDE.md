# CLAUDE.md

## Overview

**Sona** is the backend of a macOS push-to-talk speech-to-text app. Hold a global hotkey, audio is recorded via FFmpeg, transcribed locally with OpenAI Whisper, and pasted at the cursor. A Flask API (consumed by a separate UI repo, to be packaged with Electron) manages config, hotkeys and models.

## Quick Reference

- **Run:** `source .venv/bin/activate && python run.py` (`run.py` contains `bootstrap()`, the composition root)
- **Install:** `pip install -r requirements.txt` (Python 3.11+)
- **Build:** PyInstaller via `Sona.spec` (gitignored via `*.spec`)
- **User config:** `~/.sona/user_config.json`; Whisper models: `~/.cache/whisper/`
- **Tests:** none yet. Use pytest in `tests/`, mirror `src/`, mock pynput / subprocess / whisper

## Module Map

| Module | Responsibility |
|--------|---------------|
| `src/audio/` | FFmpeg recording (`AudioRecorderImpl`), audio validation |
| `src/core/hot_key/` | pynput global listener, press/release actions |
| `src/core/transcription/` | Whisper adapter (`AITranscriberImpl`), background orchestrator, result handler (clipboard + paste), cleanup, `device/` (MPS/CUDA/CPU) |
| `src/runtime/` | `AudioTranscriptionRuntimeManager`: start/stop/reload of hotkey + transcriber |
| `src/event_management/` | Singleton `EventMessenger` pub/sub + `Event` enum |
| `src/server/` | Flask app (`app.py`) and `config/`, `hot_key/`, `models/` (entity / repository / service / factory layers) |
| `src/utils/` | `BundledFfmpeg` (root `./ffmpeg`), `clipboard` (pbcopy/pbpaste) |
| `src/AppServices.py` | Wires recorder, orchestrator, hotkey controller |

**Flow:** hotkey press -> record -> release -> orchestrator (shared thread pool) -> Whisper -> clipboard/paste -> temp file deleted. Saving config emits `CONFIG_SAVED`, which reloads the runtime.

**API** (`/api/...`): `user-config` (GET/POST), `models`, `hot-keys`, `audio-devices`, `download-model`, `model-download-state`, `delete-model`.

## Conventions

- `pathlib.Path` for paths; type hints on all signatures
- `typing.Protocol` for interfaces (not ABC); `*Impl` classes and `*Factory` classes
- Every class has a docstring with **Responsibility** and **Interface**
- PascalCase filename per primary class; snake_case for utility modules
- Imports use the full `src.` prefix; dataclasses for DTOs
- Whisper/torch imported lazily; shared model cached at class level; guard shared state with locks

## Commit Format

```
type(scope): description (max 50 chars, imperative)

<General title>
- Functional Change: <impact>
- Technical Change: <details>
- Criticality: <Low|Medium|High|CRITICAL> - <justification>
```

Types: `feat fix refactor perf docs style test chore`. Scopes: `transcription hotkey audio config build server dev`.

## Constraints and Known Gaps

- macOS only (clipboard, paste, avfoundation). Needs Accessibility, Input Monitoring and Microphone permissions
- Never commit `.env` or the `./ffmpeg` binary (both gitignored)
- Microphone is chosen by name via the `mic_device` config field (null = system default); a missing device falls back to the default
- Server binds to `127.0.0.1` only, debug off. Port: `--port` or `SONA_PORT` (default 5000). CORS origins: `SONA_ALLOWED_ORIGINS` (comma-separated; defaults to Vite dev and Electron `null`). No auth token
