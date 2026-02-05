import os
import json
from pathlib import Path
from typing import Dict, Tuple, List, Any

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    if not content.startswith('---'):
        return {}, content.strip()
    try:
        parts = content.split('---', 2)
        if len(parts) < 3: return {}, content.strip()
        frontmatter_raw = parts[1].strip()
        body = parts[2].strip()
        metadata = {}
        for line in frontmatter_raw.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
                if ',' in value:
                    metadata[key] = [v.strip() for v in value.split(',')]
                else:
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    metadata[key] = value
        return metadata, body
    except:
        return {}, content

def get_master_agent_dir() -> Path:
    """Returns the .agent directory inside the agent-bridge project."""
    # File is in src/agent_bridge/kiro_conv.py
    return Path(__file__).resolve().parent.parent.parent / ".agent"

def convert_kiro(source_dir: str, output_dir: str):
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

    base_dir = Path(output_dir).resolve()
    
    if not base_dir.exists(): base_dir.mkdir(parents=True)

    print(f"{Colors.HEADER}🏗️  Converting to Kiro Format...{Colors.ENDC}")

    # Process Agents
    agents_dir = root_path / "agents"
    kiro_agents_dir = base_dir / "agents"
    if not kiro_agents_dir.exists(): kiro_agents_dir.mkdir(parents=True)

    haiku_agents = ["documentation-writer", "seo-specialist", "explorer-agent", "product-owner", "product-manager", "code-archaeologist"]

    for file_path in agents_dir.glob("*.md"):
        try:
            content = file_path.read_text(encoding='utf-8')
            meta, body = parse_frontmatter(content)
            description = meta.get("description", "")
            if isinstance(description, list): description = " ".join(description)

            # Map tools
            raw_tools = meta.get("tools", [])
            tool_map = {"bash": "shell", "terminal": "shell", "edit": "write", "replace_file_content": "write", "multi_replace_file_content": "write", "create_file": "write", "write_to_file": "write"}
            kiro_tools = list(dict.fromkeys([tool_map.get(t.lower(), t.lower()) for t in raw_tools]))

            # Map skills
            agent_skills = meta.get("skills", [])
            resources = [f"skill://{output_dir}/skills/{s}/SKILL.md" for s in agent_skills]

            agent_data = {
                "name": meta.get("name", file_path.stem),
                "description": description,
                "prompt": body,
                "tools": kiro_tools
            }
            if resources: agent_data["resources"] = resources

            # Smart model selection
            model_val = meta.get("model", "")
            if file_path.stem in haiku_agents:
                agent_data["model"] = "claude-haiku-4.5"
            elif model_val and model_val.lower() != "inherit":
                agent_data["model"] = model_val

            with open(kiro_agents_dir / f"{file_path.stem}.json", 'w', encoding='utf-8') as f:
                json.dump(agent_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{Colors.RED}❌ Failed agent {file_path.name}: {e}{Colors.ENDC}")

    # Process Skills
    skills_dir = root_path / "skills"
    kiro_skills_dir = base_dir / "skills"
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir(): continue
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            dest_dir = kiro_skills_dir / skill_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / "SKILL.md"
            with open(skill_file, 'r', encoding='utf-8') as src, open(dest_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

    # Process Workflows
    workflows_dir = root_path / "workflows"
    steering_dir = base_dir / "steering"
    if workflows_dir.exists():
        steering_dir.mkdir(parents=True, exist_ok=True)
        for wf_file in workflows_dir.glob("*.md"):
            try:
                meta, body = parse_frontmatter(wf_file.read_text(encoding='utf-8'))
                with open(steering_dir / f"{wf_file.stem}.md", 'w', encoding='utf-8') as f:
                    f.write(f"# Workflow: /{wf_file.stem}\n\n{meta.get('description', '')}\n\n{body}")
            except: pass

    print(f"{Colors.GREEN}✅ Kiro conversion complete!{Colors.ENDC}")

def copy_mcp_kiro(root_path: Path):
    """Copies MCP config to .kiro/settings/mcp.json"""
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
            
            # Kiro expects .kiro/settings/mcp.json
            kiro_settings_dir = root_path / ".kiro" / "settings"
            kiro_settings_dir.mkdir(parents=True, exist_ok=True)

            with open(kiro_settings_dir / "mcp.json", 'w', encoding='utf-8') as f:
                json.dump(mcp_data, f, indent=4)
                
            print(f"{Colors.BLUE}  🔌 Copied to .kiro/settings/mcp.json{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}  ❌ Failed to copy MCP config to Kiro: {e}{Colors.ENDC}")
