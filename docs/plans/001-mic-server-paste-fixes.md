# Plan 001: Mic selection, server hardening, paste timing

Status: done (1. mic selection, 2. server hardening, 3. paste timing)

## Goal

Fix the three biggest issues found in the backend review so the UI and Electron packaging can build on a stable base.

## 1. Hardcoded microphone (done)

**Problem:** `AudioRecorderImpl._build_input_args` uses `-i ":1"` on macOS. This picks the wrong device, or fails, on any machine where the mic is not index 1.

**Approach:**
1. Add a device listing helper that parses `ffmpeg -f avfoundation -list_devices true -i ""` (output is on stderr) into audio devices with an index and a name.
2. Add an optional `mic_device` field to `UserConfig` and to `parse_submitted_config`. Default to the system default device when unset.
3. Pass the selected device from `AppServices` to `AudioRecorderImpl`. Reload through the existing `CONFIG_SAVED` event.
4. Add `GET /api/audio-devices` for the UI.
5. Fall back to the default device, and log a clear message, if the saved device no longer exists.

**Done when:** the mic is chosen from the UI, survives restarts, and a missing device does not break recording.

## 2. Server hardening (done)

**Problem:** `flask_app.run(debug=True)` exposes the Werkzeug debugger, CORS allows any origin, and the port is not controlled by the caller.

**Approach:**
1. Set `debug=False`.
2. Bind to `127.0.0.1` only.
3. Read host and port from CLI args or environment variables, so Electron can choose the port.
4. Restrict CORS to the origins the UI actually uses (dev server and the Electron app). Confirm the exact origins when the UI repo is available.
5. Optional: require a per-launch token that Electron passes in and the UI sends as a header.
6. Review error responses so they do not leak exception details unnecessarily.

**Done when:** the server runs without debug mode, listens on localhost on a configurable port, and rejects requests from unlisted origins.

## 3. Paste timing (done)

**Problem:** `TranscriptionResultHandlerImpl` fires Cmd+V immediately after writing the clipboard. When `keep_output_in_clipboard` is off, it then restores the old clipboard right away. The target app can read the clipboard after the restore and paste the wrong content.

**Approach:**
1. Add a short delay between the clipboard write and the Cmd+V keystroke.
2. Add a longer delay between the paste and the clipboard restore.
3. Make both delays named constants so they are easy to tune.
4. Release the keys in reverse order of pressing.

**Done when:** pasting works reliably in several apps (browser, editor, terminal) with `keep_output_in_clipboard` both on and off.

## Order of work

1. Server hardening (small, no dependencies).
2. Paste timing (small, isolated).
3. Mic selection (touches config, recorder and API).

## Related small fixes to do alongside

- Apply `fix_for_first_attempt_transcription_failure.patch` (None audio path when a recording is too short).
- Fix `ModelDownloadManager.is_downloading` raising before the first download.
- Check that `GET /api/user-config` serializes the config dataclass, and remove or implement the unused `PUT` method.

## Out of scope

Tests, logging, custom hotkeys, non-macOS support.
