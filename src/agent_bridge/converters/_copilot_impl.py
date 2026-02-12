"""
Implementation logic cho GitHub Copilot converter.

Tach rieng de converters/copilot.py chi chua BaseConverter wrapper.
"""

import re
import shutil
from pathlib import Path
from typing import Any, Dict, List

import yaml

from agent_bridge.core.agent_registry import get_agent_role as _get_role
from agent_bridge.core.types import CapturedFile


def _role_to_copilot_tools(slug: str) -> list[str]:
    """Derive Copilot tool list from central AgentRole capabilities."""
    role = _get_role(slug)
    if not role:
        return ["search/codebase", "edit/editFiles", "web/fetch"]

    tools = []
    if role.can_search:
        tools.append("search/codebase")
        tools.append("search/usages")
    if role.can_write:
        tools.append("edit/editFiles")
    if role.can_read:
        tools.append("web/fetch")
    if role.can_execute:
        tools.append("read/terminalLastCommand")
    if role.slug in ("project-planner",):
        if "web/githubRepo" not in tools:
            tools.append("web/githubRepo")
    return tools if tools else ["search/codebase", "edit/editFiles", "web/fetch"]


AGENT_SUBAGENTS_MAP = {
    "orchestrator": ["*"],
    "project-planner": ["*"],
    "debugger": ["backend-specialist", "frontend-specialist", "test-engineer"],
}

AGENT_HANDOFFS_MAP = {
    "project-planner": [
        {"label": "Start Implementation", "agent": "orchestrator", "prompt": "Implement the plan outlined above following the task breakdown.", "send": False},
        {"label": "Security Review", "agent": "security-auditor", "prompt": "Review the security aspects of this implementation plan.", "send": False},
    ],
    "orchestrator": [
        {"label": "Frontend Tasks", "agent": "frontend-specialist", "prompt": "Implement the frontend components as specified.", "send": False},
        {"label": "Backend Tasks", "agent": "backend-specialist", "prompt": "Implement the backend services as specified.", "send": False},
        {"label": "Database Setup", "agent": "database-architect", "prompt": "Design and implement the database schema.", "send": False},
        {"label": "Write Tests", "agent": "test-engineer", "prompt": "Write tests for the implemented features.", "send": False},
    ],
    "explorer-agent": [{"label": "Create Plan", "agent": "project-planner", "prompt": "Create an implementation plan based on this codebase analysis.", "send": False}],
    "security-auditor": [{"label": "Fix Security Issues", "agent": "backend-specialist", "prompt": "Fix the security vulnerabilities identified in the audit.", "send": False}],
    "test-engineer": [{"label": "Fix Failing Tests", "agent": "backend-specialist", "prompt": "Fix the code to make the failing tests pass.", "send": False}],
    "debugger": [{"label": "Implement Fix", "agent": "backend-specialist", "prompt": "Implement the fix for the identified bug.", "send": False}],
}

_RE_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_RE_H1_NAME = re.compile(r"^#\s+(.+?)(?:\s*[-–—]\s*(.+))?$", re.MULTILINE)
_RE_ROLE_PATTERNS = [
    re.compile(r"(?:You are|Role:|##\s*Role)[:\s]*(.+?)(?:\n\n|\n##|\n#\s)", re.IGNORECASE | re.DOTALL),
    re.compile(r"(?:Purpose|Mission)[:\s]*(.+?)(?:\n\n|\n##)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^>\s*(.+?)$", re.MULTILINE),
]
_RE_SKILL_PATTERNS = [
    re.compile(r"skills?[:\s]+\[([^\]]+)\]", re.IGNORECASE),
    re.compile(r"`([a-z][a-z0-9\-]+)`\s*skill", re.IGNORECASE),
    re.compile(r"uses?\s+(?:the\s+)?`([a-z][a-z0-9\-]+)`", re.IGNORECASE),
]


def extract_agent_metadata(content: str, filename: str) -> Dict[str, Any]:
    """Extract metadata from agent markdown content."""
    metadata = {"name": "", "description": "", "role": "", "skills": []}
    fm_match = _RE_FRONTMATTER.match(content)
    if fm_match:
        try:
            existing = yaml.safe_load(fm_match.group(1))
            if existing:
                for key, value in existing.items():
                    if key in ["skills", "tools"] and isinstance(value, str):
                        metadata[key] = [s.strip() for s in value.split(",")]
                    else:
                        metadata[key] = value
        except yaml.YAMLError:
            pass
    name_match = _RE_H1_NAME.search(content)
    if name_match:
        metadata["name"] = name_match.group(1).strip()
        if name_match.group(2) and not metadata.get("description"):
            metadata["description"] = name_match.group(2).strip()
    if not metadata["name"]:
        metadata["name"] = filename.replace(".md", "").replace("-", " ").title()
    for pattern in _RE_ROLE_PATTERNS:
        role_match = pattern.search(content)
        if role_match and not metadata.get("role"):
            metadata["role"] = role_match.group(1).strip()[:300]
            break
    for pattern in _RE_SKILL_PATTERNS:
        for match in pattern.finditer(content):
            skills_str = match.group(1)
            for skill in re.split(r"[,\s]+", skills_str):
                skill = skill.strip().strip("`\"'")
                if skill and skill not in metadata["skills"]:
                    metadata["skills"].append(skill)
    return metadata


def generate_copilot_frontmatter(agent_slug: str, metadata: Dict[str, Any]) -> str:
    """Generate YAML frontmatter for Copilot agent profile."""
    frontmatter: Dict[str, Any] = {}
    frontmatter["name"] = metadata.get("name") or agent_slug.replace("-", " ").title()
    description = metadata.get("description") or metadata.get("role", "")
    if not description:
        description = f"Specialized agent for {agent_slug.replace('-', ' ')} tasks"
    frontmatter["description"] = description[:500] if len(description) > 500 else description
    tools = _role_to_copilot_tools(agent_slug)
    subagents = AGENT_SUBAGENTS_MAP.get(agent_slug)
    if subagents:
        if "agent" not in tools:
            tools = [*tools, "agent"]
        frontmatter["agents"] = subagents
    frontmatter["tools"] = tools
    handoffs = AGENT_HANDOFFS_MAP.get(agent_slug)
    if handoffs:
        frontmatter["handoffs"] = handoffs
    if agent_slug in ["code-archaeologist"]:
        frontmatter["user-invokable"] = False
    return yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)


def convert_agent_to_copilot(source_path: Path, dest_path: Path) -> bool:
    """Convert a single agent file to Copilot format with full frontmatter."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()
        metadata = extract_agent_metadata(content, source_path.name)
        frontmatter = generate_copilot_frontmatter(agent_slug, metadata)
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)
        COPILOT_PROMPT_MAX_CHARS = 30000
        body = content_clean.strip()
        if len(body) > COPILOT_PROMPT_MAX_CHARS:
            truncate_suffix = "\n\n... (truncated to fit Copilot 30K char limit)\n"
            body = body[: COPILOT_PROMPT_MAX_CHARS - len(truncate_suffix)] + truncate_suffix
        output = f"---\n{frontmatter}---\n\n{body}\n"
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_skill_to_copilot(source_dir: Path, dest_dir: Path) -> bool:
    """Convert skill directory to Copilot Agent Skills format."""
    try:
        skill_name = source_dir.name
        dest_skill_dir = dest_dir / skill_name
        dest_skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = source_dir / "SKILL.md"
        if not skill_file.exists():
            md_files = list(source_dir.glob("*.md"))
            skill_file = md_files[0] if md_files else None
        if skill_file and skill_file.exists():
            content = skill_file.read_text(encoding="utf-8")
            existing_meta = {}
            frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
            if frontmatter_match:
                try:
                    existing_meta = yaml.safe_load(frontmatter_match.group(1)) or {}
                    content = content[frontmatter_match.end():]
                except yaml.YAMLError:
                    pass
            normalized_name = existing_meta.get("name") or skill_name
            normalized_name = re.sub(r"[^a-z0-9-]", "-", normalized_name.lower())
            normalized_name = re.sub(r"-+", "-", normalized_name).strip("-")
            if len(normalized_name) > 64:
                normalized_name = normalized_name[:64].rstrip("-")
            skill_description = existing_meta.get("description")
            if not skill_description:
                desc_match = re.search(r"^(?:>|Description:|Purpose:)\s*(.+?)$", content, re.MULTILINE | re.IGNORECASE)
                skill_description = desc_match.group(1).strip() if desc_match else f"Skill for {skill_name.replace('-', ' ')}. Use when working with related tasks."
            if len(skill_description) > 1024:
                skill_description = skill_description[:1021] + "..."
            if not normalized_name or not skill_description:
                print(f"  Skill {skill_name}: missing required fields (name or description)")
                return False
            frontmatter = {"name": normalized_name, "description": skill_description}
            SKIP_FIELDS = {"allowed-tools"}
            for key, value in existing_meta.items():
                if key not in ("name", "description") and key not in SKIP_FIELDS:
                    frontmatter[key] = value
            yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
            output = f"---\n{yaml_str}---\n\n{content.strip()}\n"
            (dest_skill_dir / "SKILL.md").write_text(output, encoding="utf-8")
        SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
        for item in source_dir.iterdir():
            if item.is_dir():
                if item.name not in SKIP_DIRS and not item.name.startswith("."):
                    shutil.copytree(item, dest_skill_dir / item.name, dirs_exist_ok=True)
            elif item.name != "SKILL.md" and item.suffix in (".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh"):
                shutil.copy2(item, dest_skill_dir / item.name)
        return True
    except Exception as e:
        print(f"  Error converting skill {source_dir.name}: {e}")
        return False


def convert_workflow_to_prompt(source_path: Path, dest_path: Path) -> bool:
    """Convert workflow to Copilot prompt file (.prompt.md)."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        content = source_path.read_text(encoding="utf-8")
        existing_meta = {}
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if frontmatter_match:
            try:
                existing_meta = yaml.safe_load(frontmatter_match.group(1)) or {}
                content = content[frontmatter_match.end():]
            except yaml.YAMLError:
                pass
        frontmatter = {}
        if "name" in existing_meta:
            frontmatter["name"] = existing_meta["name"]
        if "description" in existing_meta:
            frontmatter["description"] = existing_meta["description"]
        elif desc_match := re.search(r"^##?\s*Purpose\s*\n\n(.+?)(?:\n\n|\n##)", content, re.DOTALL):
            frontmatter["description"] = desc_match.group(1).strip()[:200]
        if "agent" in existing_meta:
            frontmatter["agent"] = existing_meta["agent"]
        if "model" in existing_meta:
            frontmatter["model"] = existing_meta["model"]
        if "tools" in existing_meta:
            frontmatter["tools"] = existing_meta["tools"]
        if "argument-hint" in existing_meta:
            frontmatter["argument-hint"] = existing_meta["argument-hint"]
        if frontmatter:
            yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
            output = f"---\n{yaml_str}---\n\n{content.strip()}\n"
        else:
            output = content.strip() + "\n"
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def convert_rule_to_instruction(source_path: Path, dest_path: Path) -> bool:
    """Convert rule to Copilot instruction file (.instructions.md)."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        content = source_path.read_text(encoding="utf-8")
        existing_meta = {}
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if frontmatter_match:
            try:
                existing_meta = yaml.safe_load(frontmatter_match.group(1)) or {}
                content = content[frontmatter_match.end():]
            except yaml.YAMLError:
                pass
        frontmatter = {}
        if "name" in existing_meta:
            frontmatter["name"] = existing_meta["name"]
        if "description" in existing_meta:
            frontmatter["description"] = existing_meta["description"]
        if "applyTo" in existing_meta:
            frontmatter["applyTo"] = existing_meta["applyTo"]
        elif "trigger" in existing_meta:
            trigger = existing_meta["trigger"]
            if trigger == "always_on":
                frontmatter["applyTo"] = "**"
            elif isinstance(trigger, str) and "*" in trigger:
                frontmatter["applyTo"] = trigger
        if frontmatter:
            yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
            output = f"---\n{yaml_str}---\n\n{content.strip()}\n"
        else:
            output = content.strip() + "\n"
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting rule {source_path.name}: {e}")
        return False


def convert_to_copilot(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """Main conversion function for GitHub Copilot format."""
    stats = {"agents": 0, "skills": 0, "workflows": 0, "rules": 0, "errors": [], "warnings": []}
    agents_src = source_root / ".agent" / "agents"
    agents_dest = dest_root / ".github" / "agents"
    skills_src = source_root / ".agent" / "skills"
    skills_dest = dest_root / ".github" / "skills"
    workflows_src = source_root / ".agent" / "workflows"
    workflows_dest = dest_root / ".github" / "prompts"
    rules_src = source_root / ".agent" / "rules"
    rules_dest = dest_root / ".github" / "instructions"

    if agents_src.exists():
        if verbose:
            print("Converting agents to Copilot format...")
        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / agent_file.name
            if convert_agent_to_copilot(agent_file, dest_file):
                stats["agents"] += 1
                if verbose:
                    print(f"  {agent_file.name}")
            else:
                stats["errors"].append(f"agent:{agent_file.name}")

    if skills_src.exists():
        if verbose:
            print("Converting skills to Copilot format...")
        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                if convert_skill_to_copilot(skill_dir, skills_dest):
                    stats["skills"] += 1
                    if verbose:
                        print(f"  {skill_dir.name}")
                else:
                    stats["errors"].append(f"skill:{skill_dir.name}")

    if workflows_src.exists():
        if verbose:
            print("Converting workflows to Copilot prompt files...")
        for workflow_file in workflows_src.glob("*.md"):
            dest_file = workflows_dest / workflow_file.name.replace(".md", ".prompt.md")
            if convert_workflow_to_prompt(workflow_file, dest_file):
                stats["workflows"] += 1
                if verbose:
                    print(f"  {workflow_file.name}")
            else:
                stats["errors"].append(f"workflow:{workflow_file.name}")

    if rules_src.exists():
        if verbose:
            print("Converting rules to Copilot instructions...")
        for rule_file in rules_src.glob("*.md"):
            dest_file = rules_dest / rule_file.name.replace(".md", ".instructions.md")
            if convert_rule_to_instruction(rule_file, dest_file):
                stats["rules"] += 1
                if verbose:
                    print(f"  {rule_file.name}")
            else:
                stats["errors"].append(f"rule:{rule_file.name}")

    # Run external skill plugins (declarative, config-driven via .agent/plugins.json)
    try:
        from agent_bridge.core.plugins import PluginRunner

        runner = PluginRunner(source_root)
        plugin_results = runner.run_for_ide("copilot", dest_root, verbose=verbose)
        for pname, pstatus in plugin_results.items():
            if pstatus == "ok":
                if verbose:
                    print(f"  ✓ Plugin '{pname}' installed")
            elif pstatus.startswith("error"):
                stats["warnings"].append(f"Plugin '{pname}': {pstatus}")
    except ImportError:
        pass

    if verbose:
        print(f"\nCopilot conversion complete:")
        print(f"  {stats['agents']} agents, {stats['skills']} skills")
        print(f"  {stats['workflows']} workflows, {stats['rules']} rules")
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")
    return stats


# =============================================================================
# REVERSE CONVERSION (IDE -> .agent/)
# =============================================================================


def reverse_convert_copilot(
    project_path: Path, agent_dir: Path, verbose: bool = True
) -> List[CapturedFile]:
    """Scan .github/ va tra ve danh sach file co the capture."""
    result: List[CapturedFile] = []
    github_root = project_path / ".github"

    if not github_root.exists():
        return result

    agents_dir = github_root / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            agent_path = agent_dir / "agents" / f.name
            result.append(
                CapturedFile(
                    ide_path=f,
                    agent_path=agent_path,
                    status="new",
                    ide_name="copilot",
                )
            )

    skills_dir = github_root / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                agent_path = agent_dir / "skills" / d.name / "SKILL.md"
                result.append(
                    CapturedFile(
                        ide_path=d / "SKILL.md",
                        agent_path=agent_path,
                        status="new",
                        ide_name="copilot",
                    )
                )

    prompts_dir = github_root / "prompts"
    if prompts_dir.exists():
        for f in prompts_dir.glob("*.prompt.md"):
            stem = f.name.replace(".prompt.md", "")
            agent_path = agent_dir / "workflows" / f"{stem}.md"
            result.append(
                CapturedFile(
                    ide_path=f,
                    agent_path=agent_path,
                    status="new",
                    ide_name="copilot",
                )
            )

    instructions_dir = github_root / "instructions"
    if instructions_dir.exists():
        for f in instructions_dir.glob("*.instructions.md"):
            stem = f.name.replace(".instructions.md", "")
            agent_path = agent_dir / "rules" / f"{stem}.md"
            result.append(
                CapturedFile(
                    ide_path=f,
                    agent_path=agent_path,
                    status="new",
                    ide_name="copilot",
                )
            )

    return result


def apply_reverse_capture_copilot(
    captured: CapturedFile, project_path: Path, agent_dir: Path
) -> bool:
    """Thuc hien ghi noi dung reverse-converted vao agent_path."""
    ide_path = captured.ide_path
    agent_path = captured.agent_path
    if not ide_path.exists():
        return False

    github_root = project_path / ".github"

    if github_root / "agents" in ide_path.parents or ide_path.parent == github_root / "agents":
        content = ide_path.read_text(encoding="utf-8")
        body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        agent_path.write_text(body, encoding="utf-8")
        return True

    if github_root / "skills" in ide_path.parents:
        skill_dir = ide_path.parent
        content = ide_path.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if fm_match:
            try:
                fm = yaml.safe_load(fm_match.group(1)) or {}
                body = content[fm_match.end() :].strip()
                fm_clean = {k: v for k, v in fm.items() if k in ("name", "description")}
                if fm_clean:
                    fm_str = yaml.dump(fm_clean, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    body = f"---\n{fm_str}---\n\n{body}\n"
            except yaml.YAMLError:
                body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
        else:
            body = content.strip()
        dest_skill_dir = agent_dir / "skills" / skill_dir.name
        dest_skill_dir.mkdir(parents=True, exist_ok=True)
        (dest_skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
        for item in skill_dir.iterdir():
            if item.name != "SKILL.md":
                if item.is_file():
                    shutil.copy2(item, dest_skill_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, dest_skill_dir / item.name, dirs_exist_ok=True)
        return True

    if github_root / "prompts" in ide_path.parents or ide_path.parent == github_root / "prompts":
        content = ide_path.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if fm_match:
            try:
                fm = yaml.safe_load(fm_match.group(1)) or {}
                body = content[fm_match.end() :].strip()
                fm_clean = {k: v for k, v in fm.items() if k not in ("tools", "argument-hint")}
                if fm_clean:
                    fm_str = yaml.dump(fm_clean, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    body = f"---\n{fm_str}---\n\n{body}\n"
            except yaml.YAMLError:
                body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
        else:
            body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        agent_path.write_text(body, encoding="utf-8")
        return True

    if github_root / "instructions" in ide_path.parents or ide_path.parent == github_root / "instructions":
        content = ide_path.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if fm_match:
            try:
                fm = yaml.safe_load(fm_match.group(1)) or {}
                body = content[fm_match.end() :].strip()
                
                # Strip IDE-specific fields
                apply_to = fm.pop("applyTo", None)
                fm.pop("name", None)
                fm.pop("description", None)
                
                # Convert applyTo to trigger
                if apply_to == "**":
                    fm["trigger"] = "always_on"
                elif apply_to:
                    fm["trigger"] = apply_to
                
                # Only write frontmatter if there are remaining fields
                if fm:
                    fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    body = f"---\n{fm_str}---\n\n{body}\n"
                else:
                    body = f"{body}\n"
            except yaml.YAMLError:
                body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
        else:
            body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        agent_path.write_text(body, encoding="utf-8")
        return True

    return False
