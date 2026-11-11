---
name: Essential_Skill
description: Core behavioral guidelines requiring doc_manager_skill on every task, plans that assign separate execution tasks to at least four distinct subagents, strict user plan approval, cross-platform skill discovery, task-based Gemini model selection, execution audits, and automated Git workflows.
---

# Essential Skill

This skill defines the complete operational lifecycle for workspace tasks: mandatory use of `doc_manager_skill`, plans that allocate separate execution work to at least four distinct subagents, explicit user plan authorization, cross-platform skill discovery, task-based Gemini model selection, coordinated subagent execution, result audits, and safe Git workflows.

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
- If any required subagent tool is offline or fewer than four distinct execution subagents can be launched, immediately alert the user and stop; do not replace them with role prompts in one agent or assign all implementation work to the main agent.
- If the LLM Council or another optional review service is unavailable, alert the user and follow the approved fallback process.
- Do NOT silently skip mandatory verification steps or enter retry loops.

---

## Phase 1: Planning with Claude, LLM Council & Fast-Track Exception

### Rule 7: Planning & LLM Council Pre-Review
- **Analyze & Plan**: Use Claude model capabilities to inspect codebase, evaluate complexity, and construct execution steps.
- **Plan Must Allocate Execution Work to Four Subagents**: Before presenting the plan, decompose the approved scope into at least **four distinct, non-overlapping work packages** and assign each package to a different subagent instance. The plan must explicitly show, for every subagent: its role/name, exact task, files or components it owns, expected deliverable, dependencies, and verification responsibility. These are execution assignments, not planning/review personas. Examples include implementation of separate components, tests, documentation, integration, or a focused verification task, chosen to fit the actual project. Do not invent unnecessary code changes just to create assignments; use meaningful independent deliverables. The main agent coordinates, resolves interfaces, integrates the results, and checks completion; it must not silently perform all work itself. Four roles/prompts handled by one agent do not count.
- **Plan Review**: Use the LLM Council (`council-chairman` or reviewer subagent) for one critique pass when available. This optional review does not replace the four execution assignments.
- **Token & Cost Guard**: Cap Council reviews to **max 1 pass** per phase. Multi-pass reviews are forbidden unless explicitly requested by the user.
- **⚡ Fast-Track Exception for Tiny Tasks**:
  - **Condition**: Task complexity is **Low**, targets **1 single file**, and modifies **<5 lines**.
  - **Action**: Skip only the optional Pre-Plan Council Review and Post-Execution Audit. The plan must still assign four distinct execution subagents, and the mandatory `doc_manager_skill` workflow still applies. Present the assignments for approval, then execute.

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

### Rule 10: Mandatory Four-Subagent Execution
- After the user approves the plan, launch at least four **distinct Gemini subagent instances** (`invoke_subagent` / `define_subagent`) and give each the exact execution assignment listed in the plan.
- Each subagent must perform its assigned work and return its deliverable plus verification evidence. They are workers, not merely planners or reviewers. Keep ownership non-overlapping; coordinate shared interfaces through the main agent.
- The main agent coordinates the workers, integrates their deliverables, handles cross-task conflicts, and performs final end-to-end verification. It must not replace the four workers by doing all implementation itself.
- Never count four role prompts to one agent, four planning-only agents, or one worker plus three reviewers as satisfying this rule. If four distinct execution agents cannot be run, stop and ask the user rather than continuing with fewer.
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
