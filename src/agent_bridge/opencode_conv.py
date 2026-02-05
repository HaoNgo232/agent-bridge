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

def map_tools_to_opencode(tools: List[str]) -> Dict[str, bool]:
    """Map Antigravity tools to OpenCode tool permissions."""
    mapping = {
        "bash": "bash",
        "terminal": "bash",
        "shell": "bash",
        "edit": "write",
        "write": "write",
        "replace_file_content": "write",
        "multi_replace_file_content": "write",
        "read_file": "read",
        "web": "webfetch",
        "search": "webfetch"
    }
    
    opencode_tools = {}
    for t in tools:
        oc_tool = mapping.get(t.lower())
        if oc_tool:
            opencode_tools[oc_tool] = True
            
    # Default permissions if not specified
    if not opencode_tools:
        opencode_tools = {"bash": True, "write": True, "read": True, "webfetch": True}
        
    return opencode_tools

def convert_opencode(source_dir: str, output_unused: str):
    root_path = Path(source_dir).resolve()
    
    # Fallback to Master Copy if local source_dir doesn't exist
    if not root_path.exists() or not (root_path / "agents").exists():
        master_path = get_master_agent_dir()
        if master_path.exists():
            print(f"{Colors.YELLOW}🔔 Local source '{source_dir}' not found or invalid, using Master Copy: {master_path}{Colors.ENDC}")
            root_path = master_path
        else:
            print(f"{Colors.RED}❌ Error: No source tri thức found.{Colors.ENDC}")
            print(f"{Colors.YELLOW}👉 Please run 'agent-bridge update' first to initialize your Master Vault from Internet.{Colors.ENDC}")
            return

    # OpenCode directory
    opencode_dir = Path(".opencode").resolve()
    agents_out_dir = opencode_dir / "agents"

    print(f"{Colors.HEADER}🏗️  Converting to OpenCode Format...{Colors.ENDC}")

    # 1. PROCESS AGENTS -> .opencode/agents/<agent>.md
    agents_src_dir = root_path / "agents"
    if agents_src_dir.exists():
        if not agents_out_dir.exists(): agents_out_dir.mkdir(parents=True)
        for agent_file in agents_src_dir.glob("*.md"):
            try:
                meta, body = parse_frontmatter(agent_file.read_text(encoding='utf-8'))
                name = meta.get("name", agent_file.stem)
                desc = meta.get("description", "")
                if isinstance(desc, list): desc = " ".join(desc)
                
                # Model mapping (OpenCode uses provider/model syntax)
                raw_model = meta.get("model", "")
                oc_model = None
                if raw_model and raw_model.lower() != "inherit":
                    oc_model = raw_model
                    if "gpt-4" in raw_model.lower(): oc_model = "openai/gpt-4o"
                    elif "claude-3-sonnet" in raw_model.lower(): oc_model = "anthropic/claude-3-5-sonnet-20240620"
                    elif "claude-3-opus" in raw_model.lower(): oc_model = "anthropic/claude-3-opus-20240229"
                
                # Temperature
                temp = meta.get("temperature", None)

                # Mode mapping
                mode = "subagent"
                if agent_file.stem == "orchestrator":
                    mode = "primary"

                # Tool mapping
                tools_meta = meta.get("tools", [])
                if isinstance(tools_meta, str): tools_meta = [t.strip() for t in tools_meta.split(",")]
                oc_tools = map_tools_to_opencode(tools_meta)

                lines = ["---"]
                lines.append(f"description: \"{desc}\"")
                lines.append(f"mode: {mode}")
                if oc_model:
                    lines.append(f"model: {oc_model}")
                if temp is not None:
                    lines.append(f"temperature: {temp}")
                
                # Tools YAML block
                lines.append("tools:")
                for tool, allowed in oc_tools.items():
                    lines.append(f"  {tool}: {str(allowed).lower()}")
                
                lines.append("---")
                lines.append(f"\n{body}")

                with open(agents_out_dir / f"{agent_file.stem}.md", 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
                print(f"{Colors.BLUE}  🔹 Agent: {agent_file.stem}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  ❌ Failed agent {agent_file.name}: {e}{Colors.ENDC}")

    # 2. PROCESS SKILLS -> .opencode/agents/<skill>.md (As subagents)
    skills_src_dir = root_path / "skills"
    if skills_src_dir.exists():
        if not agents_out_dir.exists(): agents_out_dir.mkdir(parents=True)
        for skill_dir in skills_src_dir.iterdir():
            if not skill_dir.is_dir(): continue
            src_skill_file = skill_dir / "SKILL.md"
            if src_skill_file.exists():
                try:
                    meta, body = parse_frontmatter(src_skill_file.read_text(encoding='utf-8'))
                    name = meta.get("name", skill_dir.name)
                    desc = meta.get("description", "")
                    if isinstance(desc, list): desc = " ".join(desc)
                    
                    # OpenCode specific mapping for skills (always subagents)
                    mode = "subagent"
                    
                    # Tool mapping
                    tools_meta = meta.get("tools", [])
                    if isinstance(tools_meta, str): tools_meta = [t.strip() for t in tools_meta.split(",")]
                    oc_tools = map_tools_to_opencode(tools_meta)

                    lines = ["---"]
                    lines.append(f"description: \"{desc or name}\"")
                    lines.append(f"mode: {mode}")
                    
                    # Tools YAML block
                    lines.append("tools:")
                    for tool, allowed in oc_tools.items():
                        lines.append(f"  {tool}: {str(allowed).lower()}")
                    
                    lines.append("---")
                    lines.append(f"\n{body}")

                    # Use skill directory name as the agent file name
                    with open(agents_out_dir / f"{skill_dir.name}.md", 'w', encoding='utf-8') as f:
                        f.write("\n".join(lines))
                    print(f"{Colors.BLUE}  🔸 Skill: {skill_dir.name}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}  ❌ Failed skill {skill_dir.name}: {e}{Colors.ENDC}")

    # 3. GENERATE AGENTS.md (Root Level)
    # OpenCode uses AGENTS.md in project root for global project instructions
    # We can use the project-planner or orchestrator prompt as a base for this if it exists
    planner_file = agents_src_dir / "project-planner.md"
    if planner_file.exists():
        try:
            _, body = parse_frontmatter(planner_file.read_text(encoding='utf-8'))
            with open(Path("AGENTS.md"), 'w', encoding='utf-8') as f:
                f.write(f"# Project Instructions\n\n{body}")
            print(f"{Colors.BLUE}  📜 Generated AGENTS.md (Project Root){Colors.ENDC}")
        except: pass

    print(f"{Colors.GREEN}✅ OpenCode conversion complete!{Colors.ENDC}")
