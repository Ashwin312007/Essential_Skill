---
name: doc_manager_skill
description: Full project operating system for any AI coding agent or CLI. Sets up and runs a Claude Code-style harness (root instructions in AGENTS.md or CLAUDE.md, scoped rules, reusable commands, skills, agent roles, permission gates, and hooks) and a disciplined workflow: research the stack's official wiki and docs (such as the ROS wiki for robotics or framework docs and OWASP for web apps) to find architecture and design flaws, plan, wait for approval, match skills to the project, run work with a model tier, verify, audit, then commit with Conventional Commits. Use this whenever the user wants to onboard an AI to a codebase, stop repeating project context, set guardrails for what an AI can change, write or update an instruction file, make any CLI work like Claude Code, plan and approve AI edits before they happen, automate Git commits and pushes safely, or organise AI skills and prompts, even if they don't use these terms.
---

# doc_manager_skill

This skill gives any AI agent the same working environment as Claude Code. It has two parts:

1. **Files**: a `.claude/` directory and a root instruction file that hold the project's rules.
2. **Runtime**: `scripts/doc_manager.py`, a stdlib-only Python CLI (Windows, Linux, macOS, Python 3.8+) that any agent can call. It enforces the rules, which a markdown file cannot do on its own.

Define the rules once in the repository and let every agent load them.

---

## 1. Replicating the Claude Code harness in any CLI

| Claude Code feature | Portable equivalent | Command |
|---|---|---|
| `CLAUDE.md` loaded at session start | Root file (`AGENTS.md`, or `CLAUDE.md`) plus rules, prepended to the system prompt | `doc_manager.py context` |
| `.claude/rules/` | Scoped rule files, each with an "applies when" line | included in `context` |
| `.claude/commands/` | Reusable prompt templates | listed in `context` |
| `.claude/skills/` | Skill folders with `SKILL.md`, matched to the project | `doc_manager.py discover` |
| `.claude/agents/` | Focused role definitions (reviewer, auditor, test engineer) | listed in `context` |
| `settings.json` permissions (allow / ask / deny) | Permission gate with exit codes 0 / 1 / 2 | `doc_manager.py check --tool <T> --input <V>` |
| Hooks (`PreToolUse`, `PostToolUse`) | Commands that run on events; exit 2 blocks the action | `doc_manager.py hook <Event> --tool <T> --input <V>` |
| Subagent model selection | Complexity tiers mapped to models | `doc_manager.py tier low\|medium\|high` |
| Planning research | Official wiki and docs for the detected stack | `doc_manager.py sources` |
| Project health | Harness validator | `doc_manager.py validate` |

### Wiring it into an agent

Do this once at the start of each session:

```bash
python scripts/doc_manager.py init        # scaffold, only if missing; never overwrites
python scripts/doc_manager.py validate    # fix any ERROR lines before work begins
python scripts/doc_manager.py context     # load this output into the agent's instructions
```

Before any shell command, file write, or other side effect that isn't clearly routine:

```bash
python scripts/doc_manager.py check --tool Bash --input "git push origin main"
# exit 0 = allow, run it
# exit 1 = ask, get the user's explicit confirmation first
# exit 2 = deny, do not run it, explain why to the user
```

After each edit or command, run the hooks for that event:

```bash
python scripts/doc_manager.py hook PostToolUse --tool Edit --input "src/app.py"
# exit 2 means a hook blocked the action: stop, report the hook's output, and fix the cause
```

### Agents without native hooks or permissions

Some CLIs have no hook or permission system. The agent still follows the same protocol by hand. It runs `context` at the start, runs `check` before risky actions and treats `ask` and `deny` the same way the harness would, and runs the hook commands listed in `.claude/settings.json` after edits. Say which steps are manual so the user knows the gate is advisory.

### Making the agent load this skill

Put a short pointer in the root file or the tool's own instruction file, for example: "Before working here, run `python scripts/doc_manager.py context` and follow the rules it prints." This is the only setup step a new tool needs.

---

## 2. Operating rules

These rules apply to every task in the project. They come from Essential_Skill and have been generalised so they don't depend on one vendor.

**R1. Research, then plan, before modifying files.** Read the stack's wiki or docs (Phase 1, `doc_manager.py sources`) and inspect the repo. Then write a plan with the research findings, the objective, complexity (Low, Medium, or High), the model tier for each step, the files it will touch, and measurable success criteria. Mark the plan as awaiting approval.

**R2. Approval gate.** Do not modify files or run side-effect commands until the user explicitly approves the plan. Silence is not approval. If the user rejects the plan twice in a row, stop generating plans and ask for exact requirements, a preferred design, or step-by-step instructions.

**R3. No assumptions.** If a requirement, design choice, or detail is ambiguous, ask before planning. Ask one focused question at a time when possible.

**R4. Keep it simple.** Don't add abstractions, future-proofing, or libraries the user didn't ask for.

**R5. Contain edits.** Change only the files the task requires. Don't refactor adjacent code without permission.

**R6. Verify empirically.** Before reporting success, run the build, tests, or validation commands and show the result. "It should work" is not verification.

**R7. Tool outages.** If a subagent, MCP server, or review service is unavailable, tell the user immediately. Don't skip verification silently and don't loop on retries. Fall back to direct execution only with the user's confirmation.

**R8. Protected paths.** Anything matched by `protected_paths` in settings (migrations, generated code, production configs, vendored code) needs explicit permission. The `check` command returns `ask` for these.

**R9. Secrets.** Never print, commit, or log values from `.env`, key files, or credential directories. The default settings deny reads of these.

**R10. Scope of review.** When a second pass is available, use it to critique the plan and audit the result. Limit reviews to one pass per phase unless the user asks for more. Reviews check against the goals, the scope rule (R5), and the verification evidence (R6).

---

## 3. Workflow

### Phase 1: Research, plan, and review

Planning is research first. Do not propose changes to a project you have not read about, because the wiki for that stack often documents the intended architecture and the common mistakes.

1. **Inspect the repository.** Check for existing AGENTS.md, CLAUDE.md, rules, lint configs, CI files, and READMEs. Reuse what's there. Note the stack, the entry points, and the main modules.

2. **Get the reading list.** Run `python scripts/doc_manager.py sources`. It maps the detected stack to the official wiki or docs for that stack. Examples:
   - A ROS workspace gets the ROS wiki (or ROS 2 docs), checked for package architecture, node, topic, and service design, launch files, and the ROS version the repo targets.
   - A web app gets the framework docs, plus OWASP and web.dev, checked for design flaws: auth, injection, access control, misconfiguration, rendering pitfalls, and performance.
   - Every project gets the Twelve-Factor App and the project's own docs and ADRs.

3. **Visit each source and record findings.** Open each page with `web_fetch` (or a browser tool if one is available) and read the parts the "check:" line names. For each source, write down:
   - what the source says the project should look like, and whether this repo follows it
   - design flaws or anti-patterns the repo shows that the source warns about
   - the exact URL and the section you used, so the user can check it

   If a page can't be read (blocked, offline, or paywalled), record that in the plan. Don't fill the gap from memory and present it as sourced.

4. **Compare against the wiki's guidance.** Build a short list of gaps: where the repo departs from the documented architecture, where the wiki's recommended pattern would fix a flaw you found, and where the repo is fine and should stay as it is. Mark any gap that's a judgment call as a question for the user, not a fact.

5. **Write the plan (R1)** as an artifact or document the user can read. Include a "Research" section that lists the sources visited, the findings, and the gaps. Then the proposed steps, the complexity, the model tiers, and measurable goals.

   If the change is Low complexity, touches one file, and modifies fewer than 5 lines, use the **fast track**: keep the research short (sources read, one line of findings), present the plan, get approval, execute, and skip the review passes.

6. **Review** the plan if a reviewer is available (see Section 4), then present the revised plan for approval (R2).

Keep the research in scope. Read only the sections the project's stack needs. Stop once you have enough to make the gap list, and don't turn the plan into a survey of the whole wiki.

### Phase 2: Skill matching and model tier

1. After approval, run `python scripts/doc_manager.py discover`.
2. Read the `SKILL.md` of each matched skill before acting, and apply its rules from the start.
3. Pick the model for each step with `doc_manager.py tier <level>`:

| Complexity | Typical work | Tier |
|---|---|---|
| Low | Typos, single-file fixes, quick lookups | `low` |
| Medium | Feature work, scaffolding, API integration | `medium` |
| High | Multi-file refactors, deep debugging, architecture | `high` |

If a tier prints "current session model", use the model you're running on.

### Phase 3: Execution

Run heavy coding work in a dedicated subagent when the agent supports one, so the main thread stays clean. If it doesn't, execute directly, keep each step small, and verify after each step. Check every action with `check` before running it, and run the `PostToolUse` hooks after each edit.

### Phase 4: Audit and remediation

After execution, compare the result against the plan's goals, check the diff against the contained-edit rule (R5), and confirm the verification output from R6. If the audit fails, return to Phase 3 with the specific findings. Cap at one audit pass per phase unless the user asks for more. The fast track skips this phase.

### Phase 5: Git upload

1. Confirm a repository exists with `git rev-parse --is-inside-work-tree`. If not, ask before running `git init`.
2. Run `git status --short` and confirm only planned files changed.
3. Stage explicit paths with `git add <file> ...`. Never use `git add .` or `git add -A`.
4. Commit with a Conventional Commit message: `type(scope): short description`, where type is `feat`, `fix`, `docs`, `refactor`, `test`, or `chore`.
5. Before the first push of a new branch, confirm the branch name and remote with the user. Run `git remote -v` to show the remote.
6. Push with `git push -u origin <branch>`. If the branch is behind, run `git pull --rebase origin <branch>`. If the rebase conflicts, run `git rebase --abort` and ask the user how to proceed.
7. Run `check` on every git push before running it. Pushes ask by default, and force pushes should be denied.

---

## 4. Optional review pass (LLM Council)

The review passes in Phases 1 and 4 use a second opinion. Configure it in settings:

```json
"council": { "enabled": true, "reviewer": "a different model or a reviewer agent" }
```

When it's disabled or unavailable, do a self-review against the checklist below and say in the report that it was self-reviewed.

**Plan review checklist:** Are goals measurable? Is scope limited to the requested files? Are the model tiers right? Are any assumptions still unstated?

**Audit checklist:** Does the diff match the plan? Did any unrelated file change? Is there verification output? Are protected paths untouched?

---

## 5. Communication style

- **Chat replies** can be terse when the user prefers it (Essential_Skill calls this "caveman" style: short, direct, no filler). Set `"response_style": "terse"` in settings to make this the default.
- **Documents, plans, and artifacts** should be complete and structured, with full context.

---

## 6. Creating the harness in a new project

1. Run `doc_manager.py init`.
2. Fill in `AGENTS.md` from `assets/root_instructions_template.md`. Keep it under 200 lines and put detail in `.claude/rules/`.
3. Set `permissions` and `protected_paths` in `.claude/settings.json` for this project.
4. Add rules, commands, skills, agents, and hooks only when the workflow needs them. Start with the root file.
5. Run `doc_manager.py validate`, then have the user review the root file and the settings before you call the setup finished.

---

## Configuration reference (`.claude/settings.json`)

```json
{
  "permissions": {
    "allow": ["Bash(git status)", "Bash(git diff:*)", "Bash(pytest:*)", "Read", "Edit(src/**)"],
    "ask":   ["Bash(git push:*)", "Bash(rm:*)", "Bash(npm install:*)"],
    "deny":  ["Read(./.env)", "Read(./secrets/**)", "Bash(git push --force:*)"]
  },
  "protected_paths": ["migrations/**", "generated/**"],
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write", "command": "npx prettier --write ." },
      { "matcher": "Bash", "command": "python scripts/block_force_push.py" }
    ]
  },
  "model_tiers": { "low": "", "medium": "", "high": "" },
  "council": { "enabled": false, "reviewer": "" },
  "response_style": "normal"
}
```

Rules:
- `Bash(prefix:*)` matches the command and anything starting with `prefix` followed by a space. `Bash(exact)` matches exactly.
- Compound commands (`&&`, `||`, `;`, `|`) are split, and the strictest decision wins. `deny` beats `ask`, which beats `allow`.
- `Read(path)` and `Edit(path)` use glob patterns relative to the project root.
- Anything not matched by a rule is `ask`.
- A hook with exit code 2 blocks the action. A hook with any other non-zero exit code is reported as a warning.

---

## Discovering skills

`discover` searches these locations in order, and the first skill with a given name wins:

1. `.claude/skills/` and `skills/` in the project (project-owned skills get a ranking boost)
2. Any paths in the `DOC_MANAGER_SKILL_PATHS` environment variable (separated by `:` on Linux and macOS, `;` on Windows)
3. `~/.claude/skills/`, `~/.agents/skills/`, and `~/.gemini/config/skills/`

To use a skill folder that lives elsewhere, add its parent folder to `DOC_MANAGER_SKILL_PATHS`.

---

## Files in this skill

- `scripts/doc_manager.py`: the runtime (`init`, `context`, `discover`, `sources`, `check`, `hook`, `tier`, `validate`)
- `assets/root_instructions_template.md`: a fill-in root handbook

## Origin and credits

Operating rules, the plan-approval gate, the fast-track exception, the Git workflow, and the skill-discovery approach are adapted from Essential_Skill by Ashwin312007 (github.com/Ashwin312007/Essential_Skill). The repository's README lists an MIT license, but no LICENSE file was present in the clone, so check the license with the author before redistributing.