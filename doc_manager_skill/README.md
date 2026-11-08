# doc_manager_skill

A project operating system for AI coding agents. It gives any agent or CLI the same working environment as Claude Code: project rules loaded at session start, permission gates for commands and edits, hooks, reusable commands, skills, and a planning workflow that reads the stack's official docs before changing anything.

It works with Claude Code, Gemini CLI, Codex CLI, Cursor, and any other tool that can run a shell command. The runtime is a single Python script with no dependencies.

## What it does

- **Research before planning.** Detects the project's stack (ROS, Next.js, Django, Rust, and about 25 others) and lists the official wiki or docs to read. For a ROS workspace, it points to the ROS wiki. For a web app, it points to the framework docs plus OWASP and web.dev. The agent checks the repo against those sources and records gaps in the plan.
- **Approval gate.** No file edits or side-effect commands until you approve the plan.
- **Permission gate.** Each shell command or file edit is allowed, asked about, or denied based on `.claude/settings.json`. Compound commands are split and checked piece by piece.
- **Hooks.** Commands that run after edits or tool calls. A hook that exits with code 2 blocks the action.
- **Skill discovery.** Ranks installed skills against the project's files.
- **Model tiers.** Maps low, medium, and high complexity to the models you configure.
- **Git workflow.** Explicit staging, Conventional Commits, and a branch and remote check before the first push.

## Quick start

Requires Python 3.8 or newer. Works on Windows, Linux, and macOS.

```bash
# 1. Copy the skill into your agent's skills folder, or into the project
cp -r doc_manager_skill .claude/skills/        # project-level
# or
cp -r doc_manager_skill ~/.claude/skills/      # all projects

# 2. Scaffold the harness in your project (never overwrites existing files)
python .claude/skills/doc_manager_skill/scripts/doc_manager.py init

# 3. Check it
python .claude/skills/doc_manager_skill/scripts/doc_manager.py validate
```

Then fill in `AGENTS.md` (or `CLAUDE.md`) using `assets/root_instructions_template.md` as a guide.

## Commands

Run from the project root, or pass `--workspace <path>`.

| Command | Purpose |
|---|---|
| `init` | Create `AGENTS.md`, `.claude/` folders, and default `settings.json` if missing |
| `context` | Print the instructions an agent should load at session start |
| `discover` | Rank installed skills against the project's stack |
| `sources` | List the wikis and docs to read during planning |
| `check --tool <Tool> --input <value>` | Return allow (0), ask (1), or deny (2) for a command or path |
| `hook <Event> --tool <Tool> --input <value>` | Run hooks for an event; exit 2 blocks the action |
| `tier low\|medium\|high` | Print the model mapped to a complexity tier |
| `validate` | Check the harness for errors and warnings |

### Examples

```bash
python doc_manager.py check --tool Bash --input "git status"        # allow
python doc_manager.py check --tool Bash --input "git push origin main"  # ask
python doc_manager.py check --tool Read --input ".env"              # deny
python doc_manager.py check --tool Edit --input "migrations/0042.sql"   # ask (protected path)
python doc_manager.py sources                                       # reading list for this stack
```

## Configuration

Settings live in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Bash(git status)", "Bash(git diff:*)", "Bash(pytest:*)", "Read"],
    "ask":   ["Bash(git push:*)", "Bash(rm:*)"],
    "deny":  ["Read(./.env)", "Read(./secrets/**)"]
  },
  "protected_paths": ["migrations/**", "generated/**"],
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write", "command": "npx prettier --write ." }
    ]
  },
  "model_tiers": { "low": "", "medium": "", "high": "" },
  "council": { "enabled": false, "reviewer": "" },
  "response_style": "normal"
}
```

- `Bash(prefix:*)` matches a command and anything that starts with `prefix`. `Bash(exact)` matches the exact command.
- `Read(path)` and `Edit(path)` take glob patterns relative to the project root.
- Anything not covered by a rule asks for confirmation.
- Where two rules conflict, `deny` beats `ask`, and `ask` beats `allow`.

## Skill discovery paths

`discover` searches these locations in order. The first skill with a given name wins.

1. `.claude/skills/` and `skills/` in the project. Project-owned skills get a ranking boost.
2. Paths in `DOC_MANAGER_SKILL_PATHS` (separated by `:` on Linux and macOS, `;` on Windows).
3. `~/.claude/skills/`, `~/.agents/skills/`, and `~/.gemini/config/skills/`.

## Using it with other CLIs

Any CLI can use the runtime directly. Two integration points matter:

- **Session start:** prepend the output of `doc_manager.py context` to the agent's system prompt or instruction file.
- **Before side effects:** run `doc_manager.py check` before each shell command or edit, and treat exit codes 1 and 2 as "ask" and "deny."

If the CLI has its own hook or permission system, wire `check` and `hook` into it. If not, the agent follows the protocol by hand, and the SKILL.md says which steps are advisory.

## Repository layout

```
doc_manager_skill/
├── SKILL.md                          # Skill definition: workflow, rules, reference
├── README.md                         # This file
├── assets/
│   └── root_instructions_template.md # Starting point for AGENTS.md
└── scripts/
    └── doc_manager.py                # Runtime (stdlib only)
```

## Limits

- The permission gate is only as strong as the agent's willingness to call it. CLIs without hooks or permission systems rely on the agent following the protocol.
- The stack-to-docs map covers about 25 stacks. Other stacks get only the generic sources, and you can add entries to `SOURCE_MAP` in `scripts/doc_manager.py`.
- Some documentation sites block automated fetching. When that happens, the agent is told to note it in the plan rather than fill the gap from memory.

## Origin

The operating rules, approval gate, fast-track exception, and Git workflow are adapted from [Essential_Skill](https://github.com/Ashwin312007/Essential_Skill) by Ashwin312007. That repository's README lists an MIT license, but its clone had no LICENSE file, so confirm the license with the author before redistributing.

## License

Not yet set. Add a LICENSE file before publishing.