# Agent Bridge

Công cụ chuyển đổi cấu hình Agent và Skill từ Antigravity Kit sang định dạng tương thích với các IDE (GitHub Copilot, OpenCode) và CLI (Kiro).

## Cài đặt

Cài đặt bằng `pip` ở chế độ editable để sử dụng lệnh toàn cục:

```bash
cd agent-bridge
pip install -e .
```

## Cách sử dụng

### 1. Khởi tạo cấu hình (`init`)

Di chuyển vào dự án của bạn và chạy:

```bash
# Khởi tạo cho tất cả các định dạng được hỗ trợ
agent-bridge init

# Khởi tạo cho từng định dạng cụ thể
agent-bridge init --copilot
agent-bridge init --opencode
agent-bridge init --kiro
```

### 2. Cập nhật tri thức (`update`)

Đồng bộ tri thức mới nhất từ repository Antigravity Kit gốc về máy. Lệnh này sẽ tự động cập nhật lại các cấu hình (`refresh`) nếu project hiện tại đã có sẵn các folder IDE.

```bash
agent-bridge update
```

### 3. Dọn dẹp cấu hình (`clean`)

Xóa các thư mục cấu hình AI đã tạo trong dự án:

```bash
# Xóa tất cả các folder .github/agents, .github/skills, .kiro, .opencode
agent-bridge clean

# Xóa theo từng IDE
agent-bridge clean --copilot
agent-bridge clean --opencode
agent-bridge clean --kiro
```

### 4. Kiểm tra hỗ trợ (`list`)

Xem danh sách các định dạng IDE/CLI mà công cụ đang hỗ trợ:

```bash
agent-bridge list
```

## Các định dạng hỗ trợ

| IDE/CLI | Vị trí cấu hình |
|---------|-----------------|
| **GitHub Copilot** | `.github/agents/`, `.github/skills/` |
| **OpenCode IDE** | `.opencode/`, `AGENTS.md` |
| **Kiro CLI** | `.kiro/agents/` |

## Cấu trúc thư mục công cụ

- `.agent/`: Master Vault lưu trữ tri thức gốc.
- `src/agent_bridge/`: Logic chuyển đổi cho từng định dạng.
- `README.md`: Hướng dẫn này.
