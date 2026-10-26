# 交互流程文件

## 🔄 AI 助手與 MCP 服務完整交互流程

本文件詳細描述 AI 助手呼叫 MCP Feedback Enhanced 服務的完整流程，包括首次呼叫、多次循環呼叫、錯誤處理和效能優化機制。

### 核心設計理念

- **持久化會話**: 支援 AI 助手多次循環呼叫，無需重複建立連線
- **環境適配**: WSL 中改用 Windows 瀏覽器開啟介面；SSH 等遠端環境需自行設定埠轉發
- **無縫狀態切換**: 會話更新時前端局部更新，保持使用者操作狀態
- **優雅錯誤處理**: 完整的錯誤恢復機制和逾時保護
- **資源優化**: 單一活躍會話模式，最小化資源佔用

## 📋 流程概覽

### 整體交互時序圖

```mermaid
sequenceDiagram
    participant AI as AI 助手<br/>(Cursor/Claude/etc)
    participant MCP as MCP 服務<br/>(server.py)
    participant WM as WebUIManager<br/>(單例管理器)
    participant FastAPI as FastAPI 應用<br/>(Web 服務)
    participant WS as WebSocket<br/>(即時通信)
    participant Browser as 瀏覽器<br/>(Web UI)
    participant User as 使用者

    Note over AI,User: 🚀 第一次呼叫流程
    AI->>+MCP: interactive_feedback(project_dir, summary, timeout)
    MCP->>MCP: 環境偵測（結果只寫進除錯日誌）
    MCP->>+WM: launch_web_feedback_ui()

    Note over WM: 會話建立
    WM->>WM: create_session()

    WM->>+FastAPI: 啟動 Web 伺服器（尚未啟動時）
    FastAPI-->>-WM: 伺服器就緒

    WM->>Browser: smart_open_browser(url)
    Note over Browser: 智能開啟瀏覽器<br/>檢測活躍分頁

    Browser->>+FastAPI: GET /
    FastAPI->>FastAPI: TemplateResponse("feedback.html")
    FastAPI-->>-Browser: HTML 頁面

    Browser->>+WS: 建立 WebSocket 連線
    WS->>WM: session.websocket = websocket
    WS-->>-Browser: connection_established

    Note over AI,User: 💬 使用者回饋流程
    User->>Browser: 填寫回饋內容
    Browser->>+WS: submit_feedback
    WS->>WM: session.submit_feedback()
    WM->>WM: feedback_completed.set()
    WS-->>-Browser: notification（回饋已收到）
    WM-->>-MCP: wait_for_feedback() 回傳回饋
    MCP-->>-AI: 回傳回饋結果

    Note over AI,User: 🔄 第二次呼叫流程 (持久化會話)
    AI->>+MCP: interactive_feedback(new_summary, timeout)
    MCP->>+WM: create_session()（每次呼叫都建立新會話）

    alt 舊分頁仍連線
        WM->>WM: 把舊 WebSocket 轉給新會話
        WM->>+WS: session_updated 通知
        WS-->>-Browser: 會話更新訊息
        Browser->>Browser: 局部更新內容
        Note over Browser: 無需重新載入頁面
    else 沒有連線中的分頁
        WM->>WM: 標記待送的會話更新
        WM->>Browser: 開啟瀏覽器，新連線建立後送 session_updated
    end

    User->>Browser: 提交新回饋
    Browser->>+WS: submit_feedback
    WS->>WM: session.submit_feedback()
    WS-->>-Browser: notification（回饋已收到）
    WM-->>-MCP: wait_for_feedback() 回傳回饋
    MCP-->>-AI: 回傳新回饋結果

    Note over AI,User: 🧹 資源清理
    alt 會話逾時
        WM->>WS: _cleanup_resources_on_timeout()
        WS->>Browser: notification（會話清理）並關閉連線
        Note over FastAPI: Web 伺服器繼續執行
    end
```

## 🚀 第一次呼叫詳細流程

### 1. AI 助手發起呼叫

**MCP 工具呼叫格式**：
```python
# AI 助手通過 MCP 協議調用
result = await interactive_feedback(
    project_directory="./my-project",
    summary="我已完成了功能 X 的實現，請檢查代碼品質和邏輯正確性。主要變更包括：\n1. 新增錯誤處理機制\n2. 優化性能瓶頸\n3. 增加單元測試覆蓋率",
    timeout=600  # 10 分鐘超時
)
```

**參數說明**：
- `project_directory`: 專案根目錄，用於上下文顯示
- `summary`: AI 工作摘要，向使用者說明已完成的工作
- `timeout`: 等待使用者回饋的逾時時間（秒）

### 2. MCP 服務處理流程

```mermaid
flowchart TD
    START[AI 呼叫 interactive_feedback] --> VALIDATE[timeout 鉗制到 60-86400 秒]
    VALIDATE --> ENV[環境偵測<br/>只寫除錯日誌]
    ENV --> MANAGER[取得 WebUIManager<br/>單例實例，首次建立時決定埠]
    MANAGER --> CREATE[create_session<br/>每次呼叫都建立新會話]

    CREATE --> SERVER[啟動 FastAPI 伺服器<br/>尚未啟動時]
    SERVER --> MODE{桌面模式?}
    MODE -->|是| DESKTOP[launch_desktop_app<br/>失敗時改走瀏覽器]
    MODE -->|否| BROWSER[智能開啟瀏覽器]

    BROWSER --> DETECT[檢測活躍分頁]
    DETECT --> OPEN_DECISION{有活躍分頁?}

    OPEN_DECISION -->|否| OPEN[開啟新瀏覽器視窗]
    OPEN_DECISION -->|是| NOTIFY[送出會話更新通知]

    DESKTOP --> WAIT[等待使用者回饋]
    OPEN --> WAIT
    NOTIFY --> WAIT

    WAIT --> TIMEOUT{檢查逾時}
    TIMEOUT -->|未逾時| FEEDBACK[接收回饋資料]
    TIMEOUT -->|逾時或介面關閉| CLEANUP[清理資源]

    FEEDBACK --> PROCESS[儲存回饋 JSON<br/>組合文字與圖片內容]
    PROCESS --> RETURN[回傳結果給 AI]

    CLEANUP --> ERROR[回傳「使用者未回應」文字]
    ERROR --> RETURN

    style START fill:#e3f2fd
    style RETURN fill:#e8f5e8
    style ERROR fill:#ffebee
    style FEEDBACK fill:#f3e5f5
```

**關鍵步驟詳解**：

#### 2.1 環境檢測與適配
- `is_remote_environment()`（`server.py`）依序檢查：WSL 一律不算遠端；`SSH_CONNECTION`、`SSH_CLIENT`、`SSH_TTY`；`REMOTE_CONTAINERS`、`CODESPACES`；`/.dockerenv`；Windows 的 `SESSIONNAME` 含 `RDP`；Linux 沒有 `DISPLAY`。結果只寫進除錯日誌與 `get_system_info` 的輸出，不改變任何行為，也不會建立 SSH 隧道。
- `is_wsl_environment()`（`web/utils/browser.py`）只在 Linux 上可能為真：`/proc/version` 含 `microsoft` 或 `wsl`、設了 `WSL_DISTRO_NAME`／`WSL_INTEROP`／`WSLENV`、或存在 `/mnt/c` 等 WSL 路徑。
- 開啟瀏覽器（`smart_browser_open()`）：桌面模式不開；WSL 依序試 `cmd.exe /c start`、`powershell.exe Start-Process`、`wslview`；其他環境用 Python 的 `webbrowser.open`。開不了時在 stderr 印出網址，請使用者手動開啟。

#### 2.2 智能會話管理
`WebUIManager.create_session(project_directory, summary)` 每次呼叫都建立新的 `WebFeedbackSession` 並設為目前會話：
- 舊會話若是「已提交」，推進為「已完成」，並留在 `sessions` 字典供 `/api/all-sessions` 查詢
- 舊會話有 WebSocket 連線時，把連線直接轉給新會話，之後由 `smart_open_browser()` 送出 `session_updated`
- 沒有舊連線時設定 `_pending_session_update`，等新 WebSocket 連線建立時送出 `session_updated`
- 回傳新的 `session_id`

#### 2.3 動態埠管理
埠在 `WebUIManager` 初始化時決定：
- `MCP_WEB_PORT=0`：綁定埠 0，由系統分配可用埠
- 其他情況以 `MCP_WEB_PORT`（1024-65535，無效時用 8765）或預設 8765 為偏好埠，交給 `PortManager.find_free_port_enhanced()`：偏好埠可用就用；被本專案或 uvicorn/fastapi 的 Python 行程佔用時先嘗試結束它；否則往上找最多 100 個埠，再往下找；都找不到時拋出 `RuntimeError`

### 3. Web UI 連線建立與初始化

```mermaid
sequenceDiagram
    participant Browser as 瀏覽器
    participant FastAPI as FastAPI 服務
    participant Template as 範本引擎
    participant WS as WebSocket
    participant Session as 會話管理
    participant I18N as 國際化

    Note over Browser,I18N: 頁面載入流程
    Browser->>+FastAPI: GET /
    FastAPI->>+Template: TemplateResponse("feedback.html")
    Template-->>-FastAPI: 完整頁面
    FastAPI-->>-Browser: HTML + CSS + JS
    Browser->>I18N: GET /api/translations
    I18N-->>Browser: 三種語言的翻譯資源

    Note over Browser,Session: WebSocket 連線建立
    Browser->>Browser: 載入 JavaScript 模組
    Browser->>+WS: 建立 WebSocket 連線 (/ws)
    WS->>WS: 檢查 Origin 與活躍會話
    WS->>Session: session.websocket = websocket
    WS-->>-Browser: connection_established

    Note over Browser,Session: 會話狀態同步
    alt 有待送的會話更新
        Session->>+WS: session_updated
        WS-->>-Browser: 會話更新通知
        Browser->>Browser: 局部更新內容
    else 沒有待送的更新
        Session->>+WS: status_update
        WS-->>-Browser: 目前會話狀態
    end

    Note over Browser,Session: 心跳檢測啟動
    Browser->>Browser: 啟動心跳定時器
    loop 每 60 秒
        Browser->>WS: heartbeat
        WS-->>Browser: heartbeat_response
    end
```

**連線建立關鍵步驟**：

#### 3.1 頁面渲染
`GET /`（`web/routes/main_routes.py` 的 `index()`）沒有活躍會話時渲染 `index.html`；有活躍會話時讀取使用者的版面設定（`load_user_layout_settings()`），以 `session_id`、`project_directory`、`summary`、`title`、`version`、`has_session`、`layout_mode` 渲染 `feedback.html`。翻譯不在伺服器端套用，由前端的 `i18n.js` 從 `/api/translations` 載入。

#### 3.2 WebSocket 連線處理
`/ws`（`websocket_endpoint()`）的處理順序：
1. Origin 不受信任時以代碼 4003 關閉；沒有活躍會話時以代碼 4004 關閉
2. 接受連線，`session.websocket = websocket`（取代舊連線），呼叫 `session.on_client_connected()`
3. 送出 `connection_established`；有 `_pending_session_update` 時接著送 `session_updated` 並清除標記，否則送 `status_update`
4. 迴圈讀取文字訊息並交給 `handle_websocket_message()`；會話已切換或連線不符時結束迴圈
5. 斷線時若這仍是會話登記的連線，清掉 `session.websocket` 並呼叫 `session.on_client_disconnected()` 啟動斷線寬限計時

## 🔄 多次循環呼叫機制

### 持久化會話架構

MCP Feedback Enhanced 的核心創新在於**持久化會話架構**，支援 AI 助手進行多次循環呼叫而無需重新建立連線。

```mermaid
stateDiagram-v2
    [*] --> FirstCall: AI 首次呼叫
    FirstCall --> SessionActive: 會話建立
    SessionActive --> UserFeedback: 等待使用者回饋
    UserFeedback --> FeedbackSubmitted: 回饋提交
    FeedbackSubmitted --> AIProcessing: AI 處理回饋
    AIProcessing --> SecondCall: AI 再次呼叫
    SecondCall --> SessionUpdated: 會話更新
    SessionUpdated --> UserFeedback: 等待新回饋

    note right of SessionActive
        Web 伺服器持續執行
        瀏覽器分頁保持開啟
        WebSocket 連線維持
    end note

    note right of SessionUpdated
        無需重新開啟瀏覽器
        局部更新頁面內容
        狀態無縫切換
    end note
```

### 第二次呼叫流程

#### 1. AI 助手再次呼叫
```python
# AI 根據用戶回饋進行調整後再次調用
result = await interactive_feedback(
    project_directory="./my-project",
    summary="根據您的建議，我已修改了錯誤處理邏輯，請再次確認",
    timeout=600
)
```

#### 2. 智能會話切換
```mermaid
flowchart TD
    CALL[AI 再次呼叫] --> CREATE[create_session<br/>建立新會話]
    CREATE --> OLD{舊會話有 WebSocket?}
    OLD -->|是| TRANSFER[把連線轉給新會話]
    OLD -->|否| PENDING[標記待送的會話更新]
    TRANSFER --> NOTIFY[smart_open_browser<br/>送出 session_updated]
    PENDING --> OPEN[開啟瀏覽器<br/>新連線建立後送出 session_updated]
    NOTIFY --> REFRESH[前端局部更新內容]
    OPEN --> REFRESH
```

#### 3. 前端無縫更新
前端收到 `action` 為 `new_session_created` 的 `session_updated` 時（`app.js` 的 `_originalHandleSessionUpdated()`）：
1. 播放音效通知（`audioManager.playNotification()`），並送出瀏覽器通知（`notificationManager.notifyNewSession()`）
2. 顯示新會話訊息
3. 500 毫秒後更新 `currentSessionId`、呼叫 `refreshPageContent()` 更新 AI 摘要等內容、`clearFeedback()` 清空表單，並把回饋狀態設回等待中（`FEEDBACK_WAITING`）
4. 有開啟會話逾時時重新啟動計時，最後呼叫 `checkAndStartAutoSubmit()` 檢查自動提交

WebSocket 連線不會重建。

## 🚀 新功能交互流程

### 自動提交功能流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant UI as 前端介面
    participant ASM as AutoSubmitManager
    participant PM as PromptManager
    participant WS as WebSocket

    Note over User,WS: 🔧 設定自動提交
    User->>UI: 在提示詞設定把某個提示詞設為自動提交
    UI->>PM: setAutoSubmitPrompt(id)
    UI->>UI: settingsManager.set autoSubmitPromptId、autoSubmitEnabled
    User->>UI: 設定倒數秒數（autoSubmitTimeout）
    Note over UI: 設定經 SettingsManager 存到 ui_settings.json

    Note over User,WS: ⏰ 自動提交執行
    WS->>UI: session_updated（AI 新呼叫）
    UI->>UI: checkAndStartAutoSubmit()
    UI->>PM: getPromptById(autoSubmitPromptId)
    alt 已啟用、提示詞標記為自動提交、狀態為等待回饋
        UI->>ASM: start(timeout, promptId)
        ASM->>UI: showCountdownDisplay()
        loop 每秒更新
            ASM->>UI: updateCountdownDisplay(remaining)
        end
        ASM->>UI: 時間到 performAutoSubmit()
        UI->>UI: 填入提示詞到輸入框並 submitFeedback('auto')
        UI->>WS: submit_feedback
        UI->>PM: usePrompt(promptId)
    else 條件不滿足
        UI->>ASM: stop()
    end
```

會話歷史裡每則使用者訊息的提交方式（`submission_method`）看這次提交是誰觸發的：只有倒數到期由 `performAutoSubmit()` 送出時記為 `auto`；倒數期間使用者自己按送出或按 Ctrl+Enter，記為 `manual`（`FeedbackApp.collectFeedbackData()`、`recordUserMessage()`）。

### 提示詞管理流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant UI as 設定介面
    participant PM as PromptManager
    participant Modal as PromptModal
    participant Storage as SettingsManager

    Note over User,Storage: 📝 新增提示詞
    User->>UI: 點選「新增提示詞」
    UI->>Modal: showAddModal()
    Modal->>User: 顯示編輯表單
    User->>Modal: 輸入名稱和內容
    Modal->>PM: addPrompt(name, content)
    PM->>PM: 驗證資料和唯一性
    PM->>Storage: set('promptSettings') 存到 ui_settings.json
    PM->>UI: 觸發 addPromptsChangeCallback() 註冊的回呼
    UI->>UI: refreshPromptList()

    Note over User,Storage: ✏️ 編輯提示詞
    User->>UI: 點選編輯按鈕
    UI->>Modal: showEditModal(prompt)
    Modal->>User: 顯示預填表單
    User->>Modal: 修改內容
    Modal->>PM: updatePrompt(id, name, content)
    PM->>Storage: 更新 ui_settings.json
    PM->>UI: 觸發回呼更新介面

    Note over User,Storage: 🎯 使用提示詞
    User->>UI: 在輸入區點選提示詞按鈕
    UI->>PM: getPromptsSortedByUsage()
    PM-->>UI: 回傳排序後列表
    UI->>Modal: showSelectModal(prompts)
    User->>Modal: 選擇提示詞
    Modal->>PM: usePrompt(id)
    PM->>Storage: 更新使用記錄
    Modal->>UI: 填入提示詞內容
```

### 會話管理流程（v2.4.3 重構增強）

```mermaid
sequenceDiagram
    participant AI as AI 助手
    participant Server as MCP 伺服器
    participant SM as SessionManager
    participant SDM as SessionDataManager
    participant SUR as SessionUIRenderer
    participant UI as 前端介面

    Note over AI,UI: 📊 會話生命週期管理
    AI->>Server: interactive_feedback()
    Server->>Server: create_session()
    Server->>UI: session_updated 或 status_update（WebSocket）
    UI->>SM: updateCurrentSession(session_info) 或 updateStatusInfo(status_info)
    SM->>SDM: updateCurrentSession() 或 updateStatusInfo()
    SDM->>SM: onSessionChange 回呼
    SM->>SUR: renderCurrentSession()
    SUR->>UI: 更新會話顯示（頁籤化設計）

    Note over AI,UI: 📝 使用者回饋處理
    UI->>Server: submit_feedback（WebSocket）
    UI->>SDM: addUserMessage()
    SDM->>Server: POST /api/add-user-message
    Server->>AI: 回傳回饋結果
    Server->>UI: notification（回饋已收到）

    Note over AI,UI: 📚 會話歷史管理
    Server->>UI: status_update
    UI->>SM: updateStatusInfo(status_info)
    SM->>SDM: updateStatusInfo()
    alt 狀態為已提交、已完成、逾時、錯誤或已過期
        SDM->>SDM: handleSessionCompleted()
        SDM->>SDM: addSessionToHistory()，saveToServer() 存回伺服器
        SDM->>SDM: updateStats()
        SDM->>SM: onHistoryChange 回呼
        SM->>SUR: renderSessionHistory()
    else 會話未完成
        SDM->>SDM: updateCurrentSession()
    end

    Note over AI,UI: 🔍 載入歷史與儲存期限
    SDM->>Server: GET /api/load-session-history、/api/all-sessions
    Server-->>SDM: 存檔的會話、目前行程的即時會話
    SDM->>SDM: 依 session_id 合併（同一會話以即時資料為準）
    SDM->>SDM: 不在即時清單的未結束會話標為 closed（已斷線）
    SDM->>SDM: cleanupExpiredSessions() 移除超過儲存期限的會話
    SDM->>Server: POST /api/save-session-history
    UI->>SDM: getSessionHistory()
    SDM-->>UI: 回傳歷史列表
    UI->>SDM: getStats()
    SDM-->>UI: 回傳統計資料
    UI->>SDM: exportSessionHistory()
    SDM-->>UI: 下載 JSON 檔並回傳檔名
```

### 音效通知系統流程（v2.4.3 新增）

```mermaid
sequenceDiagram
    participant WS as WebSocket
    participant AM as AudioManager
    participant ASU as AudioSettingsUI
    participant AUDIO as Web Audio API
    participant User as 使用者

    Note over WS,User: 🔊 音效通知觸發流程
    WS->>AM: 收到 session_updated 時 app.js 呼叫 playNotification()
    alt 音效通知已啟用
        AM->>AM: getAudioById(selectedAudioId)，找不到時改用 default-beep
        AM->>AUDIO: playAudioSmart() 建立 Audio 物件並設定音量
        AUDIO->>User: 播放通知音效
        Note over AM: 瀏覽器擋下自動播放時先排入待播清單，使用者互動後再播
    else 音效通知已停用
        AM->>AM: 直接結束
    end

    Note over WS,User: 🎵 音效設定管理
    User->>ASU: 開啟音效設定
    ASU->>AM: getSettings()
    AM-->>ASU: 回傳目前設定
    ASU->>User: 顯示設定介面

    User->>ASU: 調整音量
    ASU->>AM: setVolume(volume)
    AM->>AM: saveAudioSettings()

    User->>ASU: 選擇音效
    ASU->>AM: setSelectedAudio(audioId)
    AM->>AM: saveAudioSettings()

    User->>ASU: 測試播放
    ASU->>AM: getAudioById(audioId) 後 playAudio(audioData)
    AM->>AUDIO: 播放測試音效
    AUDIO->>User: 播放音效

    Note over WS,User: 📁 自訂音效管理
    User->>ASU: 上傳自訂音效
    ASU->>User: showAudioNameModal() 輸入音效名稱
    ASU->>AM: addCustomAudio(name, file)
    AM->>AM: isValidAudioFile()、檢查名稱重複
    AM->>AM: fileToBase64()
    AM->>AM: saveAudioSettings() 經 SettingsManager 存到 ui_settings.json
    ASU->>User: 顯示上傳成功
```

### 智能記憶功能流程（v2.4.3 新增）

```mermaid
sequenceDiagram
    participant User as 使用者
    participant TEXTAREA as 輸入框
    participant THM as TextareaHeightManager
    participant RO as ResizeObserver
    participant SM as SettingsManager

    Note over User,SM: 📏 輸入框高度記憶
    User->>TEXTAREA: 調整輸入框高度
    TEXTAREA->>RO: 觸發尺寸變化事件
    RO->>THM: handleResize(element)
    THM->>THM: debounce(500ms)
    THM->>SM: set(settingKey, height)
    SM->>SM: POST /api/save-settings 存到 ui_settings.json

    Note over User,SM: 🔄 高度恢復
    User->>User: 重新載入頁面
    THM->>SM: get(settingKey)
    SM-->>THM: 回傳儲存的高度
    THM->>TEXTAREA: 應用儲存的高度
    TEXTAREA->>User: 顯示恢復的高度

    Note over User,SM: 📋 一鍵複製功能
    User->>User: 點選專案路徑
    User->>User: 觸發複製事件
    User->>User: 複製到剪貼簿
    User->>User: 顯示複製成功提示

    User->>User: 點選會話ID
    User->>User: 觸發複製事件
    User->>User: 複製到剪貼簿
    User->>User: 顯示複製成功提示（多語言）
```

## 📊 狀態同步機制

### WebSocket 訊息類型

```mermaid
graph LR
    subgraph "伺服器 → 用戶端"
        CE[connection_established<br/>連線建立]
        SU[session_updated<br/>會話更新<br/>🔊 觸發音效通知]
        ST[status_update<br/>狀態更新]
        HR[heartbeat_response<br/>心跳回應]
        PI[ping<br/>連線檢測]
        NO[notification<br/>回饋已收到／重複提交／會話清理]
    end

    subgraph "用戶端 → 伺服器"
        SF[submit_feedback<br/>提交回饋]
        GS[get_status<br/>查詢狀態]
        HB[heartbeat<br/>心跳檢測]
        PO[pong<br/>回應 ping]
        UT[user_timeout<br/>會話逾時]
        UTS[update_timeout_settings<br/>逾時設定]
    end
```

### 狀態轉換圖

前端回饋狀態（`Utils.CONSTANTS`）只有三種：`FEEDBACK_WAITING`（`waiting_for_feedback`）、`FEEDBACK_PROCESSING`（`processing`）、`FEEDBACK_SUBMITTED`（`feedback_submitted`）。自動提交倒數不是獨立狀態，而是在等待狀態下由 `autoSubmitManager` 計時。

```mermaid
stateDiagram-v2
    [*] --> FEEDBACK_WAITING: 會話建立/更新
    FEEDBACK_WAITING --> FEEDBACK_PROCESSING: 手動提交或自動提交倒數到期
    FEEDBACK_PROCESSING --> FEEDBACK_SUBMITTED: 收到回饋已收到的 notification
    FEEDBACK_PROCESSING --> FEEDBACK_WAITING: 送出失敗或 WebSocket 斷線
    FEEDBACK_WAITING --> FEEDBACK_SUBMITTED: 伺服器狀態為已提交或已完成
    FEEDBACK_SUBMITTED --> FEEDBACK_WAITING: 新會話更新

    note right of FEEDBACK_WAITING
        自動提交倒數在此狀態下執行：
        - 功能已啟用
        - 提示詞標記為自動提交
        - 時間到呼叫 performAutoSubmit()
    end note
```

## 🛡️ 錯誤處理和恢復

### 連線斷線處理
重連由 `WebSocketManager`（`websocket-manager.js`）處理，連線狀態經 `onConnectionStatusChange` 交給 `ConnectionMonitor`（`connection-monitor.js`）顯示：

- **關閉碼決定是否重連**（`handleClose()`、`shouldAttemptReconnect()`）：
  - `4004`（沒有活躍會話）：顯示斷線，不重連
  - `1000`（正常關閉，例如伺服器清理會話時以 `reason="會話清理"` 關閉）：不重連
  - 瀏覽器回報離線（`offline` 事件）：不重連；恢復上線（`online` 事件）時把重連次數歸零，1 秒後重新連線
  - 其他關閉碼：重連，直到 `MAX_RECONNECT_ATTEMPTS`（5 次）用完，之後提示「WebSocket 連線失敗，請重新整理頁面重試」
- **延遲**：指數退避，`DEFAULT_RECONNECT_DELAY`（1000 毫秒）× 2^(第 N 次 − 1)，加上 0–1 秒隨機抖動，最多 30 秒
- **連線成功**（`handleOpen()`）：重連次數與延遲歸零，啟動心跳並送出 `get_status` 取得目前狀態
- **心跳**：連線期間每 `DEFAULT_HEARTBEAT_FREQUENCY`（60000 毫秒）送一次 `{type: 'heartbeat', timestamp}`；收到 `heartbeat_response` 時，`ConnectionMonitor` 以送出到收到的時間差計算延遲
- **前端回饋狀態**：斷線時若正處於 `FEEDBACK_PROCESSING`，`FeedbackApp.handleWebSocketClose()` 把它設回 `FEEDBACK_WAITING`，避免卡在送出中

**連線狀態顯示**（`ConnectionMonitor`）：
- 右上角狀態文字「重新連線中... (第N次)」的 N 是這次斷線後的重連次數（`reconnectAttempt`），恢復連線時歸零
- 統計面板的「重新連線」是整頁累計的重連次數（`reconnectCount`），只有重新載入頁面才歸零
- 「連線時間」在連線期間每秒更新；斷線時停止並顯示 `--:--`，重連成功後從 0 起算

伺服器端另有斷線寬限：連線中斷後若在 `CLIENT_DISCONNECT_GRACE_SECONDS`（75 秒）內沒有重新連上，視為使用者關閉介面並結束等待（`WebFeedbackSession.on_client_disconnected()`）。

### 逾時處理
`WebFeedbackSession.wait_for_feedback(timeout)` 在執行緒中等待 `feedback_completed`，實際等待時間比 `timeout` 提早一點結束（超過 30 秒提早 5 秒，否則提早 1 秒，最少 1 秒），避免與 MCP 層的逾時競爭：
- 收到回饋：回傳 `{"interactive_feedback", "images", "settings"}`
- 逾時、使用者設定的會話逾時到期、或斷線寬限到期（視為關閉介面）：清理資源後拋出 `TimeoutError`

`interactive_feedback` 接到 `TimeoutError` 時不當成錯誤，回傳「使用者未回應」的文字，要求 AI 結束任務、不要再次呼叫本工具。

## 🎯 效能優化

### 連線重用
- **WebSocket 連線保持**: 避免重複建立連線
- **會話狀態繼承**: 新會話繼承舊會話的連線
- **智能瀏覽器開啟**: 檢測活躍分頁，避免重複開啟

### 資源管理
- **自動清理機制**: 逾時會話自動清理
- **記憶體優化**: 單一活躍會話模式
- **行程管理**: 優雅的行程啟動和關閉

## 🔒 安全性考量

### 資料安全
- **本機綁定**: 伺服器只綁定 127.0.0.1，減少攻擊面
- **輸入驗證**: 嚴格的參數類型檢查和資料清理
- **檔案上傳安全**: 圖片格式驗證和大小限制
- **命令執行**: 已於 v2.6.1 移除，不再提供

### 網路安全
- **WebSocket 驗證**: 連線來源驗證
- **跨來源控制**: 沒有 CORS 中介層；非 GET/HEAD/OPTIONS 的 `/api/*` 檢查 Origin 並要求 `application/json`
- **逾時保護**: 防止長時間佔用資源
- **錯誤訊息過濾**: 避免敏感資訊洩露

## 🚀 效能優化總結

### 連線重用優勢
- **減少啟動時間**: Web 伺服器啟動後持續執行，之後的呼叫不必重新啟動伺服器與瀏覽器
- **單一活躍會話**: 同一時間只有一個目前會話
- **提升使用者體驗**: 無縫會話切換，保持操作狀態
- **減少網路開銷**: WebSocket 連線保持和重用

### 資源管理效率
- **智能清理**: 自動檢測和清理過期資源
- **動態埠分配**: 避免埠衝突，支援並行開發
- **錯誤恢復**: 優雅的錯誤處理和自動重連
- **跨平台適配**: WSL 中改用 Windows 瀏覽器開啟介面，其他環境用 Python 的 `webbrowser`

---

## 📚 相關文件

- **[系統架構總覽](./system-overview.md)** - 了解整體架構設計理念和技術棧
- **[元件詳細說明](./component-details.md)** - 深入了解各層元件的具體實作
- **[API 參考文件](./api-reference.md)** - 完整的 API 端點和參數說明
- **[部署指南](./deployment-guide.md)** - 環境設定和部署最佳實踐
