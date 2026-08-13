import os
import sys
import re

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def detect_project_keywords(workspace_dir):
    keywords = set()
    
    root_files = []
    try:
        root_files = os.listdir(workspace_dir)
    except Exception as e:
        print(f"Error reading workspace directory {workspace_dir}: {e}", file=sys.stderr)
        return keywords

    file_mapping = {
        'package.json': {'javascript', 'node', 'npm', 'yarn'},
        'tsconfig.json': {'typescript', 'ts'},
        'requirements.txt': {'python', 'pip'},
        'pyproject.toml': {'python', 'poetry', 'uv'},
        'Pipfile': {'python', 'pipenv'},
        'setup.py': {'python'},
        'Cargo.toml': {'rust', 'cargo'},
        'go.mod': {'go', 'golang'},
        'CMakeLists.txt': {'c++', 'cpp', 'cmake'},
        'Makefile': {'make'},
        'Dockerfile': {'docker', 'container'},
        'docker-compose.yml': {'docker', 'container'},
        'firebase.json': {'firebase', 'firestore', 'hosting'},
        'angular.json': {'angular'},
        'next.config.js': {'next.js', 'nextjs', 'react'},
        'next.config.mjs': {'next.js', 'nextjs', 'react'},
        'tailwind.config.js': {'tailwind'},
        'tailwind.config.ts': {'tailwind'},
        'vite.config.js': {'vite', 'react', 'vue'},
        'vite.config.ts': {'vite', 'react', 'vue'},
        'svelte.config.js': {'svelte'},
        'dag': {'airflow'},
    }

    for filename in root_files:
        lowered = filename.lower()
        if lowered in file_mapping:
            keywords.update(file_mapping[lowered])
        
        _, ext = os.path.splitext(lowered)
        if ext == '.py':
            keywords.add('python')
        elif ext in ('.js', '.jsx'):
            keywords.update(['javascript', 'react'])
        elif ext in ('.ts', '.tsx'):
            keywords.update(['typescript', 'react'])
        elif ext == '.rs':
            keywords.add('rust')
        elif ext == '.go':
            keywords.add('go')
        elif ext in ('.cpp', '.hpp', '.cc', '.h'):
            keywords.update(['c++', 'cpp'])
        elif ext == '.c':
            keywords.add('c')
        elif ext == '.sql':
            keywords.update(['sql', 'database', 'postgres', 'mysql', 'sqlite'])
        elif ext in ('.yaml', '.yml'):
            if 'k8s' in lowered or 'kubernetes' in lowered or 'deploy' in lowered:
                keywords.update(['kubernetes', 'k8s', 'yaml'])

    file_count = 0
    for root, dirs, files in os.walk(workspace_dir):
        for d in list(dirs):
            if d.startswith('.') or d in ('node_modules', 'venv', 'env', '__pycache__', 'target', 'build', 'dist', 'out'):
                dirs.remove(d)
        
        for f in files:
            file_count += 1
            if file_count > 300:
                break
            lowered = f.lower()
            _, ext = os.path.splitext(lowered)
            if ext == '.py':
                keywords.add('python')
            elif ext in ('.js', '.jsx'):
                keywords.update(['javascript', 'react'])
            elif ext in ('.ts', '.tsx'):
                keywords.update(['typescript', 'react'])
            elif ext == '.rs':
                keywords.add('rust')
            elif ext == '.go':
                keywords.add('go')
            elif ext in ('.cpp', '.hpp', '.cc', '.h'):
                keywords.update(['c++', 'cpp'])
            elif ext == '.sql':
                keywords.update(['sql', 'database'])
            elif ext == '.sol':
                keywords.update(['solidity', 'ethereum', 'smart contract', 'web3'])
            elif ext == '.tf':
                keywords.update(['terraform', 'infrastructure', 'iac'])

        if file_count > 300:
            break

    return keywords

def parse_skill(skill_dir):
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_md_path):
        return None
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None
    
    frontmatter_text = match.group(1)
    metadata = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            metadata[key.strip().lower()] = val.strip()
            
    name = metadata.get('name', os.path.basename(skill_dir))
    description = metadata.get('description', '')
    return {
        'name': name,
        'description': description,
        'path': skill_md_path,
        'dir_name': os.path.basename(skill_dir)
    }

def find_matching_skills(skills_parent_dir, project_keywords):
    matched_skills = []
    
    if not os.path.exists(skills_parent_dir):
        return []

    for entry in os.listdir(skills_parent_dir):
        entry_path = os.path.join(skills_parent_dir, entry)
        if os.path.isdir(entry_path):
            skill_info = parse_skill(entry_path)
            if not skill_info:
                continue
            
            score = 0
            matching_keywords = []
            
            name_lower = skill_info['name'].lower()
            desc_lower = skill_info['description'].lower()
            
            for kw in project_keywords:
                pattern = re.compile(r'\b' + re.escape(kw) + r'\b')
                if pattern.search(name_lower) or pattern.search(desc_lower):
                    score += 2
                    matching_keywords.append(kw)
                elif kw in name_lower or kw in desc_lower:
                    score += 1
                    matching_keywords.append(kw)

            web_techs = {'javascript', 'typescript', 'react', 'next.js', 'nextjs', 'tailwind', 'vite', 'html', 'css', 'vue', 'svelte', 'web', 'node'}
            top_web_skills = (
                'emil-design-eng', 'animate', 'review-animations', 'improve-animations', 'apple-design',
                'shadcn-ui', 'awesome-react', 'front-end-checklist', 'developer-roadmap',
                'front-end-interview-handbook', 'you-dont-know-js', '30-seconds-of-code',
                'app-ideas', '50projects50days', 'web-dev-for-beginners'
            )
            if skill_info['dir_name'] in top_web_skills:
                if project_keywords.intersection(web_techs) or not project_keywords:
                    score += 20
                    matching_keywords.append('primary web dev engineering skill')

            if skill_info['dir_name'] in ('claude-mem', 'mem-search', 'learn-codebase', 'smart-explore', 'pathfinder', 'knowledge-agent'):
                score += 15
                matching_keywords.append('primary persistent memory skill')

            if skill_info['dir_name'] in ('Essential_Skill', 'Basic_skills', 'debugger', 'dx-optimizer', 'error-detective'):
                score += 1
                matching_keywords.append('general utility')
            
            if score > 0:
                skill_info['score'] = score
                skill_info['matched_by'] = list(set(matching_keywords))
                matched_skills.append(skill_info)
                
    matched_skills.sort(key=lambda x: x['score'], reverse=True)
    return matched_skills

def main():
    workspace = os.getcwd()
    if len(sys.argv) > 1:
        workspace = os.path.abspath(sys.argv[1])
        
    print(f"Scanning workspace: {workspace}")
    keywords = detect_project_keywords(workspace)
    print(f"Detected project keywords/technologies: {', '.join(sorted(keywords)) if keywords else 'None'}")
    print(f"Searching skills in: {SKILLS_DIR}")
    
    matches = find_matching_skills(SKILLS_DIR, keywords)
    
    if not matches:
        print("\nNo matching domain-specific skills found. Recommended to use basic/general utility skills:")
        basic_skills = ['Essential_Skill', 'Basic_skills', 'debugger', 'dx-optimizer']
        for b in basic_skills:
            bp = os.path.join(SKILLS_DIR, b)
            info = parse_skill(bp)
            if info:
                print(f"- {info['name']}: {info['description']}")
    else:
        print(f"\nFound {len(matches)} matching skills for your project:")
        for idx, m in enumerate(matches[:15], 1):
            print(f"{idx}. {m['name']} (matched: {', '.join(m['matched_by'])})")
            print(f"   Description: {m['description']}")
            print(f"   Path: file:///{m['path'].replace(os.sep, '/')}")
            print()

if __name__ == '__main__':
    main()
