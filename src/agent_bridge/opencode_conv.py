import os
from pathlib import Path
from typing import Dict, Tuple, List, Any
from .copilot_conv import parse_frontmatter, get_master_agent_dir
from .utils import Colors, ask_user

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

def convert_opencode(source_dir: str, output_unused: str, force: bool = False):
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
    
    # Confirmation for OpenCode Overwrite
    if (opencode_dir / "agents").exists() and not force:
        if not ask_user(f"Found existing '{opencode_dir}/agents'. Update OpenCode agents?", default=True):
             print(f"{Colors.YELLOW}⏭️  Skipping OpenCode agents update.{Colors.ENDC}")
             return

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
                
                # Model mapping
                raw_model = meta.get("model", "")
                oc_model = None
                if raw_model and raw_model.lower() != "inherit":
                    oc_model = raw_model
                    if "gpt-4" in raw_model.lower(): oc_model = "openai/gpt-4o"
                    elif "claude-3-sonnet" in raw_model.lower(): oc_model = "anthropic/claude-3-5-sonnet-20240620"
                    elif "claude-3-opus" in raw_model.lower(): oc_model = "anthropic/claude-3-opus-20240229"
                
                # Mode mapping
                mode = "subagent"
                if agent_file.stem == "orchestrator":
                    mode = "primary"

                # Tool mapping
                tools_meta = meta.get("tools", [])
                if isinstance(tools_meta, str): tools_meta = [t.strip() for t in tools_meta.split(",")]
                oc_tools = map_tools_to_opencode(tools_meta)

                # Build clean metadata dictionary for OpenCode
                oc_meta = {
                    "description": desc,
                    "mode": mode,
                    "tools": oc_tools
                }
                if oc_model: oc_meta["model"] = oc_model
                if meta.get("temperature") is not None: oc_meta["temperature"] = meta["temperature"]

                import yaml
                new_content = f"---\n{yaml.dump(oc_meta, sort_keys=False)}---\n{body}"

                with open(agents_out_dir / f"{agent_file.stem}.md", 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"{Colors.BLUE}  🔹 Agent: {agent_file.stem}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  ❌ Failed agent {agent_file.name}: {e}{Colors.ENDC}")

    # 2. PROCESS SKILLS -> .opencode/skills/<skill>/SKILL.md (Official OpenCode Skill Format)
    skills_src_dir = root_path / "skills"
    skills_out_dir = opencode_dir / "skills"
    if skills_src_dir.exists():
        for skill_dir in skills_src_dir.iterdir():
            if not skill_dir.is_dir(): continue
            src_skill_file = skill_dir / "SKILL.md"
            if src_skill_file.exists():
                try:
                    meta, body = parse_frontmatter(src_skill_file.read_text(encoding='utf-8'))
                    name = meta.get("name", skill_dir.name)
                    desc = meta.get("description", "")
                    if isinstance(desc, list): desc = " ".join(desc)
                    
                    # OpenCode Official Skill Frontmatter
                    # Only name, description, license, compatibility, metadata are recognized
                    oc_skill_meta = {
                        "name": name.lower().replace("_", "-"),
                        "description": desc or name
                    }

                    import yaml
                    new_content = f"---\n{yaml.dump(oc_skill_meta, sort_keys=False)}---\n{body}"

                    dest_skill_dir = skills_out_dir / skill_dir.name
                    dest_skill_dir.mkdir(parents=True, exist_ok=True)
                    with open(dest_skill_dir / "SKILL.md", 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"{Colors.BLUE}  🔸 Skill: {skill_dir.name} (Official Format){Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}  ❌ Failed skill {skill_dir.name}: {e}{Colors.ENDC}")

    # 3. GENERATE AGENTS.md (Root Level)
    # OpenCode uses AGENTS.md in project root for global project instructions
    planner_file = agents_src_dir / "project-planner.md"
    if planner_file.exists():
        try:
            _, body = parse_frontmatter(planner_file.read_text(encoding='utf-8'))
            with open(Path("AGENTS.md"), 'w', encoding='utf-8') as f:
                f.write(f"# Project Instructions\n\n{body}")
            print(f"{Colors.BLUE}  📜 Generated AGENTS.md (Project Root){Colors.ENDC}")
        except: pass

    # 4. ENRICH ORCHESTRATOR WITH TASK & SKILL PERMISSIONS
    # In OpenCode, a primary agent needs explicit permission to call subagents via 'task' and load skills via 'skill'
    orchestrator_out = agents_out_dir / "orchestrator.md"
    if orchestrator_out.exists():
        try:
            # Collect all other agent names
            subagent_names = [f.stem for f in agents_out_dir.glob("*.md") if f.stem != "orchestrator"]
            
            # CLEANUP: If a subagent name also exists as a native skill, remove it from agents folder
            # to avoid duplication and use official skill tool instead.
            for name in list(subagent_names):
                if (skills_out_dir / name).exists():
                    old_agent_file = agents_out_dir / f"{name}.md"
                    if old_agent_file.exists():
                        old_agent_file.unlink()
                        subagent_names.remove(name)
                        print(f"{Colors.YELLOW}  🧹 Removed legacy skill-agent: {name}.md (Replaced by Official Skill){Colors.ENDC}")

            meta, body = parse_frontmatter(orchestrator_out.read_text(encoding='utf-8'))
            
            # Ensure meta is a dict
            if not isinstance(meta, dict): meta = {}
            
            # Update permissions for the custom orchestrator
            if "permission" not in meta: meta["permission"] = {}
            meta["permission"]["task"] = subagent_names
            meta["permission"]["skill"] = {"*": "allow"}
            
            if "tools" not in meta: meta["tools"] = {}
            meta["tools"]["skill"] = True
            
            # Reconstruct frontmatter
            import yaml
            new_content = f"---\n{yaml.dump(meta, sort_keys=False)}---\n{body}"
            orchestrator_out.write_text(new_content, encoding='utf-8')
            print(f"{Colors.GREEN}  ✅ Orchestrator enriched with Task & Skill permissions.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}  ⚠️ Could not enrich orchestrator permissions: {e}{Colors.ENDC}")

    # 5. GENERATE opencode.json (Global Configuration)
    opencode_json_path = opencode_dir / "opencode.json"
    try:
        import json
        config = {
            "permission": {
                "skill": {
                    "*": "allow"
                }
            },
            "agent": {
                "plan": {
                    "permission": {
                        "skill": {
                            "*": "allow"
                        }
                    }
                }
            }
        }
        with open(opencode_json_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"{Colors.BLUE}  📂 Generated opencode.json (Global Config){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}  ❌ Failed to generate opencode.json: {e}{Colors.ENDC}")

    print(f"{Colors.GREEN}✅ OpenCode conversion complete!{Colors.ENDC}")

def copy_mcp_opencode(root_path: Path, force: bool = False):
    """Copies MCP config to .opencode/mcp.json"""
    mcp_src = get_master_agent_dir() / "mcp_config.json"
    if not mcp_src.exists():
         mcp_src = root_path / ".agent" / "mcp_config.json"

    if mcp_src.exists():
        opencode_dir = root_path / ".opencode"
        dest_file = opencode_dir / "mcp.json"
        
        # Confirmation for MCP Overwrite (Safe Default)
        if dest_file.exists() and not force:
            if not ask_user(f"Found existing '{dest_file}'. Overwrite MCP config?", default=False):
                print(f"{Colors.YELLOW}🔒 Kept existing OpenCode MCP config.{Colors.ENDC}")
                return

        try:
            import json
            import re
            
            content = mcp_src.read_text(encoding='utf-8')
            content = re.sub(r'//.*', '', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            mcp_data = json.loads(content)
            
            # OpenCode uses ".opencode/mcp.json" (as we decided for manual import) or opencode.json
            # Format: { "$schema": "...", "mcp": { "server": { "type": "local", "command": ..., "enabled": true } } }
            # Our source data has "mcpServers" key. We'll map it to "mcp" key.
            
            opencode_data = {
                "$schema": "https://opencode.ai/config.json",
                "mcp": {}
            }
            
            source_servers = mcp_data.get("mcpServers", {})
            for name, config in source_servers.items():
                new_config = config.copy()
                
                # Enhanced for OpenCode
                if "type" not in new_config:
                    new_config["type"] = "local" # Default to local stdio
                if "enabled" not in new_config:
                    new_config["enabled"] = True
                
                # OpenCode Schema Fix: "command" must be an array of strings, "args" is forbidden.
                # If we have "command" as string and "args" as list, merge them.
                if "command" in new_config and isinstance(new_config["command"], str):
                    base_cmd = new_config["command"]
                    args = new_config.get("args", [])
                    # Merge into single list
                    new_config["command"] = [base_cmd] + args
                    # Remove args if present
                    if "args" in new_config:
                        del new_config["args"]
                        
                opencode_data["mcp"][name] = new_config

            opencode_dir.mkdir(parents=True, exist_ok=True)

            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(opencode_data, f, indent=4)
                
            print(f"{Colors.BLUE}  🔌 Copied to .opencode/mcp.json (Wrapped in 'mcp' key + schema fix){Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}  ❌ Failed to copy MCP config to OpenCode: {e}{Colors.ENDC}")
