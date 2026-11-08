#!/usr/bin/env python3
"""doc_manager: a CLI-agnostic project harness.

Replicates the parts of the Claude Code harness that matter for a project:
  - root instructions (AGENTS.md or CLAUDE.md)
  - scoped rules, commands, agent roles (.claude/rules, .claude/commands, .claude/agents)
  - skill discovery (.claude/skills plus shared skill folders)
  - permission decisions (allow / ask / deny) from .claude/settings.json
  - event hooks with blocking exit codes (exit 2 blocks, as in Claude Code)
  - model tier mapping for subagents

Stdlib only. Runs on Windows, Linux and macOS with Python 3.8+.

Any agent or CLI can call it. Typical integration:
  python doc_manager.py context          # prepend output to the system prompt
  python doc_manager.py check --tool Bash --input "git push"   # gate a command
  python doc_manager.py hook PostToolUse --tool Edit --input "src/app.py"

Exit codes: 0 ok / allow, 1 ask or warnings, 2 deny or blocked, 3 config error.
"""
import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_CANDIDATES = ["AGENTS.md", "CLAUDE.md"]
CLAUDE_DIR = ".claude"
SUBDIRS = ["rules", "commands", "skills", "agents", "hooks"]
SKILL_FILE = "SKILL.md"
ROOT_LINE_WARN = 200
SKIP_DIRS = {"node_modules", "venv", "env", "__pycache__", "target", "build", "dist", "out"}
DECISION_RANK = {"allow": 0, "ask": 1, "deny": 2}
DECISION_EXIT = {"allow": 0, "ask": 1, "deny": 2}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}

DEFAULT_SETTINGS = {
    "permissions": {
        "allow": ["Bash(git status)", "Bash(git diff:*)", "Bash(git log:*)", "Read"],
        "ask": ["Bash(git push:*)", "Bash(rm:*)", "Bash(npm install:*)", "Bash(pip install:*)"],
        "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"],
    },
    "protected_paths": ["migrations/**", "generated/**"],
    "hooks": {"PostToolUse": []},
    "model_tiers": {"low": "", "medium": "", "high": ""},
    "council": {"enabled": False, "reviewer": ""},
}

# Keyword detection, adapted from Essential_Skill's find_skills.py.
FILE_KEYWORDS = {
    "package.json": {"javascript", "node", "npm"},
    "tsconfig.json": {"typescript"},
    "requirements.txt": {"python", "pip"},
    "pyproject.toml": {"python"},
    "cargo.toml": {"rust", "cargo"},
    "go.mod": {"go", "golang"},
    "cmakelists.txt": {"c++", "cmake"},
    "dockerfile": {"docker", "container"},
    "docker-compose.yml": {"docker", "container"},
    "firebase.json": {"firebase", "firestore"},
    "angular.json": {"angular"},
    "next.config.js": {"nextjs", "react"},
    "next.config.mjs": {"nextjs", "react"},
    "tailwind.config.js": {"tailwind"},
    "tailwind.config.ts": {"tailwind"},
    "vite.config.js": {"vite", "react"},
    "vite.config.ts": {"vite", "react"},
    "svelte.config.js": {"svelte"},
    "package.xml": {"ros", "ros2"},
}
EXT_KEYWORDS = {
    ".py": {"python"},
    ".js": {"javascript", "react"},
    ".jsx": {"javascript", "react"},
    ".ts": {"typescript"},
    ".tsx": {"typescript", "react"},
    ".rs": {"rust"},
    ".go": {"go"},
    ".cpp": {"c++", "cpp"},
    ".hpp": {"c++", "cpp"},
    ".cc": {"c++", "cpp"},
    ".h": {"c++", "cpp"},
    ".c": {"c"},
    ".sql": {"sql", "database"},
    ".sol": {"solidity", "ethereum", "web3"},
    ".tf": {"terraform", "infrastructure"},
    ".launch": {"ros", "ros2"},
    ".msg": {"ros", "ros2"},
    ".srv": {"ros", "ros2"},
}

# Official wikis and docs to read during planning, keyed by detected keyword.
# Each entry: (name, url, what to check there).
SOURCE_MAP = {
    "ros": [("ROS wiki", "https://wiki.ros.org/", "package architecture, node/topic/service design, launch files, message conventions, the ROS version this repo targets")],
    "ros2": [("ROS 2 documentation", "https://docs.ros.org/", "node lifecycle, QoS settings, executors, colcon build layout, package structure")],
    "px4": [("PX4 docs", "https://docs.px4.io/", "module architecture, uORB messaging, parameter and failsafe handling")],
    "react": [("React docs", "https://react.dev/", "component design, state placement, effect misuse, keys and rendering pitfalls")],
    "nextjs": [("Next.js docs", "https://nextjs.org/docs", "routing model, server vs client components, data fetching, caching")],
    "typescript": [("TypeScript handbook", "https://www.typescriptlang.org/docs/", "type safety gaps, any-usage, strictness flags")],
    "javascript": [("MDN Web Docs", "https://developer.mozilla.org/", "API correctness, browser compatibility, security-sensitive APIs")],
    "node": [("Node.js docs", "https://nodejs.org/docs/latest/api/", "async error handling, streams, process and security defaults")],
    "vue": [("Vue guide", "https://vuejs.org/guide/", "component structure, reactivity pitfalls")],
    "svelte": [("Svelte docs", "https://svelte.dev/docs", "component structure, reactivity model")],
    "tailwind": [("Tailwind docs", "https://tailwindcss.com/docs", "class conventions, config, responsive patterns")],
    "python": [("Python docs", "https://docs.python.org/3/", "stdlib usage, typing, packaging")],
    "django": [("Django docs", "https://docs.djangoproject.com/", "models, migrations, security settings, deployment checklist")],
    "fastapi": [("FastAPI docs", "https://fastapi.tiangolo.com/", "dependency injection, validation, async usage")],
    "rust": [("The Rust Book", "https://doc.rust-lang.org/book/", "ownership design, error handling, unsafe usage")],
    "go": [("Effective Go", "https://go.dev/doc/effective_go", "package layout, error handling, concurrency patterns")],
    "c++": [("cppreference", "https://en.cppreference.com/", "memory safety, RAII, undefined behaviour")],
    "docker": [("Docker docs", "https://docs.docker.com/", "image size, non-root users, secrets handling")],
    "kubernetes": [("Kubernetes docs", "https://kubernetes.io/docs/", "resource limits, probes, security context")],
    "terraform": [("Terraform docs", "https://developer.hashicorp.com/terraform/docs", "state handling, module structure, drift")],
    "sql": [("PostgreSQL docs", "https://www.postgresql.org/docs/", "indexes, migrations, transaction boundaries")],
    "firebase": [("Firebase docs", "https://firebase.google.com/docs", "security rules, data modelling")],
    "solidity": [("Solidity docs", "https://docs.soliditylang.org/", "reentrancy, access control, upgrade safety")],
    "godot": [("Godot docs", "https://docs.godotengine.org/", "scene structure, signals, performance")],
}
# Checked for every project regardless of stack.
ALWAYS_SOURCES = [
    ("The Twelve-Factor App", "https://12factor.net/", "config, dependencies, logging and process model"),
    ("Project's own docs", "README, CONTRIBUTING, docs/, and any ADRs in the repo", "stated architecture, decisions already made, known issues"),
]
WEB_SOURCES = [
    ("OWASP Top 10", "https://owasp.org/www-project-top-ten/", "auth, injection, access control, misconfiguration in the design"),
    ("web.dev", "https://web.dev/", "performance, accessibility, security headers"),
]
WEB_KEYWORDS = {"javascript", "typescript", "react", "nextjs", "vue", "svelte", "node", "django", "fastapi", "firebase", "tailwind"}


# ----------------------------------------------------------------- helpers

def die(msg, code=3):
    print(f"doc_manager: {msg}", file=sys.stderr)
    sys.exit(code)


def find_root(ws):
    for name in ROOT_CANDIDATES:
        p = ws / name
        if p.is_file():
            return p
    return None


def load_settings(ws):
    """Merge .claude/settings.json over defaults. Missing file means defaults."""
    merged = json.loads(json.dumps(DEFAULT_SETTINGS))
    p = ws / CLAUDE_DIR / "settings.json"
    if not p.is_file():
        return merged
    try:
        user = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"invalid JSON in {p}: {e}")
    for key, value in user.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_frontmatter(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line[:1].isspace():
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta


def first_line(path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip() and not line.startswith("#"):
            return line.strip()[:160]
    return ""


def skill_search_paths(ws):
    """Ordered (path, is_project_owned) pairs. Project-owned skills rank higher."""
    pairs = [(ws / CLAUDE_DIR / "skills", True), (ws / "skills", True)]
    env = os.environ.get("DOC_MANAGER_SKILL_PATHS", "")
    for raw in env.split(os.pathsep):
        if raw.strip():
            pairs.append((Path(raw.strip()).expanduser(), False))
    home = Path.home()
    pairs += [
        (home / CLAUDE_DIR / "skills", False),
        (home / ".agents" / "skills", False),
        (home / ".gemini" / "config" / "skills", False),
    ]
    return [(p, owned) for p, owned in pairs if p.is_dir()]


def list_skills(ws):
    found = {}
    for base, owned in skill_search_paths(ws):
        for d in sorted(base.iterdir()):
            sk = d / SKILL_FILE
            if not (d.is_dir() and sk.is_file()):
                continue
            meta = parse_frontmatter(sk.read_text(encoding="utf-8", errors="replace")) or {}
            name = meta.get("name", d.name)
            if name in found:  # first search path wins
                continue
            found[name] = {
                "name": name,
                "description": meta.get("description", ""),
                "path": sk,
                "project": owned,
            }
    return list(found.values())


def detect_keywords(ws, limit=300):
    kws, seen = set(), 0
    for root, dirs, files in os.walk(ws):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]
        for f in files:
            seen += 1
            if seen > limit:
                return kws
            low = f.lower()
            kws |= FILE_KEYWORDS.get(low, set())
            kws |= EXT_KEYWORDS.get(Path(low).suffix, set())
    return kws


def score_skill(skill, kws):
    name, desc = skill["name"].lower(), skill["description"].lower()
    score, hits = 0, []
    for kw in kws:
        if re.search(r"\b" + re.escape(kw) + r"\b", name + " " + desc):
            score += 2
            hits.append(kw)
        elif len(kw) >= 4 and kw in name + " " + desc:  # avoid 'go'/'c' substring noise
            score += 1
            hits.append(kw)
    if skill["project"]:
        score += 5
        hits.append("project-owned")
    return score, hits


def normalize_path(p):
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def rel_to_ws(ws, value):
    p = Path(value)
    if p.is_absolute():
        try:
            return p.resolve().relative_to(ws.resolve()).as_posix()
        except ValueError:
            return p.as_posix()
    return normalize_path(value)


# ----------------------------------------------------------- permissions

RULE_RE = re.compile(r"^(\w+)(?:\((.*)\))?$")


def rule_matches(rule, tool, value):
    m = RULE_RE.match(rule.strip())
    if not m:
        return False
    rtool, arg = m.group(1), m.group(2)
    if rtool != tool:
        return False
    if not arg:
        return True
    if tool == "Bash":
        if arg.endswith(":*"):
            prefix = arg[:-2].strip()
            return value == prefix or value.startswith(prefix + " ")
        return value == arg.strip()
    return fnmatch.fnmatch(normalize_path(value), normalize_path(arg))


def decide(perms, tool, value):
    for bucket in ("deny", "ask", "allow"):
        if any(rule_matches(r, tool, value) for r in perms.get(bucket, [])):
            return bucket
    return "ask"  # unknown actions require confirmation


def split_shell(command):
    parts = re.split(r"&&|\|\||;|\|", command)
    return [p.strip() for p in parts if p.strip()] or [command]


def check(ws, settings, tool, value):
    perms = settings.get("permissions", {})
    values = split_shell(value) if tool == "Bash" else [value]
    decisions = []
    reasons = []
    for v in values:
        d = decide(perms, tool, v)
        decisions.append(d)
        reasons.append(f"{v!r} -> {d}")
    if tool in EDIT_TOOLS:
        rel = rel_to_ws(ws, value)
        for glob in settings.get("protected_paths", []):
            if fnmatch.fnmatch(rel, normalize_path(glob)):
                decisions.append("ask")
                reasons.append(f"{rel!r} matches protected path {glob!r}")
    final = max(decisions, key=lambda d: DECISION_RANK[d])
    return final, reasons


# ------------------------------------------------------------- commands

def cmd_init(ws, _args):
    created = []
    if not find_root(ws):
        template = Path(__file__).resolve().parent.parent / "assets" / "root_instructions_template.md"
        body = template.read_text(encoding="utf-8") if template.is_file() else "# Project Handbook\n"
        (ws / ROOT_CANDIDATES[0]).write_text(body, encoding="utf-8")
        created.append(ROOT_CANDIDATES[0])
    for sub in SUBDIRS:
        d = ws / CLAUDE_DIR / sub
        if not d.exists():
            d.mkdir(parents=True)
            created.append(f"{CLAUDE_DIR}/{sub}/")
    settings_path = ws / CLAUDE_DIR / "settings.json"
    if not settings_path.exists():
        settings_path.write_text(json.dumps(DEFAULT_SETTINGS, indent=2) + "\n", encoding="utf-8")
        created.append(f"{CLAUDE_DIR}/settings.json")
    print("created: " + (", ".join(created) if created else "nothing (already initialised)"))
    return 0


def cmd_context(ws, _args):
    """Print the full instruction bundle an agent should load at session start."""
    parts = []
    root = find_root(ws)
    if root:
        parts.append(f"# Root instructions ({root.name})\n\n{root.read_text(encoding='utf-8')}")
    else:
        parts.append("# No root instruction file. Run: doc_manager.py init")

    rules = sorted((ws / CLAUDE_DIR / "rules").glob("*.md")) if (ws / CLAUDE_DIR / "rules").is_dir() else []
    for r in rules:
        parts.append(f"## Rule: {r.name}\n\n{r.read_text(encoding='utf-8')}")

    for label, sub in (("Commands", "commands"), ("Agent roles", "agents")):
        d = ws / CLAUDE_DIR / sub
        if d.is_dir():
            items = sorted(d.glob("*.md"))
            if items:
                lines = [f"- {f.stem}: {first_line(f)}" for f in items]
                parts.append(f"## {label}\n\n" + "\n".join(lines))

    skills = list_skills(ws)
    if skills:
        # Progressive disclosure: list names and descriptions; bodies load on use.
        lines = [f"- {s['name']}: {s['description']} (file: {s['path']})" for s in skills]
        parts.append("## Available skills (read SKILL.md before using)\n\n" + "\n".join(lines))

    s = load_settings(ws)
    parts.append(
        "## Session settings\n\n"
        f"- Protected paths: {', '.join(s.get('protected_paths', [])) or 'none'}\n"
        f"- Model tiers: {json.dumps(s.get('model_tiers', {}))}\n"
        "- Permission gate: run `doc_manager.py check --tool <Tool> --input <value>` before "
        "any shell command or file edit that is not clearly routine."
    )
    print("\n\n".join(parts))
    return 0


def cmd_discover(ws, _args):
    kws = detect_keywords(ws)
    print(f"Workspace: {ws}")
    print(f"Detected keywords: {', '.join(sorted(kws)) or 'none'}")
    skills = list_skills(ws)
    if not skills:
        print("No skills found. Searched:")
        for p, _ in skill_search_paths(ws):
            print(f"  {p}")
        return 0
    ranked = []
    for s in skills:
        score, hits = score_skill(s, kws)
        if score > 0:
            ranked.append((score, s, hits))
    ranked.sort(key=lambda x: x[0], reverse=True)
    if not ranked:
        print("No skills matched this workspace. General guidance still applies.")
        return 0
    print(f"\nMatched {len(ranked)} skill(s):")
    for i, (score, s, hits) in enumerate(ranked[:15], 1):
        print(f"{i}. {s['name']} (score {score}; matched: {', '.join(hits)})")
        print(f"   {s['description']}")
        print(f"   file:///{s['path'].as_posix()}\n")
    return 0


def cmd_check(ws, args):
    settings = load_settings(ws)
    decision, reasons = check(ws, settings, args.tool, args.input)
    print(json.dumps({"decision": decision, "tool": args.tool, "input": args.input, "reasons": reasons}, indent=2))
    return DECISION_EXIT[decision]


def cmd_hook(ws, args):
    settings = load_settings(ws)
    entries = settings.get("hooks", {}).get(args.event, [])
    if not entries:
        print(f"no hooks for {args.event}")
        return 0
    payload = json.dumps({"event": args.event, "tool": args.tool, "input": args.input})
    worst = 0
    for entry in entries:
        matcher = entry.get("matcher")
        if matcher and args.tool and not re.fullmatch(matcher, args.tool):
            continue
        cmd = entry.get("command")
        if not cmd:
            continue
        env = {**os.environ, "DM_EVENT": args.event, "DM_TOOL": args.tool or "", "DM_INPUT": args.input or ""}
        r = subprocess.run(cmd, shell=True, cwd=str(ws), input=payload, text=True,
                           capture_output=True, env=env)
        print(f"[hook] {cmd} -> exit {r.returncode}")
        if r.stdout.strip():
            print(r.stdout.rstrip())
        if r.stderr.strip():
            print(r.stderr.rstrip(), file=sys.stderr)
        if r.returncode == 2:
            worst = 2  # block, matching Claude Code's convention
        elif r.returncode != 0:
            worst = max(worst, 1)
    return worst


def cmd_sources(ws, _args):
    """List the wikis and docs to read during planning for this project's stack."""
    kws = detect_keywords(ws)
    print(f"Workspace: {ws}")
    print(f"Stack keywords: {', '.join(sorted(kws)) or 'none detected'}\n")
    seen, lines = set(), []

    def add(entries, label):
        for name, url, focus in entries:
            if url in seen:
                continue
            seen.add(url)
            lines.append(f"- [{label}] {name}: {url}\n    check: {focus}")

    for kw in sorted(kws):
        add(SOURCE_MAP.get(kw, []), kw)
    if kws & WEB_KEYWORDS:
        add(WEB_SOURCES, "web")
    add(ALWAYS_SOURCES, "all")

    print("Read these during planning (use web_fetch or a browser; record what you found):")
    print("\n".join(lines))
    print("\nIf a source cannot be read, say so in the plan. Do not fill the gap from memory.")
    return 0


def cmd_tier(ws, args):
    tiers = load_settings(ws).get("model_tiers", {})
    model = tiers.get(args.tier, "")
    print(model or "current session model (no tier mapping configured)")
    return 0


def cmd_validate(ws, _args):
    problems, warnings = [], []
    root = find_root(ws)
    if not root:
        problems.append("no AGENTS.md or CLAUDE.md at workspace root")
    else:
        n = len(root.read_text(encoding="utf-8").splitlines())
        if n > ROOT_LINE_WARN:
            warnings.append(f"{root.name} is {n} lines; move detail into .claude/rules/")
    try:
        load_settings(ws)
    except SystemExit:
        problems.append(".claude/settings.json is invalid JSON")
    for sub in ("rules", "commands", "agents"):
        d = ws / CLAUDE_DIR / sub
        if d.is_dir():
            for f in d.glob("*.md"):
                if not f.read_text(encoding="utf-8").strip():
                    warnings.append(f"empty file: {f.relative_to(ws).as_posix()}")
    skills_dir = ws / CLAUDE_DIR / "skills"
    if skills_dir.is_dir():
        for d in skills_dir.iterdir():
            sk = d / SKILL_FILE
            if d.is_dir() and sk.is_file():
                meta = parse_frontmatter(sk.read_text(encoding="utf-8", errors="replace")) or {}
                for key in ("name", "description"):
                    if not meta.get(key):
                        problems.append(f"{sk.relative_to(ws).as_posix()} missing frontmatter '{key}'")
    for p in problems:
        print(f"ERROR   {p}")
    for w in warnings:
        print(f"WARN    {w}")
    if not problems and not warnings:
        print("OK      harness is valid")
    return 2 if problems else (1 if warnings else 0)


def build_parser():
    p = argparse.ArgumentParser(prog="doc_manager.py", description=__doc__.split("\n\n")[0])
    p.add_argument("--workspace", default=os.getcwd(), help="project root (default: cwd)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="scaffold the .claude/ harness without overwriting files")
    sub.add_parser("context", help="print the instruction bundle for session start")
    sub.add_parser("discover", help="rank skills against the workspace")
    sub.add_parser("validate", help="check the harness for errors")

    c = sub.add_parser("check", help="allow / ask / deny a tool use (exit 0/1/2)")
    c.add_argument("--tool", required=True, help="e.g. Bash, Edit, Write, Read")
    c.add_argument("--input", required=True, help="the command or file path")

    h = sub.add_parser("hook", help="run hooks for an event (exit 2 blocks)")
    h.add_argument("event", help="e.g. PreToolUse, PostToolUse")
    h.add_argument("--tool", default="")
    h.add_argument("--input", default="")

    sub.add_parser("sources", help="list the wikis and docs to read for this stack")

    t = sub.add_parser("tier", help="print the model mapped to a complexity tier")
    t.add_argument("tier", choices=["low", "medium", "high"])
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    ws = Path(args.workspace).expanduser().resolve()
    if not ws.is_dir():
        die(f"workspace not found: {ws}")
    handlers = {
        "init": cmd_init, "context": cmd_context, "discover": cmd_discover,
        "check": cmd_check, "hook": cmd_hook, "tier": cmd_tier, "validate": cmd_validate,
        "sources": cmd_sources,
    }
    return handlers[args.command](ws, args)


if __name__ == "__main__":
    sys.exit(main())