import os
import json
import shutil
from pathlib import Path
from typing import Dict, Tuple, List, Any
from .utils import Colors, ask_user


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    if not content.startswith('---'):
        return {}, content.strip()
    try:
        parts = content.split('---', 2)
        if len(parts) < 3: return {}, content.strip()
        frontmatter_raw = parts[1].strip()
        body = parts[2].strip()
        metadata = {}
        import yaml
        metadata = yaml.safe_load(frontmatter_raw)
        if not isinstance(metadata, dict): metadata = {}
        return metadata, body
    except:
        return {}, content

def get_glob_for_context(context_id: str) -> str:
    """Map agent/skill domain to file globs for Copilot."""
    mapping = {
        "frontend-specialist": "**/*.{ts,tsx,js,jsx,css,scss,html}",
        "frontend-design": "**/*.{ts,tsx,js,jsx,css,scss,html}",
        "backend-specialist": "**/*.{py,js,ts,go,rs,php,api,server}",
        "api-patterns": "**/*.{py,js,ts,go,rs,php,api,server}",
        "database-architect": "**/prisma/**, **/drizzle/**, **/schema/**, **/*.sql",
        "database-design": "**/prisma/**, **/drizzle/**, **/schema/**, **/*.sql",
        "test-engineer": "**/*.test.{ts,tsx,js,jsx}, **/test_*.py, **/tests/**, **/__tests__/**",
        "testing-patterns": "**/*.test.{ts,tsx,js,jsx}, **/test_*.py, **/tests/**, **/__tests__/**",
        "devops-engineer": "**/docker/**, **/ci/**, **/.github/workflows/**, Dockerfile, *.yaml, *.yml",
        "seo-specialist": "**/public/**, **/pages/**, **/metadata/**, robots.txt, sitemap.xml",
        "seo-fundamentals": "**/public/**, **/pages/**, **/metadata/**, robots.txt, sitemap.xml",
        "mobile-developer": "**/ios/**, **/android/**, **/*.{swift,kt,java}",
        "mobile-design": "**/ios/**, **/android/**, **/*.{swift,kt,java}",
        "security-auditor": "**/*.{ts,js,py,go,rs,auth}",
        "vulnerability-scanner": "**/*.{ts,js,py,go,rs,auth}",
        "clean-code": "**/*",
        "node-best-practices": "**/*.{js,ts,json}",
        "react-best-practices": "**/*.{ts,tsx,jsx,js}",
        "python-patterns": "**/*.py",
        "rust-pro": "**/*.rs",
        "bash-linux": "**/*.sh"
    }
    return mapping.get(context_id, None)

def get_master_agent_dir() -> Path:
    """Returns the .agent directory inside the agent-bridge project."""
    return Path(__file__).resolve().parent.parent.parent / ".agent"

def convert_copilot(source_dir: str, output_unused: str, force: bool = False):
    root_path = Path(source_dir).resolve()
    
    # Fallback to Master Copy if local source_dir doesn't exist
    if not root_path.exists() or not (root_path / "agents").exists():
        master_path = get_master_agent_dir()
        if master_path.exists():
            print(f"{Colors.YELLOW}🔔 Local source '{source_dir}' not found or invalid, using Master Copy: {master_path}{Colors.ENDC}")
            root_path = master_path
        else:
            print(f"{Colors.RED}❌ Error: No source tri thức found.{Colors.ENDC}")
            print(f"{Colors.YELLOW}👉 Please run 'agent-bridge update-kit' first to initialize your Master Vault from Internet.{Colors.ENDC}")
            return

    # Official GitHub Copilot directories
    github_dir = Path(".github").resolve()
    
    # Confirmation for Copilot Overwrite
    if (github_dir / "agents").exists() and not force:
        if not ask_user(f"Found existing '{github_dir}/agents'. Update Copilot agents?", default=True):
             print(f"{Colors.YELLOW}⏭️  Skipping Copilot agents update.{Colors.ENDC}")
             return

    agents_out_dir = github_dir / "agents"
    skills_out_dir = github_dir / "skills"

    print(f"{Colors.HEADER}🏗️  Converting to Official GitHub Copilot Spec...{Colors.ENDC}")

    # 1. PROCESS AGENTS -> .github/agents/<agent>.md
    agents_src_dir = root_path / "agents"
    if agents_src_dir.exists():
        if not agents_out_dir.exists(): agents_out_dir.mkdir(parents=True)
        for agent_file in agents_src_dir.glob("*.md"):
            try:
                meta, body = parse_frontmatter(agent_file.read_text(encoding='utf-8'))
                name = meta.get("name", agent_file.stem)
                desc = meta.get("description", "")
                if isinstance(desc, list): desc = " ".join(desc)
                
                glob = get_glob_for_context(agent_file.stem)
                
                lines = [
                    "---",
                    f"name: {name}",
                    f"description: {desc}"
                ]
                if glob:
                    lines.append(f"applyTo: \"{glob}\"")
                lines.append("---")
                lines.append("\n# Prompt")
                lines.append(f"\n{body}")

                with open(agents_out_dir / f"{agent_file.stem}.md", 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
                print(f"{Colors.BLUE}  🔹 Agent: {agent_file.stem}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  ❌ Failed agent {agent_file.name}: {e}{Colors.ENDC}")

    # 2. PROCESS SKILLS -> .github/skills/<skill>/SKILL.md
    skills_src_dir = root_path / "skills"
    if skills_src_dir.exists():
        if not skills_out_dir.exists(): skills_out_dir.mkdir(parents=True)
        for skill_dir in skills_src_dir.iterdir():
            if not skill_dir.is_dir(): continue
            src_skill_file = skill_dir / "SKILL.md"
            if src_skill_file.exists():
                try:
                    meta, body = parse_frontmatter(src_skill_file.read_text(encoding='utf-8'))
                    name = meta.get("name", skill_dir.name)
                    desc = meta.get("description", "")
                    if isinstance(desc, list): desc = " ".join(desc)
                    
                    # Copilot skills REQUIRE a 'usage' field in frontmatter
                    usage = meta.get("usage", f"Use this skill for {desc or name} tasks.")
                    glob = get_glob_for_context(skill_dir.name)

                    lines = [
                        "---",
                        f"name: {name}",
                        f"description: {desc or name}",
                        f"usage: \"{usage}\""
                    ]
                    if glob:
                        lines.append(f"applyTo:\n  - \"{glob}\"")
                    lines.append("---")
                    lines.append("\n# Instructions")
                    lines.append(f"\n{body}")

                    dest_dir = skills_out_dir / skill_dir.name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    with open(dest_dir / "SKILL.md", 'w', encoding='utf-8') as f:
                        f.write("\n".join(lines))
                    print(f"{Colors.BLUE}  🔸 Skill: {skill_dir.name}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}  ❌ Failed skill {skill_dir.name}: {e}{Colors.ENDC}")

    # Cleanup old non-spec files if they exist
    old_instr_file = github_dir / "copilot-instructions.md"
    if old_instr_file.exists(): old_instr_file.unlink()
    old_instr_dir = github_dir / "instructions"
    if old_instr_dir.exists():
        import shutil
        shutil.rmtree(old_instr_dir)

    print(f"{Colors.GREEN}✅ Official Copilot Spec conversion complete!{Colors.ENDC}")

def copy_mcp_copilot(root_path: Path, force: bool = False):
    """Copies MCP config to .vscode/mcp.json"""
    mcp_src = get_master_agent_dir() / "mcp_config.json"
    if not mcp_src.exists():
         mcp_src = root_path / ".agent" / "mcp_config.json"

    if mcp_src.exists():
        vscode_dir = root_path / ".vscode"
        dest_file = vscode_dir / "mcp.json"
        
        # Confirmation for MCP Overwrite (Safe Default)
        if dest_file.exists() and not force:
            if not ask_user(f"Found existing '{dest_file}'. Overwrite MCP config?", default=False):
                print(f"{Colors.YELLOW}🔒 Kept existing Copilot MCP config.{Colors.ENDC}")
                return

        try:
            import json
            import re
            
            content = mcp_src.read_text(encoding='utf-8')
            content = re.sub(r'//.*', '', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            mcp_data = json.loads(content)
            
            # Copilot stores it in .vscode/mcp.json
            vscode_dir.mkdir(parents=True, exist_ok=True)

            # User Request: "GitHub Copilot root key is wrong, it should be 'servers'"
            # Example provided: { "servers": { "MCP SERVER NAME": ... } }
            # So we format specifically for Copilot by renaming 'mcpServers' -> 'servers'
            
            final_data = {}
            if "mcpServers" in mcp_data:
                final_data["servers"] = mcp_data["mcpServers"]
            else:
                 # If source lacks mcpServers key, assume it is flat or already correct
                 final_data = mcp_data

            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4)
                
            print(f"{Colors.BLUE}  🔌 Copied to .vscode/mcp.json (Root key: 'servers'){Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}  ❌ Failed to copy MCP config to Copilot: {e}{Colors.ENDC}")
