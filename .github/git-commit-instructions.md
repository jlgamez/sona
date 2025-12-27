# Git Commit Instructions

You are an expert developer tasked with creating high-quality, scannable, and descriptive git commits. Every commit must follow this specific structure to ensure both human readability and machine-friendly history.

---
## 1. Commit Structure
Each commit message must consist of a **Header**, a **Body**, and an optional **Footer**.

```text

<General title of commit>
- 🚀 Functional Change: <What the user or system experiences now>
- ⚙️ Technical Change: <High-level code/logic change details>
- ⚠️ Criticality: <Low | Medium | High | CRITICAL> - <Brief justification>
```

---

## 2. Component Guidelines

### A. The Header (Line 1)

* **Format**: `type(scope): description`
* **Type**: Use standard prefixes: `feat`, `fix`, `refactor`, `perf`, `docs`, `style`, `test`, `chore`.
* **Scope**: The specific module or file being changed (e.g., `whisper`, `hotkey`, `ui`).
* **Description**: Max 50 characters, imperative mood ("Add feature" not "Added feature"), no period at the end.

### B. The Body (Bullet Points)

Every bullet must start with a **Relevant Emoji** and **Bold Title**.

1. **Functional Change** 🚀: Describe the impact on the application's behavior. If it’s an internal refactor with no visible change, state "No functional change (refactor/internal)."
2. **Technical Change** ⚙️: Detail *how* the code was altered (e.g., "Switched from official Whisper to faster-whisper for CTranslate2 support").
3. **Criticality** ⚠️: Define the risk or importance:
* **Low**: Cosmetic, docs, or non-breaking minor tweaks.
* **Medium**: New features or bug fixes that don't affect core stability.
* **High**: Changes to core logic, performance-heavy updates.
* **CRITICAL**: Security fixes, breaking API changes, or crash resolutions.



---

## 3. Best Practices

* **Atomic Commits**: One commit per logical change. If you fixed a bug AND added a feature, make TWO commits.
* **Imperative Voice**: Always write the header as if you are giving a command.
* **No "How" in Header**: The header is for "What." The Technical Change bullet is for "How."
* **Context over Content**: Don't just say "Updated main.py." Say *why* it was updated.

---

## 4. Example Commit Message

```text
feat(transcription): implement faster-whisper engine

Transcription time optimisation
- 🚀 Functional Change: Drastically reduced transcription wait time for the user.
- ⚙️ Technical Change: Replaced openai-whisper with faster-whisper using CTranslate2 and float16 quantization.
- ⚠️ Criticality: High - Fundamental change to the transcription pipeline; improves UX significantly.

```