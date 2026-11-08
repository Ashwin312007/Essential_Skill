# Essential Skill

A toolkit for AI coding agents that combines structured task execution with reusable project-level guardrails.

This repository contains two complementary skills:

- **Essential_Skill** — defines the agent's operating workflow: plan first, obtain approval, discover relevant skills, select an execution model, verify changes, audit the result, and use a controlled Git workflow.
- **doc_manager_skill** — provides a portable Python CLI that gives coding agents a Claude Code-style project harness, including project instructions, skill discovery, permission checks, hooks, and validation.

## Repository contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Main Essential Skill instructions |
| `scripts/find_skills.py` | Cross-platform skill discovery utility |
| `doc_manager_skill/SKILL.md` | Portable project-harness skill instructions |
| `doc_manager_skill/README.md` | Detailed documentation for doc_manager_skill |
| `doc_manager_skill/scripts/doc_manager.py` | Standard-library Python CLI |
| `doc_manager_skill/assets/root_instructions_template.md` | Template for a project's `AGENTS.md` or `CLAUDE.md` |

## 1. Essential_Skill

Essential_Skill defines a structured workflow for AI-assisted engineering tasks.

### Core workflow

1. Inspect the project and understand the task.
2. Research relevant official documentation.
3. Prepare a scoped plan with goals and verification criteria.
4. Wait for explicit user approval before making changes.
5. Discover and activate relevant skills.
6. Select the execution approach based on task complexity.
7. Implement only the approved changes.
8. Run relevant tests and verify the result.
9. Review the diff and commit using Conventional Commits.
10. Push to the intended remote branch after checking repository state.

The skill also defines fallback behavior for unavailable tools, limits review passes, and protects against unrelated changes.

### Install

Clone the repository:

```bash
git clone https://github.com/Ashwin312007/Essential_Skill.git
```

Install the repository's Essential_Skill folder in the skills directory supported by your agent. For Gemini CLI, the documented user-level location is:

**Windows (PowerShell):**

```powershell
$dest = "$env:USERPROFILE\.gemini\config\skills\Essential_Skill"
New-Item -ItemType Directory -Force -Path $dest
Copy-Item .\Essential_Skill\* $dest -Recurse -Force
```

**Linux / macOS:**

```bash
mkdir -p "$HOME/.gemini/config/skills/Essential_Skill"
cp -R Essential_Skill/. "$HOME/.gemini/config/skills/Essential_Skill/"
```

Adjust the destination if your agent uses a different skill discovery directory.

### Run skill discovery

**Windows (PowerShell):**

```powershell
python "$env:USERPROFILE\.gemini\config\skills\Essential_Skill\scripts\find_skills.py" "C:\path\to\workspace"
```

**Linux / macOS:**

```bash
python "$HOME/.gemini/config/skills/Essential_Skill/scripts/find_skills.py" "/path/to/workspace"
```

Omit the workspace argument if you want the script to use its default behavior.

## 2. doc_manager_skill

doc_manager_skill is a portable project harness for AI coding agents and command-line tools. Its Python runtime uses only the standard library and supports Python 3.8+ on Windows, Linux, and macOS.

### Features

- **Project context:** gathers root instructions, scoped rules, commands, agent roles, and available skills.
- **Skill discovery:** detects project technologies and ranks matching skills.
- **Permission checks:** evaluates commands and file operations as `allow`, `ask`, or `deny`.
- **Hooks:** runs configured commands after supported events.
- **Model tiers:** maps low, medium, and high complexity to configured models.
- **Documentation research:** suggests official documentation sources for the detected stack.
- **Validation:** checks whether the project harness is configured correctly.

### Install

Copy the `doc_manager_skill` directory into your project's skills folder:

```bash
# Project-level installation
cp -r doc_manager_skill .claude/skills/

# Or user-level installation
cp -r doc_manager_skill ~/.claude/skills/
```

On Windows, copy the directory using File Explorer or PowerShell. The destination can also be any skill directory supported by your agent.

### Initialize and validate

Run these commands from the target project root:

```bash
python .claude/skills/doc_manager_skill/scripts/doc_manager.py init
python .claude/skills/doc_manager_skill/scripts/doc_manager.py validate
python .claude/skills/doc_manager_skill/scripts/doc_manager.py context
```

The `init` command creates missing project instruction and `.claude/` configuration files. It does not overwrite existing files.

Use `assets/root_instructions_template.md` as a starting point when writing the project's `AGENTS.md` or `CLAUDE.md`.

### Useful commands

Run the script from the project root, or pass `--workspace <path>` to target another directory.

| Command | Purpose |
|---|---|
| `init` | Create missing harness files and directories |
| `validate` | Validate the project harness |
| `context` | Print the instructions an agent should load |
| `discover` | Find and rank relevant installed skills |
| `sources` | List documentation sources for the detected stack |
| `check --tool <Tool> --input <Value>` | Check whether an action is allowed |
| `hook <Event> --tool <Tool> --input <Value>` | Run hooks for an event |
| `tier low|medium|high` | Print the configured model for a complexity tier |

### Permission check examples

```bash
# Expected to allow
python doc_manager.py check --tool Bash --input "git status"

# Expected to ask for approval
python doc_manager.py check --tool Bash --input "git push origin main"

# Expected to deny
python doc_manager.py check --tool Read --input ".env"
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Allowed / successful |
| `1` | Approval required or warnings |
| `2` | Denied or blocked |
| `3` | Configuration error |

The permission gate is effective only when the agent or CLI actually runs and respects it. Tools without native hooks or permission controls require the agent to follow the protocol manually.

For the complete configuration reference and limitations, see [doc_manager_skill/README.md](doc_manager_skill/README.md).

## Requirements

- Python 3.8 or newer for the Python utilities.
- Git for cloning the repository and using the Git workflow.
- An AI agent or CLI that supports loading skill instructions; shell access is needed to use doc_manager_skill's runtime.

## Contributing

Keep changes focused and compatible with the documented platforms. When submitting changes:

1. Explain the problem and proposed change.
2. Keep edits limited to the relevant files.
3. Run applicable checks and include the results.
4. Use a Conventional Commit message, such as `docs: clarify installation steps` or `fix: handle missing skill metadata`.

## License

No `LICENSE` file is currently included in this repository. Check with the repository owner before redistributing or reusing the contents.
