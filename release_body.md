# Release v2.8.4 - 2026-10-25 - Session History Retention and Message Handling Fixes

## 🌟 Key Highlights
- Session history keeps earlier sessions after the MCP server restarts (#177); sessions a previous process left waiting for feedback show as "Disconnected".
- Session durations in history now come from the real creation and end times, and the retention period actually removes expired records.
- Durations in the English UI get spaces and singular/plural units (`7 seconds`, `1 minute 5 seconds`).
- A new-session notice is no longer swallowed by a heartbeat reply, so the page switches to the new session.
- After switching languages, the current session card and session history change to the new language immediately.

## 🌐 Detailed Release Notes

### 🇺🇸 English
📖 **[View Complete English Release Notes](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/RELEASE_NOTES/CHANGELOG.en.md)**

### 🇹🇼 繁體中文
📖 **[查看完整繁體中文發布說明](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/RELEASE_NOTES/CHANGELOG.zh-TW.md)**

### 🇨🇳 简体中文
📖 **[查看完整简体中文发布说明](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/RELEASE_NOTES/CHANGELOG.zh-CN.md)**

---

## 📦 Quick Installation / 快速安裝

```bash
# Latest version / 最新版本
uvx mcp-feedback-enhanced@latest

# This specific version / 此特定版本
uvx mcp-feedback-enhanced@v2.8.4
```

## 🔗 Links
- **Documentation**: [README.md](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/README.md)
- **Full Changelog**: [CHANGELOG](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/RELEASE_NOTES/)
- **Issues**: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

---
**Release automatically generated from CHANGELOG system** 🤖
