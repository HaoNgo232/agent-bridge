import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from .utils import Colors, get_master_agent_dir

def check_and_refresh_project(source_dir: str):
    """Detects existing formats and refreshes them."""
    # We import here to avoid circular imports if any
    from .copilot_conv import convert_copilot
    from .kiro_conv import convert_kiro
    from .opencode_conv import convert_opencode

    cwd = Path.cwd()
    
    # Check for Copilot
    if (cwd / ".github" / "agents").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing Copilot Spec...{Colors.ENDC}")
        convert_copilot(source_dir, "")
        
    # Check for Kiro
    if (cwd / ".kiro" / "agents").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing Kiro Format...{Colors.ENDC}")
        convert_kiro(source_dir, ".kiro")
        
    # Check for OpenCode
    if (cwd / ".opencode" / "agents").exists() or (cwd / "AGENTS.md").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing OpenCode Format...{Colors.ENDC}")
        convert_opencode(source_dir, "")

KIT_REPO_URL = "https://github.com/vudovn/antigravity-kit"

def update_kit(target_dir: str):
    target_path = Path(target_dir).resolve()
    
    # Check if target_dir is local .agent and if it exists
    # If it doesn't exist and we're not in a kit project, we might want to update master
    master_path = get_master_agent_dir()
    
    if not Path(target_dir).exists() and not Path(".git").exists():
         print(f"{Colors.YELLOW}🔔 Local .agent not found, updating Master Copy instead...{Colors.ENDC}")
         target_path = master_path

    print(f"{Colors.HEADER}🔄 Updating Antigravity Kit to: {target_path}{Colors.ENDC}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        try:
            print(f"{Colors.BLUE}  📥 Cloning repository...{Colors.ENDC}")
            subprocess.run(["git", "clone", "--depth", "1", KIT_REPO_URL, str(tmp_path)], check=True, capture_output=True)
            
            repo_agent_dir = tmp_path / ".agent"
            if not repo_agent_dir.exists():
                # Try root if .agent folder doesn't exist (depending on repo structure)
                repo_agent_dir = tmp_path

            print(f"{Colors.BLUE}  📂 Syncing agents and skills...{Colors.ENDC}")
            
            for sub in ["agents", "skills", "workflows"]:
                src = repo_agent_dir / sub
                dst = target_path / sub
                
                if src.exists():
                    if not dst.exists():
                        dst.mkdir(parents=True)
                    
                    # Merge content
                    for item in src.iterdir():
                        dest_item = dst / item.name
                        if item.is_dir():
                            if dest_item.exists():
                                shutil.rmtree(dest_item)
                            shutil.copytree(item, dest_item)
                        else:
                            shutil.copy2(item, dest_item)
                    print(f"{Colors.GREEN}    ✅ Sync {sub} complete.{Colors.ENDC}")

            # Sync Global Configs (including MCP)
            for config_file in ["mcp_config.json"]:
                src_conf = repo_agent_dir / config_file
                dst_conf = target_path / config_file
                
                if src_conf.exists():
                    if not dst_conf.exists():
                        shutil.copy2(src_conf, dst_conf)
                        print(f"{Colors.GREEN}    ✅ Init {config_file} from Kit.{Colors.ENDC}")
                    else:
                        print(f"{Colors.YELLOW}    🔒 Kept local {config_file} (User Override).{Colors.ENDC}")

            print(f"{Colors.GREEN}✨ Antigravity Kit is now up to date!{Colors.ENDC}")
            
            # Smart Refresh
            check_and_refresh_project(str(target_path))

        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Failed to clone repository: {e.stderr.decode()}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error during sync: {e}{Colors.ENDC}")
