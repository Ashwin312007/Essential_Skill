---
name: Essential_Skill
description: Core behavioral guidelines combining Claude-driven planning, LLM Council pre-plan review & post-execution audit, strict user plan approval, automated skill discovery, task-based Gemini model selection, mandatory Gemini subagent execution, caveman TUI formatting, and automated Git upload workflows.
---

# Essential Skill

This skill defines the complete operational lifecycle for workspace tasks: using Claude for strategic planning, obtaining explicit user plan authorization, running dynamic skill discovery (`Skill_Finder`), selecting the appropriate Gemini model tier based on task complexity, always executing via dedicated Gemini subagents, auditing results with the LLM Council, and automating Git upload workflows.

---

## 💬 Communication & Format Standards

- **TUI (Chat Window Output)**: Must strictly use **Caveman Language** (terse, telegraphic, ultra-compressed, direct receipts, zero fluff). Keep responses short to save context window tokens.
- **Artifacts**: Detailed, structured, comprehensive Markdown documents providing full architectural and operational context.

---

## Phase 1: Planning with Claude, LLM Council & Plan Approval

### Rule 1: Planning with Claude Model & LLM Council
- **Always plan before modifying any files.**
- **Use Claude model for planning**: Consult Claude / LLM Council planning capabilities to analyze the codebase, break down requirements, evaluate task complexity, and construct a comprehensive step-by-step plan.
- **LLM Council Pre-Plan Review**: Consult the **LLM Council** (`council-chairman` or multi-model reviewer subagents) to critique, stress-test, and refine the plan before finalizing.
- **Create Plan Artifact**: Save the plan as a structured **artifact** detailing:
  1. Objectives and scope.
  2. Identified task complexity level (Low / Medium / High).
  3. Recommended Gemini model tier for execution subagents (`flash_lite`, `flash`, `pro`, `inherit`).
  4. Step-by-step implementation tasks.
- **Get Explicit User Approval**: Request explicit user approval on the plan artifact (using `RequestFeedback: true`) before performing any code modifications or execution tasks.
- **STRICT APPROVAL GATE**: **Do NOT modify files or execute code until the user explicitly approves the Plan Artifact.**

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

---

## Phase 2: Skill Discovery & Gemini Model Selection

### Rule 6: Mandatory Skill Activation Upon Plan Approval
Once the user explicitly approves the plan artifact, you **must immediately run Skill Finder** (or run shift-left skill discovery prior to plan finalization) to discover and activate all domain-specific skills relevant to the workspace before starting implementation.

#### Step 1: Execute Skill Finder
Run the skill discovery script against the project/workspace directory:
```powershell
python C:\Users\teash\.gemini\config\skills\Essential_Skill\scripts\find_skills.py
```
*(Or specify the target workspace path if working in a specific project subdirectory)*:
```powershell
python C:\Users\teash\.gemini\config\skills\Essential_Skill\scripts\find_skills.py "C:\path\to\workspace"
```

#### Step 2: Read and Activate Matched Skills
1. Review the output from `find_skills.py`.
2. For every relevant matched skill returned:
   - Use the `view_file` tool to inspect its `SKILL.md`.
   - Activate its specific rules, design standards, and architectural patterns right from the start of implementation.
3. Inform the user which skills were matched and activated for the project execution phase.

### Rule 7: Gemini Model Selection Based on Work Complexity
Determine the appropriate Gemini model tier for subagent execution based on the task complexity established in the approved plan:

| Task Complexity | Work Type | Selected Gemini Model Tier |
| :--- | :--- | :--- |
| **Low** | Simple file edits, typos, quick lookups, basic single-file fixes | `flash_lite` or `flash` |
| **Medium** | Feature implementation, component scaffolding, API integration | `flash` or `inherit` |
| **High** | Architectural refactoring, multi-file changes, deep debugging, complex reasoning | `pro` or `inherit` |

---

## Phase 3: Subagent Execution & Verification

### Rule 8: Always Use Gemini Subagents for Execution
- **Never execute heavy coding tasks directly on the main thread.**
- **Always launch Gemini subagents** (`invoke_subagent` or `define_subagent`) to perform execution tasks:
  - Assign clear, self-contained subtasks to each subagent.
  - Set the `Model` parameter (`flash_lite`, `flash`, `pro`, `inherit`) matching the chosen Gemini model tier for that subtask.
  - Subagents run using Gemini models, execute code edits, run build/test commands, and report results back to the main thread.
- Upon subagent completion:
  - Verify all goals empirically.
  - Synthesize and present the completed work clearly to the user.

---

## Phase 4: LLM Council Post-Execution Audit & Remediation Loop

### Rule 9: LLM Council Post-Audit & Remediation
- **Post-Execution Audit**: Once subagent execution and empirical verification are complete, consult the **LLM Council** (`council-chairman` or multi-model auditor subagents) to audit completed work against initial goals, localized scope limits (Rule 4), and verification evidence (Rule 5).
- **Audit Remediation Loop**:
  - If the Council Audit passes -> Proceed to Phase 5.
  - If the Council Audit detects bugs, scope creep, or unverified goals -> Automatically loop back to Phase 3 (Execution) with specific audit findings to fix issues before proceeding.

---

## Phase 5: Automated Git Upload Workflow

### Rule 10: Automated Git Upload & Synchronization
1. **Repository Check**:
   - Run `git rev-parse --is-inside-work-tree`.
   - If not a git repo, prompt user or execute `git init` if confirmed.
2. **Status Verification**:
   - Run `git status --short` to ensure only planned target files are modified.
3. **Explicit Staging**:
   - Run `git add <file1> <file2>` (use explicit paths; avoid indiscriminate `git add .` to strictly preserve localized scope).
4. **Structured Commit**:
   - Run `git commit -m "type(scope): concise description"` using Conventional Commit standards (`feat:`, `fix:`, `docs:`, `refactor:`).
5. **Remote Synchronization & Push**:
   - Run `git remote -v`.
   - If remote is set: execute `git push`.
   - If no upstream branch: execute `git push -u origin <current_branch>`.
   - If remote out of sync: execute `git pull --rebase origin <current_branch>`.
   - If rebase conflicts occur: run `git rebase --abort` and ask user for manual guidance.
