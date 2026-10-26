# 桌面應用程式建置指南

本文件說明如何建置 MCP Feedback Enhanced 的桌面應用程式。

## 先決條件

### 必需工具

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Rust 工具鏈**
   ```bash
   # 安裝 Rust (如果尚未安裝)
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

   # 驗證安裝
   rustc --version
   cargo --version
   ```

3. **Tauri CLI** (自動安裝)
   ```bash
   cargo install tauri-cli
   ```

### 開發依賴

```bash
# 安裝 Python 開發依賴
uv sync --dev

# 或使用 pip
pip install -e ".[dev]"
```

## 建置方法

### 方法 1: 使用 Makefile (建議)

```bash
# 建置 Debug 版本
make build-desktop

# 建置 Release 版本
make build-desktop-release

# 建置並測試
make test-desktop

# 清理建置產物
make clean-desktop

# 完整建置流程 (包含 PyPI 套件)
make build-all
```

### 方法 2: 直接使用 Python 腳本

```bash
# 建置 Debug 版本
python scripts/build_desktop.py

# 建置 Release 版本
python scripts/build_desktop.py --release

# 清理建置產物
python scripts/build_desktop.py --clean

# 查看說明
python scripts/build_desktop.py --help
```

## 建置產物

建置完成後，產物將位於：

```
src/mcp_feedback_enhanced/
├── desktop_release/                                   # 發佈用二進位檔案
│   ├── __init__.py
│   ├── mcp-feedback-enhanced-desktop.exe              # Windows
│   ├── mcp-feedback-enhanced-desktop-macos-intel     # macOS Intel
│   ├── mcp-feedback-enhanced-desktop-macos-arm64     # macOS Apple Silicon
│   └── mcp-feedback-enhanced-desktop-linux           # Linux
├── desktop_app/                                       # 發佈用 Python 模組
│   ├── __init__.py
│   └── desktop_app.py
└── ...

src-tauri/python/mcp_feedback_enhanced_desktop/        # 開發環境模組
├── __init__.py
├── desktop_app.py
└── ...
```

### 多平台支援

建置腳本會自動建置以下平台的二進位檔案：

- **Windows**: `mcp-feedback-enhanced-desktop.exe`
- **macOS Intel**: `mcp-feedback-enhanced-desktop-macos-intel`
- **macOS Apple Silicon**: `mcp-feedback-enhanced-desktop-macos-arm64`
- **Linux**: `mcp-feedback-enhanced-desktop-linux`

桌面應用會根據執行平台自動選擇對應的二進位檔案。

## 測試桌面應用程式

```bash
# 方法 1: 直接測試
python -m mcp_feedback_enhanced test --desktop

# 方法 2: 使用 Makefile
make test-desktop
```

## 跨平台注意事項

### Windows
- 桌面應用程式不會顯示額外的 CMD 視窗
- 二進位檔案: `mcp-feedback-enhanced-desktop.exe`

### Linux/macOS
- 二進位檔案: `mcp-feedback-enhanced-desktop`
- 自動設定執行權限

## 故障排除

### 常見問題

1. **Rust 未安裝**
   ```
   ❌ 未找到 Rust 編譯器
   💡 請安裝 Rust: https://rustup.rs/
   ```
   解決方案: 安裝 Rust 工具鏈

2. **Tauri CLI 未安裝**
   ```
   ⚠️  Tauri CLI 未安裝，嘗試安裝...
   ```
   解決方案: 腳本會自動安裝；若接著顯示 `❌ 無法安裝 Tauri CLI`，請手動執行 `cargo install tauri-cli` 查看錯誤

3. **建置失敗**
   ```
   ❌ 構建失敗: <錯誤訊息>
   ```
   或所有平台的 Tauri 建置都失敗時：
   ```
   ❌ 所有平台構建都失敗了
   ❌ 沒有成功構建任何平台
   ```
   解決方案: 依錯誤訊息檢查 Rust 環境，再清理後重新建置：
   ```bash
   make clean-desktop
   make build-desktop
   ```

### 檢查環境

```bash
# 檢查 Rust 環境
make check-rust

# 安裝開發依賴與 pre-commit hooks
make dev-setup
```

### 跨平台編譯要求

建置腳本會自動安裝以下 Rust targets：

```bash
# 這些 targets 會自動安裝，無需手動執行
rustup target add x86_64-pc-windows-msvc      # Windows
rustup target add x86_64-apple-darwin         # macOS Intel
rustup target add aarch64-apple-darwin        # macOS Apple Silicon
rustup target add x86_64-unknown-linux-gnu    # Linux
```

**注意**:
- 本機建置通常只能成功建置目前平台的二進位檔案
- 跨平台編譯需要複雜的工具鏈設定（C 編譯器、系統函式庫等）
- **完整的多平台支援在 GitHub Actions CI 中達成**
- 發佈到 PyPI 時會自動包含所有平台的二進位檔案

## 自動化建置

### CI/CD 多平台建置

GitHub Actions 會在各自的原生平台上建置桌面應用：

```yaml
# 多平台建置策略
strategy:
  matrix:
    include:
      - os: windows-latest    # Windows 原生建置
        target: x86_64-pc-windows-msvc
      - os: macos-latest      # macOS 原生建置
        target: x86_64-apple-darwin
      - os: ubuntu-latest     # Linux 原生建置
        target: x86_64-unknown-linux-gnu
```

這確保了：
- ✅ 每個平台在其原生環境中建置
- ✅ 避免跨平台編譯的複雜性
- ✅ 最終 PyPI 套件包含所有平台的二進位檔案

### 本機自動化

```bash
# 完整的開發工作流程
make dev-setup      # 初始化環境
make quick-check    # 程式碼檢查
make build-all      # 建置所有元件
make test-all       # 測試所有功能
```

## 發布流程

1. **建置發布版本**
   ```bash
   make build-desktop-release
   ```

2. **建置 PyPI 套件**
   ```bash
   make build-all
   ```

3. **驗證套件內容**
   ```bash
   # 檢查桌面應用程式是否包含在套件中
   tar -tf dist/*.tar.gz | grep desktop
   ```

桌面應用程式現在已完全整合到 PyPI 套件中，包含所有主要平台的二進位檔案，使用者安裝後可直接使用 `--desktop` 選項啟動。

### 平台相容性

- **Windows**: 支援 x64 架構
- **macOS**: 支援 Intel 和 Apple Silicon (M1/M2) 架構
- **Linux**: 支援 x64 架構

桌面應用會自動偵測執行平台並選擇對應的二進位檔案。
