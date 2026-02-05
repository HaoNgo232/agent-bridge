import json
import tempfile
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_bridge.copilot_conv import convert_copilot
from agent_bridge.cursor_conv import convert_cursor
from agent_bridge.windsurf_conv import convert_windsurf
from agent_bridge.opencode_conv import convert_opencode


def create_test_agents_dir(tmp_dir):
    """Create minimal test agents structure"""
    agents_dir = tmp_dir / "agents"
    agents_dir.mkdir()
    
    # Create test agent
    agent_content = """---
name: test-agent
description: Test agent for verification
---

You are a test agent."""
    
    (agents_dir / "test-agent.md").write_text(agent_content)
    
    # Create skills
    skills_dir = tmp_dir / "skills" / "test-skill"
    skills_dir.mkdir(parents=True)
    
    skill_content = """---
name: test-skill
description: Test skill
usage: Use for testing
---

Test skill content."""
    
    (skills_dir / "SKILL.md").write_text(skill_content)
    
    return tmp_dir


def test_copilot_format():
    """Verify GitHub Copilot output format"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = create_test_agents_dir(tmp_path / "source")
        
        # Change to temp dir for output
        import os
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            convert_copilot(str(source), "", force=True)
            
            # Verify agent format
            agent_file = tmp_path / ".github" / "agents" / "test-agent.md"
            assert agent_file.exists(), "Agent file not created"
            
            content = agent_file.read_text()
            assert "---" in content, "Missing frontmatter"
            assert "name: test-agent" in content, "Missing name"
            assert "description:" in content, "Missing description"
            assert "applyTo" not in content, "❌ applyTo should not exist"
            
            # Verify skill format
            skill_file = tmp_path / ".github" / "skills" / "test-skill" / "SKILL.md"
            assert skill_file.exists(), "Skill file not created"
            
            skill_content = skill_file.read_text()
            assert "usage: Use for testing" in skill_content, "❌ usage format wrong (should not have quotes)"
            assert 'usage: "' not in skill_content, "❌ usage has quotes"
            
            print("✅ Copilot format: PASS")
            
        finally:
            os.chdir(old_cwd)


def test_cursor_format():
    """Verify Cursor output format"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = create_test_agents_dir(tmp_path / "source")
        
        import os
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            convert_cursor(str(source), "", force=True)
            
            # Verify .mdc format
            mdc_file = tmp_path / ".cursor" / "rules" / "project-instructions.mdc"
            assert mdc_file.exists(), "MDC file not created"
            
            content = mdc_file.read_text()
            lines = content.split('\n')
            
            # Check frontmatter
            assert lines[0] == "---", "Missing frontmatter start"
            assert "globs:" in content, "Missing globs field"
            assert "globs: *" not in content, "❌ globs should be empty, not '*'"
            assert "alwaysApply: true" in content, "Missing alwaysApply"
            
            # Verify skill has frontmatter
            skill_file = tmp_path / ".cursor" / "skills" / "test-skill.md"
            assert skill_file.exists(), "Skill file not created"
            
            skill_content = skill_file.read_text()
            assert "---" in skill_content, "❌ Skill missing frontmatter"
            assert "description:" in skill_content, "❌ Skill missing description"
            
            print("✅ Cursor format: PASS")
            
        finally:
            os.chdir(old_cwd)


def test_windsurf_format():
    """Verify Windsurf output format"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = create_test_agents_dir(tmp_path / "source")
        
        import os
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            convert_windsurf(str(source), "", force=True)
            
            # Verify agent file has frontmatter
            agent_file = tmp_path / ".windsurf" / "rules" / "test-agent.md"
            assert agent_file.exists(), "Agent file not created"
            
            content = agent_file.read_text()
            assert "---" in content, "❌ Missing frontmatter"
            assert "trigger: always_on" in content, "❌ Missing trigger mode"
            assert "description:" in content, "❌ Missing description"
            
            # Verify skill file has frontmatter
            skill_file = tmp_path / ".windsurf" / "rules" / "test-skill.md"
            assert skill_file.exists(), "Skill file not created"
            
            skill_content = skill_file.read_text()
            assert "trigger: always_on" in skill_content, "❌ Skill missing trigger"
            
            print("✅ Windsurf format: PASS")
            
        finally:
            os.chdir(old_cwd)


def test_opencode_format():
    """Verify OpenCode output format"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = create_test_agents_dir(tmp_path / "source")
        
        import os
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            convert_opencode(str(source), "", force=True)
            
            # Verify opencode.json exists
            opencode_json = tmp_path / ".opencode" / "opencode.json"
            assert opencode_json.exists(), "opencode.json not created"
            
            config = json.loads(opencode_json.read_text())
            assert "mcp" in config, "❌ MCP config not in opencode.json"
            assert isinstance(config["mcp"], dict), "❌ MCP should be dict"
            
            # Verify agent file
            agent_file = tmp_path / ".opencode" / "agents" / "test-agent.md"
            assert agent_file.exists(), "Agent file not created"
            
            agent_content = agent_file.read_text()
            assert "---" in agent_content, "Missing frontmatter"
            assert "mode: subagent" in agent_content, "Missing mode"
            
            print("✅ OpenCode format: PASS")
            
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    print("\n🧪 Running converter format tests...\n")
    
    try:
        test_copilot_format()
        test_cursor_format()
        test_windsurf_format()
        test_opencode_format()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
