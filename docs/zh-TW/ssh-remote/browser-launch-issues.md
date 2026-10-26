# SSH Remote 環境瀏覽器啟動問題解決方案

## 問題描述

在 SSH Remote 環境（如 Cursor SSH Remote、VS Code Remote SSH 、WSL 等）中使用 MCP Feedback Enhanced 時，可能會遇到以下問題：

- 🚫 瀏覽器無法自動啟動
- ❌ 顯示「無法啟動瀏覽器」錯誤
- 🔗 Web UI 無法在本機瀏覽器中開啟

## 原因分析

SSH Remote 環境的限制：
1. **顯示環境隔離**: 遠端伺服器沒有圖形介面環境
2. **網路隔離**: 遠端連接埠無法直接在本機存取
3. **瀏覽器不存在**: 遠端環境通常沒有安裝瀏覽器

## 解決方案

### 步驟一：設定連接埠（選用）

MCP Feedback Enhanced 預設使用連接埠 **8765**，您也可以自訂連接埠：

![設定連接埠](../images/ssh-remote-port-setting.png)

### 步驟二：等待 MCP 呼叫

**重要**：不要手動啟動 Web UI，而是要等待 AI 模型呼叫 MCP 工具時自動啟動。

當 AI 模型呼叫 `interactive_feedback` 工具時，系統會自動啟動 Web UI。

### 步驟三：查看連接埠並連線

如果瀏覽器沒有自動啟動，您需要手動連線到 Web UI：

#### 方法一：查看連接埠轉送
查看您的 SSH Remote 環境的連接埠轉送設定，找到對應的本機連接埠：

![連線到 URL](../images/ssh-remote-connect-url.png)

#### 方法二：使用 Debug 模式查看
在 IDE 中開啟 Debug 模式，選擇「輸出」→「MCP Log」，可以看到 Web UI 的 URL：

![Debug 模式查看連接埠](../images/ssh-remote-debug-port.png)

### 步驟四：在本機瀏覽器開啟

1. 複製 URL（通常是 `http://localhost:8765` 或其他連接埠）
2. 在本機瀏覽器中貼上並開啟
3. 開始使用 Web UI 進行回饋

## 連接埠轉送設定

### VS Code Remote SSH
1. 在 VS Code 中按 `Ctrl+Shift+P`
2. 輸入 "Forward a Port"
3. 輸入連接埠號碼（預設 8765）
4. 在本機瀏覽器中前往 `http://localhost:8765`

### Cursor SSH Remote
1. 查看 Cursor 的連接埠轉送設定
2. 手動加入連接埠轉送規則（連接埠 8765）
3. 在本機瀏覽器中開啟轉送後的連接埠

## 重要提醒

### ⚠️ 不要手動啟動
**請勿**手動執行 `uvx mcp-feedback-enhanced test --web` 等指令，這樣無法與 MCP 系統整合。

### ✅ 正確流程
1. 等待 AI 模型呼叫 MCP 工具
2. 系統自動啟動 Web UI
3. 查看連接埠轉送或 Debug 日誌
4. 在本機瀏覽器中開啟對應 URL

## 常見問題

### Q: 為什麼在 SSH Remote 環境中無法自動開啟瀏覽器？
A: SSH Remote 環境是無頭環境（headless），沒有圖形介面，因此無法直接啟動瀏覽器。需要透過連接埠轉送在本機瀏覽器中存取。

### Q: 如何確認 Web UI 是否正常啟動？
A: 查看 IDE 的 Debug 輸出或 MCP Log，如果看到 "Web UI 已啟動" 的訊息，表示啟動成功。

### Q: 連接埠被佔用怎麼辦？
A: 在 MCP 設定中修改連接埠號碼，或者等待系統自動選擇其他可用連接埠。

### Q: 找不到連接埠轉送設定怎麼辦？
A: 查看您的 SSH Remote 工具文件，或使用 Debug 模式查看 MCP Log 中的 URL。

### Q: 為什麼沒有接收到 MCP 新的回饋？
A: 可能是 WebSocket 連線有問題。**解決方法**：直接重新整理瀏覽器頁面，這會重新建立 WebSocket 連線。

### Q: 為什麼沒有呼叫出 MCP？
A: 請確認 MCP 工具狀態為綠燈（表示正常運作）。**解決方法**：
- 檢查 IDE 中的 MCP 工具狀態指示燈
- 如果不是綠燈，嘗試反覆開關 MCP 工具
- 等待幾秒鐘讓系統重新連線

### Q: 為什麼 Augment 無法啟動 MCP？
A: 有時候可能會有錯誤導致 MCP 工具沒有顯示綠燈狀態。**解決方法**：
- 完全關閉並重新啟動 VS Code 或 Cursor
- 重新開啟專案
- 等待 MCP 工具重新載入並顯示綠燈
