# Agent Bridge 🚀

Công cụ cầu nối giúp chuyển đổi và đồng bộ tri thức Agent/Skill từ dự án Antigravity sang các IDE và CLI phổ biến.

## 🚀 Cài đặt nhanh (Quick Start)

Copy và chạy lệnh này để cài đặt tool chỉ trong 1 lần dán:

```bash
git clone https://github.com/HaoNgo232/agent-bridge && cd agent-bridge && pipx install -e . --force
```

*Lưu ý: Bạn cần cài đặt `pipx` trước nếu chưa có (`sudo apt install pipx` hoặc `brew install pipx`).*

## 🛠️ Cách sử dụng

### 1. Khởi tạo & Cập nhật (`init`)

Di chuyển vào dự án của bạn để khởi tạo cấu hình Agent, Skill và cài đặt MCP.

**Tính năng thông minh (Smart Init):**
- **Bảo mật**: Tự động hỏi trước khi ghi đè MCP config (Mặc định: Bỏ qua để giữ key của bạn).
- **Cập nhật**: Tự động hỏi trước khi cập nhật Agent/Skill (Mặc định: Có).
- **Tương tác**: Sử dụng `--force` hoặc `-f` để bỏ qua mọi câu hỏi.

```bash
# Khởi tạo cho tất cả các định dạng
agent-bridge init

# Sử dụng chế độ cưỡng chế (Non-interactive)
agent-bridge init --force

# Khởi tạo cho từng định dạng cụ thể
agent-bridge init --copilot
agent-bridge init --opencode
agent-bridge init --kiro
agent-bridge init --cursor
agent-bridge init --windsurf
```

### 2. Quản lý MCP (`mcp`)

Cài đặt hoặc cập nhật cấu hình MCP (`.agent/mcp_config.json`) vào các IDE.

```bash
# Cài đặt MCP cho tất cả IDE (Có hỏi xác nhận nếu file đã tồn tại)
agent-bridge mcp --all

# Cài đặt cưỡng chế
agent-bridge mcp --all --force

# Cài đặt theo từng IDE
agent-bridge mcp --cursor    # .cursor/mcp.json
agent-bridge mcp --opencode  # .opencode/opencode.json
agent-bridge mcp --copilot   # .vscode/mcp.json
agent-bridge mcp --kiro      # .kiro/settings/mcp.json
```

### 3. Đồng bộ Tri thức (`update`)

Đồng bộ tri thức mới nhất từ repository Antigravity Kit gốc về máy. Lệnh này sẽ tự động làm mới (`refresh`) các cấu hình nếu dự án hiện tại đã có sẵn các folder IDE.

```bash
agent-bridge update
```

### 4. Dọn dẹp (`clean`)

Xóa các thư mục cấu hình AI đã tạo:

```bash
# Xóa tất cả cấu hình
agent-bridge clean --all

# Xóa theo từng IDE
agent-bridge clean --copilot
agent-bridge clean --kiro
```

## 💎 Các định dạng hỗ trợ & Tính năng đặc biệt

| IDE/CLI | Trạng thái | Vị trí cấu hình | Tính năng nổi bật |
|---------|------------|-----------------|-------------------|
| **Kiro CLI** | 🟢 STABLE | `.kiro/` | **Official Spec**, Auto-trust MCP, Custom Prompts (@), Spawn Hooks |
| **GitHub Copilot** | 🟡 BETA | `.github/` | Official Agent Spec (JSON/MD), Metadata merging |
| **OpenCode IDE** | 🟡 BETA | `.opencode/` | Unified JSON settings, Skill support |
| **Cursor AI** | 🟡 BETA | `.cursor/rules/` | Rule-based steering |
| **Windsurf IDE** | 🟡 BETA | `.windsurf/` | Context-aware logic |

## 📂 Cấu trúc dự án

- `.agent/`: Master Vault lưu trữ tri thức gốc.
- `src/agent_bridge/`: Logic chuyển đổi core cho từng IDE.
- `utils.py`: Tiện ích giao diện CLI và tương tác người dùng.

---
*Phát triển bởi Hao Ngo*
