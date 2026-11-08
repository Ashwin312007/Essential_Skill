# Project Handbook

> Replace the bracketed prompts with this project's details. Keep this file concise; put detailed guidance in `.claude/rules/`.

## Project
- **Purpose:** [What this project does]
- **Primary users:** [Who uses it]
- **Current status:** [Prototype / production / maintenance]

## Architecture
- **Stack and versions:** [Languages, frameworks, runtime versions]
- **Entry points:** [Main executable, application entry, launch files]
- **Key directories:** [Short directory map]
- **Data flow:** [How the main components communicate]

## Working rules
1. Inspect the repository and its existing conventions before proposing changes.
2. Research the official documentation for the detected stack; use `python scripts/doc_manager.py sources` to build the reading list.
3. Present a plan before modifying files. Include the objective, findings, complexity, model tier, files to touch, and measurable success criteria.
4. Wait for explicit user approval before edits or side effects. Ask when requirements are unclear; do not guess.
5. Make the smallest change that solves the requested problem. Do not refactor unrelated code or add dependencies without approval.
6. Protect secrets. Never print, commit, or log `.env` values, credentials, keys, or private tokens.
7. Verify changes with the relevant tests, build, lint, or validation commands. Report the exact checks and outcomes.
8. Review the final diff for scope, correctness, and accidental changes before committing.

## Commands
- **Install/setup:** [Command]
- **Run:** [Command]
- **Test:** [Command]
- **Lint/format:** [Command]
- **Build/package:** [Command]

## Constraints
- **Compatibility targets:** [Operating systems, hardware, language/runtime versions]
- **Performance or resource limits:** [If applicable]
- **Safety/security requirements:** [If applicable]
- **Files or paths requiring extra approval:** [List; also configure `protected_paths`]

## Completion criteria
A task is complete only when the requested behavior is implemented, relevant checks pass, no unrelated files are changed, and the final response summarizes the changes and verification results.

## Skill harness
At session start, run:

```bash
python scripts/doc_manager.py validate
python scripts/doc_manager.py context
```

Before a non-routine shell command or file edit, run the permission check:

```bash
python scripts/doc_manager.py check --tool Bash --input "[command]"
python scripts/doc_manager.py check --tool Edit --input "[relative/path]"
```

Treat exit code `0` as allow, `1` as ask (get user approval), `2` as deny, and `3` as a configuration error. Run configured hooks after the corresponding actions.
