# ⚡ Essential Skill

> Core behavioral guidelines and automated workflow engine for AI coding agents.

## 📖 Overview

**Essential Skill** provides a structured, high-reliability operational lifecycle for AI agents. It combines strategic planning, explicit user plan authorization, dynamic cross-platform skill discovery, task-driven model tier selection, subagent execution, LLM Council auditing, token/cost protections, and automated Git synchronization.

---

## ✨ Key Features

- **📋 Strategic Planning & Approval Gate**: Enforces pre-execution planning and requires explicit user authorization before file mutations occur.
- **🔍 Cross-Platform Skill Discovery**: Includes `scripts/find_skills.py` to dynamically inspect workspaces across Windows, Linux, and macOS to activate relevant domain skills.
- **⚡ Fast-Track Pipeline**: Bypasses heavy auditing overhead for single-file, low-complexity edits (<5 lines) to maintain fast turnarounds.
- **🏛️ LLM Council Reviews**: Integrates pre-plan critique and post-execution audits to verify implementation quality and prevent unauthorized scope drift.
- **🤖 Task-Driven Model Selection**: Maps task complexity (Low, Medium, High) to optimal model tiers (`flash_lite`, `flash`, `pro`).
- **🚀 Automated Git Workflows**: Enforces explicit staging, Conventional Commits, and safe remote synchronization with branch protection guards.

---

## 🛠️ Repository Structure

```
Essential_Skill/
├── SKILL.md                 # Primary skill definition and operational guidelines
├── README.md                # Repository documentation
└── scripts/
    └── find_skills.py       # Cross-platform workspace skill discovery script
```

---

## 🚀 Usage

### 1. Skill Discovery Script

To scan a workspace and list matched agent skills:

#### Windows (PowerShell)
```powershell
python "$env:USERPROFILE\.gemini\config\skills\Essential_Skill\scripts\find_skills.py" "C:\path\to\workspace"
```

#### Linux / macOS (Bash)
```bash
python "$HOME/.gemini/config/skills/Essential_Skill/scripts/find_skills.py" "/path/to/workspace"
```

---

## 📄 License

[MIT License](LICENSE)
