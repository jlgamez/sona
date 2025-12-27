This `context.md` file is designed to give GitHub Copilot a comprehensive understanding of your tech stack, your specific MVP goals, and the constraints of working on macOS while targeting cross-platform compatibility.

Place this file in your project root to improve the relevance of Copilot's suggestions.

---

# Project Context: Whisper-based Speech-to-Text Utility

## 1. Project Overview

This project is a high-performance, cross-platform desktop utility that allows users to record audio via a **global hotkey**, transcribe the speech using **OpenAI Whisper**, and automatically **paste** the resulting text into the active application.

### MVP Core Workflow

1. **Trigger:** User presses and holds a specific hotkey (e.g., `Cmd+Shift+R`).
2. **Record:** System captures microphone input using `ffmpeg` for as long as the key is held.
3. **Process:** The audio file is passed to `openai-whisper` for local transcription.
4. **Output:** The transcribed string is injected into the user's current cursor position (simulating a "Paste" command).

---

## 2. Technical Stack

* **Language:** Python 3.10+
* **Environment:** Virtual Environment (`venv`)
* **IDE:** PyCharm
* **Audio Engine:** `ffmpeg` (external executable)
* **Transcription:** `openai-whisper` (running locally)
* **OS Target:** macOS (Development), Windows/Linux (Deployment)

---

## 3. Implementation Details & Constraints

### Audio Handling

* Use `subprocess` to interface with the `ffmpeg` executable for capturing audio.
* Default format should be `.wav` or `.mp3` for Whisper compatibility.
* **macOS Specifics:** Ensure the app handles Permissions (Microphone & Accessibility) gracefully.

### Hotkey Management

* The listener must be **non-blocking** and global (active even when the app is in the background).
* Library preference: `pynput` or `keyboard` (Note: `keyboard` requires root on some OSs; `pynput` is generally preferred for cross-platform GUI-less apps).

### Transcription (Whisper)

* Load the model once on startup (preferably the `base` or `small` model for MVP speed).
* Use GPU acceleration (MPS on macOS/Silicon, CUDA on Windows) if available.

### Text Injection

* The output should be placed in the clipboard and then a "Paste" command (`Cmd+V` or `Ctrl+V`) should be simulated to ensure compatibility across different text fields.

