# Custom Commit

Create a git commit following Sona's commit format.

Review the staged changes with `git diff --cached`. If nothing is staged, review `git diff` and stage the appropriate files.

Write a commit message in this exact format:

```
type(scope): description
```

Where:
- **type**: feat, fix, refactor, perf, docs, style, test, or chore
- **scope**: the module being changed (e.g., transcription, hotkey, audio, config, build, server)
- **description**: max 50 characters, imperative mood, no period

Then add a body:

```
<General title of the change>
- 🚀 Functional Change: <what the user or system experiences now>
- ⚙️ Technical Change: <how the code was changed>
- ⚠️ Criticality: <Low|Medium|High|CRITICAL> - <brief justification>
```

Rules:
- Atomic commits: one logical change per commit
- If there are multiple logical changes, make multiple commits
- Keep bullet text concise
- If it is a pure refactor with no user-visible change, say "No functional change (refactor/internal)" for the Functional Change bullet

$ARGUMENTS
