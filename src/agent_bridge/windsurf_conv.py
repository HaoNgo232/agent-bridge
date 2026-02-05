import os
from pathlib import Path
from typing import Dict, Tuple, List, Any
from .copilot_conv import parse_frontmatter, get_master_agent_dir

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def convert_windsurf(source_dir: str, output_unused: str):
    root_path = Path(source_dir).resolve()
    
    if not root_path.exists() or not (root_path / "agents").exists():
        master_path = get_master_agent_dir()
        if master_path.exists():
            root_path = master_path
        else:
            print(f"{Colors.RED}❌ Error: No source tri thức found.{Colors.ENDC}")
            return

    windsurf_dir = Path(".windsurf/rules").resolve()
    print(f"{Colors.HEADER}🏗️  Converting to Windsurf Rules...{Colors.ENDC}")

    # Windsurf uses .windsurf/rules/ or .windsurfrules (single file)
    # We will generate a combined .windsurfrules file for legacy and individual files for modern
    
    legacy_file = Path(".windsurfrules").resolve()
    combined_content = ["# Windsurf Global Rules\n"]

    # 1. PROCESS AGENTS
    agents_src_dir = root_path / "agents"
    if agents_src_dir.exists():
        windsurf_dir.mkdir(parents=True, exist_ok=True)
        for agent_file in agents_src_dir.glob("*.md"):
            try:
                meta, body = parse_frontmatter(agent_file.read_text(encoding='utf-8'))
                desc = meta.get("description", "")
                if isinstance(desc, list): desc = " ".join(desc)
                
                # Windsurf modern format (just markdown)
                content = f"# Agent: {agent_file.stem}\n\n{body}"
                
                with open(windsurf_dir / f"{agent_file.stem}.md", 'w', encoding='utf-8') as f:
                    f.write(content)
                
                combined_content.append(f"## {agent_file.stem}\n{desc}\n{body}\n")
                print(f"{Colors.BLUE}  🔹 Rule: {agent_file.stem}.md{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  ❌ Failed windsurf rule {agent_file.name}: {e}{Colors.ENDC}")

    # 2. PROCESS SKILLS
    skills_src_dir = root_path / "skills"
    if skills_src_dir.exists():
        for skill_dir in skills_src_dir.iterdir():
            if not skill_dir.is_dir(): continue
            src_skill_file = skill_dir / "SKILL.md"
            if src_skill_file.exists():
                try:
                    meta, body = parse_frontmatter(src_skill_file.read_text(encoding='utf-8'))
                    desc = meta.get("description", "")
                    
                    content = f"# Skill: {skill_dir.name}\n\n{body}"
                    
                    with open(windsurf_dir / f"{skill_dir.name}.md", 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    combined_content.append(f"## Skill: {skill_dir.name}\n{body}\n")
                    print(f"{Colors.BLUE}  🔸 Skill: {skill_dir.name}.md{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}  ❌ Failed windsurf skill {skill_dir.name}: {e}{Colors.ENDC}")

    # Write legacy combined file
    with open(legacy_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(combined_content))
    print(f"{Colors.BLUE}  📜 Generated .windsurfrules (Legacy Combined){Colors.ENDC}")

    print(f"{Colors.GREEN}✅ Windsurf conversion complete!{Colors.ENDC}")

def copy_mcp_windsurf(root_path: Path):
    """Copies MCP config to .windsurf/mcp_config.json"""
    mcp_src = get_master_agent_dir() / "mcp_config.json"
    if not mcp_src.exists():
         mcp_src = root_path / ".agent" / "mcp_config.json"

    if mcp_src.exists():
        try:
            import json
            import re
            
            content = mcp_src.read_text(encoding='utf-8')
            content = re.sub(r'//.*', '', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            mcp_data = json.loads(content)
            
            # Windsurf stores it in .windsurf/mcp_config.json (Project local)
            # OR ~/.codeium/windsurf/mcp_config.json (Global)
            # We support project local here.
            windsurf_dir = root_path / ".windsurf"
            windsurf_dir.mkdir(parents=True, exist_ok=True)

            with open(windsurf_dir / "mcp_config.json", 'w', encoding='utf-8') as f:
                json.dump(mcp_data, f, indent=4)
                
            print(f"{Colors.BLUE}  🔌 Copied to .windsurf/mcp_config.json{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}  ❌ Failed to copy MCP config to Windsurf: {e}{Colors.ENDC}")
