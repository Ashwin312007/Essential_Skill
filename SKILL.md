---
name: Essential_Skill
description: Core behavioral guidelines requiring doc_manager_skill on every task, four distinct planning subagents with separate assignments, strict user plan approval, cross-platform skill discovery, task-based Gemini model selection, execution audits, cost/token guards, and automated Git workflows.
---

# Essential Skill

This skill defines the complete operational lifecycle for workspace tasks: mandatory use of `doc_manager_skill`, planning with at least four distinct subagents assigned separate tasks, explicit user plan authorization, cross-platform skill discovery, task-based Gemini model selection, subagent execution, result audits, and safe Git workflows.

---

## 💬 Communication & Format Standards

- **TUI (Chat Window Output)**: Must strictly use **Caveman Language** (terse, telegraphic, ultra-compressed, direct receipts, zero fluff). Keep responses short to save context window tokens.
- **Artifacts**: Detailed, structured, comprehensive Markdown documents providing full architectural and operational context.

---

## 📌 Mandatory Core Rules (Basic Skills Integration)

### Rule 1: Planning, Approval Gate & Rejection Handling
- **Always plan before modifying any files.**
- Construct a structured plan as an **Artifact** detailing objectives, complexity level, recommended model tiers, and step-by-step tasks.
- Set `RequestFeedback: true` on the artifact metadata.
- **STRICT APPROVAL GATE**: **Do NOT modify files or execute code until the user explicitly approves the Plan Artifact.**
- **Repeated Rejection Guard**: If the user rejects the plan artifact **2 consecutive times**, stop automated plan generation. Ask the user in TUI text to provide exact requirements, preferred design, or step-by-step instructions directly.
- **Mandatory `doc_manager_skill`**: Before planning any task, locate and read `doc_manager_skill/SKILL.md` (use the installed skill path if it is not in the workspace). Run its `context` command and inspect the result. Run `validate` when the workspace already has a harness. If the harness is missing, include `doc_manager.py init` in the plan and run it only after approval; never create harness files before approval. After approval, run `init` if needed, then `validate`, `context`, and `discover`. Use `doc_manager.py check` before every side effect and run the configured `PostToolUse` hook after each edit or command. Run `validate` again before completion. If `doc_manager_skill` or its runtime is unavailable, stop and ask the user; do not bypass it or substitute another workflow.

### Rule 2: No Assumptions
- **Make no assumptions.**
- If any requirement, design decision, architectural option, or detail is ambiguous, ask the user directly to clarify before drafting the plan.

### Rule 3: Simplicity Over Over-Engineering
- **Keep the project simple.**
- Avoid unrequested abstractions, unnecessary future-proofing, or adding extra libraries unless explicitly instructed by the user.

### Rule 4: Minimize Scope & Contained Edits
- **Do not make changes to adjacent or unrelated files.**
- Keep edits localized exclusively to the files directly required for the task. Do not touch or refactor surrounding files without explicit permission.

### Rule 5: Goal Definition & Empirical Verification
- **Define clear, measurable goals** in the plan.
- **Gather empirical runtime verification** (running builds, tests, or validation commands) demonstrating clean success before declaring work complete.

### Rule 6: Tool & Service Unavailability Fallback
- If any required subagent tool is offline or fewer than four distinct subagents can be launched, immediately alert the user and stop; do not replace them with role prompts in one agent or main-thread work.
- If the LLM Council or another optional review service is unavailable, alert the user and follow the approved fallback process.
- Do NOT silently skip mandatory verification steps or enter retry loops.

---

## Phase 1: Planning with Claude, LLM Council & Fast-Track Exception

### Rule 7: Planning & LLM Council Pre-Review
- **Analyze & Plan**: Use Claude model capabilities to inspect codebase, evaluate complexity, and construct execution steps.
- **Mandatory Four-Agent Planning Team**: Before presenting any plan, launch at least **four distinct subagent instances**. Each must receive a separate, non-overlapping planning assignment and return its own findings. Required assignments:
  1. **Requirements Analyst** — extract user goals, constraints, ambiguities, and acceptance criteria.
  2. **Codebase Analyst** — inspect relevant files, architecture, dependencies, and existing conventions.
  3. **Design/Risk Analyst** — assess implementation options, edge cases, security, and scope risks.
  4. **Verification Planner** — define tests, validation commands, and measurable completion checks.
  These are four separate agents, not four personas or sequential prompts to one agent. They must not modify files during planning. Combine their independent reports into one plan and identify unresolved disagreements. Add more agents when useful; never use fewer than four.
- **LLM Council Pre-Plan Review**: After the four reports are consolidated, consult the **LLM Council** (`council-chairman` or multi-model subagents) for one critique pass when available. The Council review does not replace the four required subagents.
- **Token & Cost Guard**: Cap Council reviews to **max 1 pass** per phase. Multi-pass reviews are forbidden unless explicitly requested by the user.
- **⚡ Fast-Track Exception for Tiny Tasks**:
  - **Condition**: Task complexity is **Low**, targets **1 single file**, and modifies **<5 lines**.
  - **Action**: Skip only the optional Pre-Plan Council Review and Post-Execution Audit. The four distinct planning subagents and mandatory `doc_manager_skill` workflow still apply. Present the simple plan for approval, then execute.

---

## Phase 2: Skill Discovery & Gemini Model Selection

### Rule 8: Mandatory Cross-Platform Skill Activation
Once the plan artifact is approved, immediately run `doc_manager.py discover` and Skill Finder using cross-platform paths. `doc_manager_skill` is mandatory on every task; other matched skills are activated as applicable:

#### Step 1: Execute Skill Finder (Cross-Platform)
Run skill discovery script dynamically based on OS:
```powershell
# Windows PowerShell
python "$env:USERPROFILE\.gemini\config\skills\Essential_Skill\scripts\find_skills.py"
```
```bash
# Linux / macOS Bash
python "$HOME/.gemini/config/skills/Essential_Skill/scripts/find_skills.py"
```
*(Or target a specific workspace path)*:
```powershell
python "$env:USERPROFILE\.gemini\config\skills\Essential_Skill\scripts\find_skills.py" "C:\path\to\workspace"
```

#### Step 2: Read and Activate Matched Skills
1. Review output from `find_skills.py`.
2. Inspect every matched skill's `SKILL.md` via `view_file`.
3. Activate its specific rules and standards right from the start of execution.

### Rule 9: Gemini Model Selection Based on Work Complexity
Determine the appropriate Gemini model tier for subagent execution based on task complexity:

| Task Complexity | Work Type | Selected Gemini Model Tier |
| :--- | :--- | :--- |
| **Low** | Simple file edits, typos, quick lookups, basic single-file fixes | `flash_lite` or `flash` |
| **Medium** | Feature implementation, component scaffolding, API integration | `flash` or `inherit` |
| **High** | Architectural refactoring, multi-file changes, deep debugging, complex reasoning | `pro` or `inherit` |

---

## Phase 3: Subagent Execution & Verification

### Rule 10: Mandatory Subagent Execution
- The four distinct planning subagents in Rule 7 are required for every task, including low-complexity and fast-track tasks. Each must complete its own separate planning assignment before the plan is presented.
- After approval, launch dedicated Gemini subagents (`invoke_subagent` / `define_subagent`) for execution tasks matching the approved plan and model tiers. Keep execution assignments scoped and non-overlapping.
- Never claim that one agent with four role prompts satisfies the four-agent requirement. If four distinct planning agents cannot be run, stop and ask the user rather than continuing with fewer.
- Verify all target goals empirically (builds, tests, or scripts).

---

## Phase 4: LLM Council Post-Execution Audit & Remediation Loop

### Rule 11: LLM Council Post-Audit & Remediation
- **Post-Execution Audit**: Consult the **LLM Council** to audit completed work against initial goals, localized scope limits (Rule 4), and verification evidence (Rule 5).
- **Token Guard**: Capped at **max 1 audit pass**.
- **Audit Remediation Loop**: If Council Audit passes -> Proceed to Phase 5. If audit fails -> Loop back to Phase 3 (Execution) with specific findings to fix issues. *(Skipped for Fast-Track tasks)*.

---

## Phase 5: Automated Git Upload Workflow

### Rule 12: Automated Git Upload & Synchronization
1. **Repository Check**: Run `git rev-parse --is-inside-work-tree`. If not a git repo, prompt user or run `git init` if confirmed.
2. **Status Verification**: Run `git status --short` to confirm only planned files are modified.
3. **Explicit Staging**: Run `git add <file1> <file2>` (explicit file paths; no indiscriminate `git add .`).
4. **Structured Commit**: Run `git commit -m "type(scope): concise description"` using Conventional Commit standards (`feat:`, `fix:`, `docs:`, `refactor:`).
5. **Remote Push & Branch Guard**:
   - Run `git remote -v`.
   - **Git Branch Guard**: Before performing initial `git push` on a newly initialized repository or unpushed branch, confirm the target branch name (e.g. `main`, `master`, `feature/xyz`) and remote URL with the user in TUI text.
   - If branch is set: execute `git push -u origin <branch_name>`.
   - If out of sync: execute `git pull --rebase origin <branch_name>`. If rebase conflicts occur, execute `git rebase --abort` and ask user for guidance.
