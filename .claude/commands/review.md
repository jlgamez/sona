# Code Review

Review the specified code against Sona's engineering standards.

If no specific file is given, review the current `git diff` (unstaged changes).

Evaluate against this checklist:

1. **Separation of Concerns:** Is IO-bound / CPU-bound / OS-bound logic properly decoupled?
2. **Thread Safety:** Does this block the main thread or hotkey listener? Are shared resources guarded with locks?
3. **Lazy Loading:** Are heavy imports (whisper, torch) deferred? Are singletons used where appropriate?
4. **Error Handling:** Does this handle macOS permission errors (TCC) gracefully? Are subprocesses cleaned up?
5. **Path Handling:** Is `pathlib.Path` used exclusively? No hardcoded separators?
6. **Type Hints:** Are all function signatures typed?
7. **Protocol Conformance:** Do implementations match their Protocol interface?
8. **Resource Cleanup:** Are temp files, audio buffers, and subprocesses cleaned up?
9. **DRY:** Is there duplication that should be extracted?
10. **Simplicity:** Can a junior developer understand the flow without a long explanation?

Output format:
- List issues found with severity (Nitpick / Suggestion / Important / Critical)
- For each issue: specific file and line, what is wrong, and how to fix it
- End with a summary: **Approve** / **Approve with suggestions** / **Request changes**

$ARGUMENTS
