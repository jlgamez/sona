# Sona

Sona is a small, audio capture and transcription helper. It records short audio snippets via FFmpeg, transcribes them with OpenAI Whisper, and lets you trigger everything via global hotkeys.

> **Note:** Sona is currently developed and tested only on **macOS**. Support for Windows and Linux is a work in progress.

The code is structured to keep concerns separate:
- **Audio**: recording and loading audio files.
- **Transcription**: loading and running Whisper in the background.
- **Hotkeys**: global keyboard listeners to start/stop recording and handle results.

## Features

- Global hotkeys to start and stop recording.
- Recording via the FFmpeg CLI (no OS-specific audio code in Python).
- Background Whisper transcription using a lazily-loaded singleton model.
- Simple cleanup of temporary audio files after transcription.
- Designed to be mostly cross-platform (macOS, Windows, Linux), with a focus on macOS.


## Setup

Python 3.11+ is recommended.

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux (bash)
   # .venv\Scripts\activate   # Windows PowerShell / cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **FFmpeg setup:**

   Sona requires FFmpeg to be available for audio recording. You have two options:

   - **Option 1: Download the FFmpeg binary**
     - Place the FFmpeg binary in the `ffmpeg/` directory at the project root (recommended for reproducibility).

   - **Option 2: Use a system-wide FFmpeg installation**
     - Install FFmpeg using your package manager (e.g., Homebrew on macOS: `brew install ffmpeg`).
     - Set the environment variable `IMAGEIO_FFMPEG_EXE` to the full path of the FFmpeg binary:
       ```bash
       export IMAGEIO_FFMPEG_EXE=/usr/local/bin/ffmpeg  # or wherever ffmpeg is installed
       ```
     - Ensure your `PATH` environment variable includes the directory containing the FFmpeg binary:
       ```bash
       export PATH="/usr/local/bin:$PATH"
       ```

   The app will attempt to use the bundled binary first, then fall back to the system FFmpeg if available and properly configured.

## Running Sona

From the project root:

```bash
source .venv/bin/activate  # if not already active
python run.py
```

On first run, Whisper will download the selected model (default is `base`, see `model_adapter.py`). This may take some time and use network/bandwidth.

Once running:

- A background hotkey listener is started using `pynput`.
- Press the configured start-recording hotkey (check `hotkey_actions.py` / `hotkey_controller_impl.py` for the exact combination).
- Speak, then press the stop-recording hotkey.
- The audio will be saved **temporarily** to `src/audio/resources/temp_audio/`, transcribed in the background, and the result will be **automatically pasted** wherever the user has the cursor.
- The transcription is also saved in the user's clipboard.

## macOS Permissions

On macOS, global hotkeys and audio capture may require extra permissions:

- **Accessibility / Input Monitoring**: required for `pynput` to capture global keyboard events.
- **Microphone**: required for your OS-level audio input, which FFmpeg uses.

If hotkeys do not work, open **System Settings ▸ Privacy & Security** and ensure your terminal/IDE has the necessary permissions. The app is designed to log permission errors rather than crash, but it cannot bypass macOS security dialogs.

## Customization

### Changing Hotkeys

To change the hotkeys for recording edit `src/controllers/hot_key/hotkey_controller_impl.py` (handles hotkey registration)

### Changing the Whisper Model

To use a different Whisper model (e.g., `base`, `small`, `medium`, `large`), edit the model name in:
- `src/controllers/transcription/model_adapter.py`

Look for the line that sets the model name (e.g., `MODEL_NAME = "base"`) and change it to your [preferred model](https://github.com/openai/whisper#:~:text=Available%20models%20and%20languages). The new model will be downloaded on first use if not already cached.
### Deleting a Whisper Model
In MacOs Whisper models are cached locally.
- to delete them all manually run `rm -rf ~/.cache/whisper` in Terminal.
- If you only want to delete a specific model: `ls ~/.cache/whisper` to see the models hosteed locally. 


## Troubleshooting

- **Whisper model download is slow**: This is normal on first run. Subsequent runs reuse cached models.
- **Hotkeys do not fire**:
  - Confirm the process is running and `pynput` installed.
  - On macOS, check Accessibility/Input Monitoring permissions for your terminal/IDE.
- **FFmpeg not found**:
  - Ensure `ffmpeg` is installed (`brew install ffmpeg` on macOS), or
  - Place a binary in the `ffmpeg/` directory.

## Architecture Notes

Sona follows a few key architectural principles:

- **Separation of Concerns**
  - IO-bound: FFmpeg recording and file IO are isolated in `src/audio/` and run via `subprocess`.
  - CPU/GPU-bound: Whisper inference is isolated in `src/controllers/transcription/model_adapter.py` and related orchestrator modules.
  
- **Lazy Loading & Singletons**
  - The Whisper model is not loaded at startup. `ModelAdapterImpl` lazily loads the model in a background-friendly way and caches it as a singleton to avoid repeated allocations.

- **Event-Driven Flow**
  - Hotkey events trigger recording start/stop callbacks.
  - Recording completion triggers a background transcription job.
  - Transcription completion triggers result handling and cleanup.

- **Resource Management**
  - Temporary audio files are written under `src/audio/resources/temp_audio/`.
  - Cleanup services are used to remove temporary files after transcription.
  - FFmpeg `subprocess` instances are tracked and terminated using `atexit` handlers.

