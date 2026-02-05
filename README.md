# 🌉 Agent Bridge (Antigravity Edition)

**Universal Knowledge Bridge for the Agentic Future.**

`agent-bridge` là một công cụ mạnh mẽ được thiết kế để quản lý, cập nhật và chuyển đổi các Agent và Skill từ Antigravity Kit sang định dạng mà các IDE hiện đại (như GitHub Copilot) và CLI (như Kiro) có thể hiểu được.

## 🌟 Tính năng cốt lõi

- **Master Vault**: Lưu trữ một "Kho tri thức Master" ngay trong máy của bạn để sử dụng offline và dự phòng.
- **Official Copilot Spec**: Chuyển đổi sang định dạng chuẩn của GitHub (`.github/agents/`).
- **OpenCode Support**: Chuyển đổi sang định dạng chuẩn của OpenCode IDE (`.opencode/agents/` và `AGENTS.md`).
- **One-Touch Sync**: Đồng bộ hóa tức thì với repository gốc.
- **Smart Refresh**: Tự động cập nhật lại toàn bộ các cấu hình IDE (Copilot/Kiro/OpenCode) sau khi đồng bộ.
- **Smart Fallback**: Tự động sử dụng Master Vault nếu project hiện tại chưa có thư mục `.agent`.

---

## 🚀 Bước 1: Cài đặt (Chỉ thực hiện MỘT LẦN duy nhất)

1. **Clone project này về máy**:
   ```bash
   git clone <link-repo-cua-ban>
   cd agent-bridge
   ```
2. **Cài đặt Global**:
   ```bash
   pip install -e . --break-system-packages
   ```

---

## 🛠️ Bước 2: Hướng dẫn sử dụng

Lệnh `agent-bridge` đã sẵn sàng để sử dụng ở bất cứ đâu.

### A. Khởi tạo AI cho project mới (`init`)
Chỉ cần di chuyển vào project mới và gõ:
```bash
agent-bridge init
```
*Lệnh này sẽ lấy tri thức (ưu tiên local, fallback Master) và tạo cả cấu trúc Copilot và Kiro cho bạn ngay lập tức.*

### B. Cập nhật và "Làm mới" toàn bộ (`update`)
Dùng lệnh này khi bạn muốn lấy tri thức mới nhất từ Antigravity Kit.
```bash
# Đứng tại thư mục master của agent-bridge
agent-bridge update

# HOẶC đứng tại project của bạn
agent-bridge update
```
*Lệnh này sẽ:*
1. Tải bản mới nhất từ Internet về Master Vault.
2. Tự động tìm xem project hiện tại có folder `.github/agents` hay `.kiro/agents` không để tự "refresh" chúng luôn.

### C. Chuyển đổi riêng lẻ
- `agent-bridge copilot`: Chỉ tạo/cập nhật chuẩn GitHub Copilot.
- `agent-bridge kiro`: Chỉ tạo/cập nhật chuẩn Kiro CLI.

---

## 📂 Giải thích cấu trúc

- `.agent/`: **Master Vault** - Bản sao cục bộ của tri thức Antigravity.
- `src/agent_bridge/`: Mã nguồn thực thi.
- `pyproject.toml`: Cấu hình hệ thống.

---
Built by HaoNgo232
