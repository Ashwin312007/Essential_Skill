---
name: Essential_Skill
description: Core behavioral guidelines combining Claude-driven planning, LLM Council pre-plan review & post-execution audit, strict user plan approval, cross-platform skill discovery, task-based Gemini model selection, mandatory Gemini subagent execution, cost/token guards, fast-track pipeline, failure fallbacks, caveman TUI formatting, and automated Git upload workflows.
---

# Essential Skill

This skill defines the complete operational lifecycle for workspace tasks: using Claude for strategic planning, obtaining explicit user plan authorization, running dynamic cross-platform skill discovery (`Skill_Finder`), selecting the appropriate Gemini model tier based on task complexity, executing via dedicated Gemini subagents, auditing results with the LLM Council, protecting against token bloat and tool outages, and automating Git upload workflows.

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
- If any subagent tool, MCP server, or LLM Council service is offline, unresponsive, or unavailable:
  - Immediately alert the user in TUI Caveman text.
  - Do NOT silently skip verification steps or enter retry loops.
  - Fall back to main-thread execution or direct commands with explicit user confirmation.

---

## Phase 1: Planning with Claude, LLM Council & Fast-Track Exception

### Rule 7: Planning & LLM Council Pre-Review
- **Analyze & Plan**: Use Claude model capabilities to inspect codebase, evaluate complexity, and construct execution steps.
- **LLM Council Pre-Plan Review**: Consult the **LLM Council** (`council-chairman` or multi-model subagents) to critique and refine the plan.
- **Token & Cost Guard**: Cap Council reviews to **max 1 pass** per phase. Multi-pass reviews are forbidden unless explicitly requested by the user.
- **⚡ Fast-Track Exception for Tiny Tasks**:
  - **Condition**: Task complexity is **Low**, targets **1 single file**, and modifies **<5 lines**.
  - **Action**: Skip Pre-Plan Council Review and Post-Execution Audit. Present simple plan directly to user for fast approval, then execute.

---

## Phase 2: Skill Discovery & Gemini Model Selection

### Rule 8: Mandatory Cross-Platform Skill Activation
Once the plan artifact is approved, immediately run Skill Finder using cross-platform paths:

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

### Rule 10: Always Use Gemini Subagents for Execution
- **Never execute heavy coding tasks directly on the main thread.**
- Launch dedicated Gemini subagents (`invoke_subagent` / `define_subagent`) to perform execution tasks matching chosen model tiers.
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
