# 桌面應用建置和發佈流程改進

## 🎯 改進目標

確保 GitHub Actions 能夠健全地建置所有平台的桌面應用執行檔，並在發佈流程中正確使用這些建置產物。

## 🔧 主要改進

### 1. 增強桌面建置工作流程 (`.github/workflows/build-desktop.yml`)

#### 新增功能：
- **平台特定依賴安裝**：為 Linux 平台自動安裝必要的系統依賴
- **詳細建置驗證**：檢查二進位檔案存在性、大小和類型
- **錯誤處理改進**：如果找不到建置產物則立即失敗
- **建置摘要增強**：提供詳細的建置狀態報告和下一步指引

#### 技術改進：
```yaml
# Linux 依賴安裝
- name: Install platform-specific dependencies (Linux)
  if: matrix.os == 'ubuntu-latest'
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      libwebkit2gtk-4.1-dev \
      libappindicator3-dev \
      librsvg2-dev \
      patchelf \
      libgtk-3-dev \
      libayatana-appindicator3-dev

# 增強的構建驗證
- name: Verify build output
  run: |
    BINARY_PATH="src-tauri/target/${{ matrix.target }}/release/${{ matrix.binary }}"
    if [ -f "$BINARY_PATH" ]; then
      echo "✅ 找到二進制文件: $BINARY_PATH"
      FILE_SIZE=$(stat -f%z "$BINARY_PATH" 2>/dev/null || stat -c%s "$BINARY_PATH" 2>/dev/null)
      echo "📏 文件大小: $FILE_SIZE bytes"
    else
      echo "❌ 二進制文件不存在: $BINARY_PATH"
      exit 1
    fi
```

### 2. 優化發佈工作流程 (`.github/workflows/publish.yml`)

#### 新增功能：
- **智慧桌面建置偵測**：自動尋找最新成功的桌面建置
- **穩健的產物下載**：改進錯誤處理和產物驗證
- **多平台二進位檔處理**：統一的平台對應和檔案重新命名
- **詳細驗證步驟**：確保所有平台的二進位檔案都有效

#### 技術改進：
```yaml
# 智能構建檢測
- name: Check desktop build availability
  run: |
    if [ -n "${{ github.event.inputs.desktop_build_run_id }}" ]; then
      echo "🎯 使用指定的構建 Run ID"
    else
      LATEST_RUN=$(curl -s -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
        "https://api.github.com/repos/${{ github.repository }}/actions/workflows/build-desktop.yml/runs?status=success&per_page=1" \
        | jq -r '.workflow_runs[0].id // empty')
      echo "run_id=$LATEST_RUN" >> $GITHUB_OUTPUT
    fi

# 統一平台映射
declare -A PLATFORM_MAP=(
  ["desktop-windows"]="mcp-feedback-enhanced-desktop.exe"
  ["desktop-macos-intel"]="mcp-feedback-enhanced-desktop-macos-intel"
  ["desktop-macos-arm64"]="mcp-feedback-enhanced-desktop-macos-arm64"
  ["desktop-linux"]="mcp-feedback-enhanced-desktop-linux"
)
```

### 3. 新增一鍵建置發佈工作流程 (`.github/workflows/build-and-release.yml`)

#### 功能特點：
- **自動化整個流程**：建置 → 驗證 → 發佈
- **靈活的平台選擇**：支援選擇特定平台或全平台建置
- **選用發佈模式**：可以只建置不發佈
- **統一狀態報告**：提供完整的流程摘要

#### 使用方式：
1. 前往 [Build Desktop & Release](../../actions/workflows/build-and-release.yml)
2. 點選 "Run workflow"
3. 選擇版本類型或輸入自訂版本
4. 選擇要建置的平台（預設：all）
5. 選用：勾選 "只構建桌面應用，不進行發佈"

### 4. 工作流程驗證腳本 (`scripts/validate_workflows.py`)

#### 功能：
- **YAML 語法驗證**：確保所有工作流程檔案語法正確
- **結構完整性檢查**：驗證必需欄位和設定
- **特定工作流程驗證**：針對桌面建置和發佈流程的專項檢查

#### 使用方式：
```bash
python scripts/validate_workflows.py
```

## 🚀 使用指南

### 方案 1：使用一鍵建置發佈（建議）
1. 觸發 "Build Desktop & Release" 工作流程
2. 系統自動建置所有平台
3. 建置成功後自動發佈

### 方案 2：分步執行
1. 先觸發 "Build Desktop Applications" 工作流程
2. 等待所有平台建置完成
3. 記錄 Run ID
4. 觸發 "Auto Release to PyPI" 工作流程
5. 設定 `include_desktop: true` 和對應的 Run ID

## 🔍 驗證清單

### 建置階段
- [ ] Windows x64 建置成功
- [ ] macOS Intel 建置成功  
- [ ] macOS ARM64 建置成功
- [ ] Linux x64 建置成功
- [ ] 所有二進位檔案大小 > 1MB
- [ ] Artifacts 正確上傳

### 發佈階段
- [ ] 桌面建置產物正確下載
- [ ] 所有平台二進位檔案正確重新命名
- [ ] 執行權限正確設定
- [ ] PyPI 套件包含桌面應用
- [ ] GitHub Release 建立成功

## 🛠️ 故障排除

### 常見問題

1. **Windows 平台 PowerShell 語法錯誤**
   - **問題**：`Missing '(' after 'if' in if statement`
   - **原因**：在 Windows 上使用了 bash 語法
   - **解決方案**：為所有 shell 腳本加上 `shell: bash` 指定

2. **Linux 相依套件衝突**
   - **問題**：`libayatana-appindicator3-dev` 與 `libappindicator3-dev` 衝突
   - **原因**：Ubuntu 24.04 中兩個套件不能同時安裝
   - **解決方案**：優先嘗試 ayatana 版本，失敗時回退到傳統版本

3. **Linux 建置失敗**
   - 檢查系統依賴是否正確安裝
   - 確認 GTK 和 WebKit 版本相容性
   - 檢查 appindicator 依賴是否正確安裝

4. **macOS 建置失敗**
   - 檢查 Xcode 命令列工具
   - 確認 target 設定正確
   - 驗證 Rust 工具鏈是否支援目標架構

5. **桌面產物下載失敗**
   - 確認指定的 Run ID 存在且成功
   - 檢查 Artifacts 保留期限（30天）
   - 驗證工作流程權限設定

6. **發佈套件缺少桌面應用**
   - 驗證 `include_desktop` 設為 true
   - 檢查桌面應用驗證步驟是否通過
   - 確認平台選擇邏輯正確執行

7. **部分平台建置失敗導致發佈被阻擋**
   - **問題**：只有部分平台建置成功（例如 2/4 個平台）
   - **原因**：發佈流程要求所有 4 個平台都必須成功
   - **解決方案**：
     - 重新執行桌面建置工作流程，確保所有平台成功
     - 檢查失敗平台的建置日誌
     - 或者設定 `include_desktop=false` 僅發佈 Web 版本

8. **多平台完整性要求**
   - **必須平台**：Windows x64、macOS Intel、macOS Apple Silicon、Linux x64
   - **驗證標準**：每個平台的二進位檔案必須 > 1MB
   - **失敗處理**：任何平台缺失或無效都會阻擋發佈

### 除錯步驟

1. **檢查工作流程設定**：
   ```bash
   python scripts/validate_workflows.py
   ```

2. **查看建置日誌**：
   - 前往 GitHub Actions 頁面
   - 檢查失敗步驟的詳細日誌

3. **驗證產物**：
   - 下載 Artifacts 手動檢查
   - 確認檔案大小和執行權限

## 📈 效果評估

### 改進前的問題
- ❌ 跨平台編譯在本機環境失敗
- ❌ 發佈流程缺少桌面應用驗證
- ❌ 錯誤處理不夠穩健
- ❌ 缺少統一的建置發佈流程

### 改進後的優勢
- ✅ 所有平台在原生環境建置
- ✅ 完整的產物驗證和錯誤處理
- ✅ 自動化的端到端流程
- ✅ 詳細的狀態報告和故障排除指引
- ✅ 靈活的建置和發佈選項

## 🎯 下一步

1. **測試新工作流程**：
   - 觸發桌面建置測試所有平台
   - 驗證發佈流程包含桌面應用

2. **監控和優化**：
   - 收集建置時間資料
   - 根據實際使用情況調整設定

3. **文件更新**：
   - 更新使用者指南
   - 加入更多故障排除案例
