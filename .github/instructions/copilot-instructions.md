# Engineering Standards: 10X Architecture & Best Practices

## 1. Core Architectural Principles

* **Separation of Concerns:** Keep the **IO-bound** (FFmpeg/Recording), **CPU/GPU-bound** (Whisper Inference), and **OS-bound** (Hotkey/Paste) logic strictly decoupled.
* **Process vs. Thread:** * Use `threading` for UI/Hotkey listening to maintain responsiveness.
* Use `subprocess` for FFmpeg to offload heavy encoding.
* Consider `multiprocessing` for transcription if the GIL (Global Interpreter Lock) impacts hotkey latency.


* **Event-Driven Design:** Use an internal event bus or simple callbacks to signal state changes (e.g., `on_record_start`, `on_transcription_complete`).

---

## 2. 10X Implementation Patterns

### Dependency Management

* **Lazy Loading:** Do not load the Whisper model at script startup. Load it in a background thread or upon the first request to ensure the "Cold Start" doesn't frustrate the user.
* **Singleton Pattern:** The Whisper Model and FFmpeg Controller should be singletons to prevent memory leaks and redundant resource allocation.

### Performance & Resource Optimization

* **Memory Management:** Explicitly clear audio buffers/temporary files immediately after transcription. Use `io.BytesIO` for small audio clips to avoid disk I/O overhead.
* **Whisper Acceleration:** * Auto-detect hardware: `device="mps"` for Apple Silicon, `device="cuda"` for Nvidia, `device="cpu"` as fallback.
* Use `fp16=True` on supported hardware to halve memory usage and double speed.



---

## 3. Robustness & Error Handling

* **Graceful Degradation:** If the hotkey fails or permissions are denied, the app must log the specific macOS error (e.g., `TCC` permissions) instead of crashing.
* **Subprocess Resilience:** Always use context managers (`with`) for file handling and ensure FFmpeg processes are explicitly killed on app exit using `atexit`.
* **Atomic Operations:** Write audio to temporary files with unique UUIDs to prevent collisions if the user triggers multiple recordings in rapid succession.

---

## 4. Cross-Platform "Code-Once" Strategy

* **Path Abstraction:** Use `pathlib.Path` exclusively. No hardcoded `/` or `\` strings.
* **Clipboard Strategy:** Abstract the "Paste" action.
* *macOS:* `pbcopy` / `pynput.keyboard`
* *Windows/Linux:* `pyperclip` / `keyboard`


* **Environment Agnosticism:** Use `shutil.which("ffmpeg")` to locate the executable rather than assuming a fixed path like `/usr/local/bin/ffmpeg`.

---

## 5. Clean Code Requirements

* **Type Hinting:** Use strict Python type hints (`callable`, `Optional`, `Union`) for all function signatures.
* **Documentation:** Every class must have a docstring explaining its **Responsibility** and its **Interface**.
* **Testing:** Write code that is "Testable by Design"—logic should be separable from the hardware (e.g., a function that transcribes a file path should be independent of the function that records the audio).

---

## 6. The "10X" Checklist

> Before suggesting code, ensure:
> 1. Is this the most performant way to handle the audio buffer?
> 2. Will this block the Main Thread (Hotkey listener)?
> 3. Does this handle the "Permission Denied" case on macOS?
> 4. Is the code "Dry"? (Don't Repeat Yourself).
