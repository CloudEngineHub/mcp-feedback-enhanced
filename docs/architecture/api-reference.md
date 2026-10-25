# API 參考文檔

本文檔提供 MCP Feedback Enhanced 的完整 API 參考，包括 MCP 工具、Web API、WebSocket 通信協議和內部 API 接口。

## 📡 MCP 工具 API

MCP Feedback Enhanced 基於 FastMCP 框架實現，提供標準的 MCP 協議支援。

### interactive_feedback

AI 助手與用戶進行交互式回饋的核心 MCP 工具。

#### 函數簽名
```python
async def interactive_feedback(
    project_directory: str = ".",
    summary: str = "我已完成了您請求的任務。",
    timeout: int = 600,
) -> list[TextContent | ImageContent]
```

#### 參數說明

| 參數 | 類型 | 必需 | 預設值 | 描述 |
|------|------|------|--------|------|
| `project_directory` | `str` | ❌ | `"."` | 專案目錄路徑，用於上下文顯示；路徑不存在時改用伺服器的工作目錄 |
| `summary` | `str` | ❌ | `"我已完成了您請求的任務。"` | AI 助手的工作摘要，向用戶說明當前狀態 |
| `timeout` | `int` | ❌ | `600` | 等待用戶回饋的超時時間（秒），伺服器端鉗制在 60–86400，無法解析時用 600 |

#### 返回值
MCP 內容列表：
- 有回饋時：第一項是彙整文字回饋與圖片資訊的 `TextContent`，之後每張圖片一個 `ImageContent`
- 等待逾時或用戶關閉介面：一個 `TextContent`，說明使用者未回應並要求 AI 結束任務、不要再呼叫本工具
- 用戶送出空白回饋：`TextContent("用戶未提供任何回饋內容。")`

#### 使用示例
```python
# 基本調用
result = await interactive_feedback(
    project_directory="./my-web-app",
    summary="我已完成登入功能的實現，包括表單驗證和錯誤處理。請檢查代碼品質。"
)

# 自定義超時
result = await interactive_feedback(
    project_directory="./complex-project",
    summary="重構完成，請詳細測試所有功能模組。",
    timeout=1200  # 20分鐘
)
```

#### 錯誤處理
工具不會把例外拋給 MCP 客戶端：逾時、用戶關閉介面與其他錯誤都轉成 `TextContent` 說明後回傳。

### get_system_info

```python
def get_system_info() -> str
```

回傳 JSON 字串，包含平台、Python 版本、是否為 WSL／遠端環境、介面類型與幾個環境偵測用的環境變數值。

## 🌐 Web API

### HTTP 端點

#### GET /
回饋頁面主入口。有活躍會話時渲染回饋頁面（`feedback.html`），沒有時渲染等待頁面（`index.html`）。

**響應**: `200 OK`（HTML）

#### GET /static/{path}
靜態資源服務（CSS、JS、圖片等）。

**參數**:
- `path`: 靜態資源路徑

**響應**: `200 OK` 或 `404 Not Found`

#### GET /api/translations
獲取多語言翻譯資源。

**響應**: `200 OK`
```json
{
    "zh-TW": {
        "app": {
            "title": "MCP Feedback Enhanced"
        }
    },
    "en": {
        "app": {
            "title": "MCP Interactive Feedback System"
        }
    },
    "zh-CN": {
        "app": {
            "title": "MCP 交互反馈系统"
        }
    }
}
```

#### GET /api/session-status
獲取當前會話狀態。

**響應**: `200 OK`
```json
{
    "has_session": true,
    "status": "active",
    "session_info": {
        "project_directory": "./my-project",
        "summary": "代碼審查完成",
        "feedback_completed": false
    }
}
```

沒有活躍會話時回傳 `{"has_session": false, "status": "no_session", "messageCode": ...}`。

#### GET /api/current-session
獲取當前會話詳細信息。

**響應**: `200 OK`
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_directory": "./my-project",
    "summary": "代碼審查完成",
    "feedback_completed": false,
    "images_count": 0
}
```

**錯誤響應**: `404 Not Found`
```json
{
    "error": "No active session",
    "messageCode": "..."
}
```

#### 其他端點

非 GET/HEAD/OPTIONS 的 `/api/*` 請求必須帶 `Content-Type: application/json`（否則 `415`），瀏覽器帶來的 Origin 必須指向本服務（否則 `403`）。

| 方法 | 路徑 | 用途 |
|------|------|------|
| GET | `/api/all-sessions` | 目前行程中所有會話的實時狀態（`{"sessions": [...]}`，含 `user_messages`） |
| POST | `/api/add-user-message` | 把一則用戶訊息記錄加到當前會話 |
| GET | `/api/load-settings` | 讀取 `~/.config/mcp-feedback-enhanced/ui_settings.json`，不存在時回 `{}` |
| POST | `/api/save-settings` | 以請求內容覆寫 `ui_settings.json` |
| POST | `/api/clear-settings` | 刪除 `ui_settings.json` |
| GET | `/api/load-session-history` | 讀取 `session_history.json`，回傳 `{"sessions": [...], "lastCleanup": ...}` |
| POST | `/api/save-session-history` | 把 `{"sessions": [...], "lastCleanup": ...}` 寫入 `session_history.json` |
| GET | `/api/log-level` | 讀取 `ui_settings.json` 的 `logLevel` |
| POST | `/api/log-level` | 更新 `ui_settings.json` 的 `logLevel` |

### WebSocket API

#### 連接端點
```
ws://127.0.0.1:{port}/ws
```

連線時必須已有活躍會話，否則以代碼 `4004` 關閉；瀏覽器帶來的 Origin 不是本服務時以代碼 `4003` 關閉。一個會話只保留最新的一條連線。

#### 訊息格式
所有訊息都是 JSON 物件，以 `type` 區分種類，其他欄位與 `type` 放在同一層，沒有 `data` 包裝：
```json
{
    "type": "heartbeat",
    "tabId": "tab_1703123456789_abc",
    "timestamp": 1703123456789
}
```

### 📤 客戶端 → 服務器訊息

| `type` | 其他欄位 | 伺服器處理 |
|--------|----------|------------|
| `submit_feedback` | `feedback`、`images`、`settings` | 提交回饋，見下方說明 |
| `get_status` | 無 | 回傳 `status_update` |
| `heartbeat` | `tabId`、`timestamp` | 更新心跳時間，回傳 `heartbeat_response` |
| `pong` | `timestamp` | 回應伺服器的 `ping`，只寫除錯日誌 |
| `user_timeout` | `timestamp` | 前端的會話超時到期；伺服器結束等待並清理會話 |
| `update_timeout_settings` | `settings.enabled`、`settings.seconds` | 更新會話超時設定 |

其他 `type` 只寫除錯日誌，不做處理。

#### submit_feedback
提交用戶回饋。

```json
{
    "type": "submit_feedback",
    "feedback": "這個功能很好，但建議增加輸入驗證。",
    "images": [
        {
            "name": "screenshot.png",
            "size": 12345,
            "type": "image/png",
            "data": "iVBORw0KGgoAAAANSUhEUgAA..."
        }
    ],
    "settings": {
        "image_size_limit": 0,
        "enable_base64_detail": false
    }
}
```

**字段說明**:
- `feedback`: 用戶回饋文字內容
- `images`: 圖片物件陣列；`data` 是不含 `data:` 前綴的 Base64。缺少 `name`、`data` 或 `size` 的項目會被略過
- `settings.image_size_limit`: 圖片大小上限（位元組），`0` 表示不限制；超過上限的圖片會被略過
- `settings.enable_base64_detail`: 是否在回給 AI 的文字中附上圖片的完整 Base64

### 📥 服務器 → 客戶端訊息

| `type` | 欄位 | 何時發送 |
|--------|------|----------|
| `connection_established` | `messageCode` | WebSocket 連線建立後 |
| `session_updated` | `action`（`"new_session_created"`）、`messageCode`、`session_info` | AI 再次呼叫 `interactive_feedback` 時通知既有分頁；連線時若有待送的會話更新也會送出 |
| `status_update` | `status_info` | 連線建立且沒有待送的會話更新時，或回應 `get_status` |
| `heartbeat_response` | `timestamp`（原樣回傳客戶端送來的值） | 回應 `heartbeat` |
| `ping` | `timestamp` | 伺服器檢查分頁是否仍連線時；客戶端回 `pong` |
| `notification` | `code`、`severity`，以及 `status` 或 `reason` | 回饋已收到（`severity: "success"`）、重複提交被忽略（`"warning"`）、會話被清理（`"warning"`，`reason` 為清理原因） |

#### session_updated
```json
{
    "type": "session_updated",
    "action": "new_session_created",
    "messageCode": "session.created",
    "session_info": {
        "session_id": "new-session-id",
        "project_directory": "./my-project",
        "summary": "根據您的建議，我已修改了錯誤處理邏輯。",
        "status": "waiting"
    }
}
```

#### status_update
```json
{
    "type": "status_update",
    "status_info": {
        "status": "waiting",
        "message": "等待用戶回饋",
        "feedback_completed": false,
        "has_websocket": true,
        "created_at": 1703123456.789,
        "last_activity": 1703123456.789,
        "project_directory": "./my-project",
        "summary": "代碼審查完成",
        "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

#### 會話歷史不走 WebSocket
沒有 `session_history` 訊息，自動提交、提示詞、音效、輸入框高度也都沒有對應的 WebSocket 訊息，這些都在前端處理，設定經 HTTP 存到 `ui_settings.json`。會話歷史由前端透過 HTTP 讀寫：
- `GET /api/load-session-history`、`POST /api/save-session-history`：存檔的歷史（`~/.config/mcp-feedback-enhanced/session_history.json`）
- `GET /api/all-sessions`：目前行程中的實時會話

## 🔧 內部 API

### WebUIManager API

#### create_session()
```python
async def create_session(
    self,
    summary: str,
    project_directory: str
) -> WebFeedbackSession
```

創建新的回饋會話。

#### smart_open_browser()
```python
async def smart_open_browser(self, url: str) -> bool
```

智能開啟瀏覽器，避免重複開啟。

**返回值**:
- `True`: 檢測到活躍標籤頁，未開啟新視窗
- `False`: 開啟了新瀏覽器視窗

### WebFeedbackSession API

#### submit_feedback()
```python
async def submit_feedback(
    self,
    feedback: str,
    images: List[str],
    settings: dict
) -> None
```

提交用戶回饋到會話。

#### wait_for_feedback()
```python
async def wait_for_feedback(self, timeout: int = 600) -> dict
```

等待用戶回饋完成。

#### add_websocket()
```python
def add_websocket(self, websocket: WebSocket) -> None
```

添加 WebSocket 連接到會話。

### PromptManager API

#### addPrompt()
```python
def addPrompt(self, name: str, content: str) -> dict
```

新增提示詞到管理器。

**參數**:
- `name`: 提示詞名稱（必須唯一）
- `content`: 提示詞內容

**返回值**: 新建的提示詞對象

#### updatePrompt()
```python
def updatePrompt(self, id: str, name: str, content: str) -> dict
```

更新現有提示詞。

#### deletePrompt()
```python
def deletePrompt(self, id: str) -> bool
```

刪除指定提示詞。

#### usePrompt()
```python
def usePrompt(self, id: str) -> dict
```

使用提示詞（更新最近使用記錄）。

#### getPromptsSortedByUsage()
```python
def getPromptsSortedByUsage(self) -> List[dict]
```

獲取按使用頻率排序的提示詞列表，自動提交提示詞優先顯示。

### SessionManager API（v2.4.3 重構增強）

#### getCurrentSession()
```python
def getCurrentSession(self) -> dict
```

獲取當前活躍會話信息。

#### getSessionHistory()
```javascript
SessionDataManager.prototype.getSessionHistory = function() // => Array<Object>
```

回傳目前會話歷史的副本，本身不過濾；保存期限在載入時由 `cleanupExpiredSessions()` 套用。

#### getSessionStats()
```python
def getSessionStats(self) -> dict
```

獲取會話統計信息，包含今日統計和平均時長。

#### exportSessionHistory()
```python
def exportSessionHistory(self, format: str = "json") -> str
```

匯出會話歷史數據。

**參數**:
- `format`: 匯出格式（json, csv）

#### cleanupExpiredSessions()
```javascript
SessionDataManager.prototype.cleanupExpiredSessions = function() // => number
```

移除超過保存期限的會話。保存期限讀取設定 `sessionHistoryRetentionHours`（預設 72 小時），以秒比較；會話時間依序取 `saved_at`、`completed_at`、`created_at`（毫秒會先換成秒）。有清掉會話時立即呼叫 `saveToServer()` 存回 `/api/save-session-history`。`loadFromServer()` 合併存檔與實時會話後會呼叫它。

**返回值**: 清理的會話數量

### AudioManager API（v2.4.3 新增）

#### playNotification()
```python
def playNotification(self) -> None
```

播放通知音效。

#### updateSettings()
```python
def updateSettings(self, enabled: bool, volume: int, selectedAudioId: str) -> None
```

更新音效設定。

#### addCustomAudio()
```python
def addCustomAudio(self, name: str, audioData: str, mimeType: str) -> dict
```

新增自訂音效。

**參數**:
- `name`: 音效名稱
- `audioData`: Base64 編碼的音效數據
- `mimeType`: MIME 類型（audio/mp3, audio/wav, audio/ogg）

#### deleteCustomAudio()
```python
def deleteCustomAudio(self, audioId: str) -> bool
```

刪除自訂音效。

#### getAllAudios()
```python
def getAllAudios(self) -> List[dict]
```

獲取所有可用音效（內建 + 自訂）。

### TextareaHeightManager API（v2.4.3 新增）

#### registerTextarea()
```python
def registerTextarea(self, elementId: str, settingKey: str) -> bool
```

註冊 textarea 元素進行高度管理。

#### saveHeight()
```python
def saveHeight(self, elementId: str, height: int) -> None
```

保存 textarea 高度到設定。

#### loadHeight()
```python
def loadHeight(self, elementId: str) -> int
```

從設定載入 textarea 高度。

#### unregisterTextarea()
```python
def unregisterTextarea(self, elementId: str) -> None
```

取消註冊 textarea 元素。

### AutoSubmitManager API

#### start()
```python
def start(self, timeoutSeconds: int, promptId: str) -> None
```

啟動自動提交倒數計時器。

#### stop()
```python
def stop(self) -> None
```

停止自動提交倒數計時器。

#### updateSettings()
```python
def updateSettings(self, enabled: bool, timeout: int, promptId: str) -> None
```

更新自動提交設定。

## 📊 狀態碼和錯誤碼

### HTTP 狀態碼
- `200 OK`: 請求成功
- `302 Found`: 重定向
- `404 Not Found`: 資源不存在
- `500 Internal Server Error`: 服務器內部錯誤

### WebSocket 錯誤碼
```python
class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
```

### 會話狀態
```python
class SessionStatus:
    WAITING = "FEEDBACK_WAITING"
    PROCESSING = "FEEDBACK_PROCESSING"
    SUBMITTED = "FEEDBACK_SUBMITTED"
    ERROR = "ERROR"
```

### 提示詞狀態
```python
class PromptStatus:
    ACTIVE = "active"           # 活躍提示詞
    AUTO_SUBMIT = "auto_submit" # 自動提交提示詞
    ARCHIVED = "archived"       # 已歸檔提示詞
```

### 自動提交狀態
```python
class AutoSubmitStatus:
    DISABLED = "disabled"       # 已停用
    ENABLED = "enabled"         # 已啟用
    COUNTDOWN = "countdown"     # 倒數計時中
    COMPLETED = "completed"     # 已完成提交
```

### 音效通知狀態（v2.4.3 新增）
```python
class AudioNotificationStatus:
    DISABLED = "disabled"       # 已停用
    ENABLED = "enabled"         # 已啟用
    PLAYING = "playing"         # 播放中
    ERROR = "error"             # 播放錯誤
```

### 會話歷史狀態（v2.4.3 新增）
```python
class SessionHistoryStatus:
    ACTIVE = "active"           # 活躍會話
    COMPLETED = "completed"     # 已完成會話
    EXPIRED = "expired"         # 已過期會話
    ARCHIVED = "archived"       # 已歸檔會話
```

### 隱私等級（v2.4.3 新增）
```python
class PrivacyLevel:
    FULL = "full"               # 完整記錄
    BASIC = "basic"             # 基本記錄
    DISABLED = "disabled"       # 停用記錄
```

## 🔒 安全考慮

### 輸入驗證
- 回饋內容長度限制：最大 10,000 字符
- 圖片大小限制：單張最大 5MB
- 圖片數量限制：最多 10 張
- 支援的圖片格式：PNG, JPEG, GIF, WebP
- 提示詞名稱長度限制：最大 100 字符
- 提示詞內容長度限制：最大 5,000 字符
- 提示詞數量限制：最多 50 個
- **音效文件限制（v2.4.3 新增）**：
  - 支援格式：MP3, WAV, OGG
  - 單個文件最大：2MB
  - 自訂音效數量：最多 20 個
  - 音效名稱長度：最大 50 字符
- **會話歷史限制（v2.4.3 新增）**：
  - 預設保存期限：72 小時
  - 可選保存期限：24 小時、72 小時、7 天（168 小時）、30 天（720 小時）
  - 單個會話最大用戶訊息數：100 條

### 資源保護
- WebSocket 連接數限制：每會話最多 5 個連接
- 會話超時自動清理
- 內存使用監控和限制

### 跨域設置
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境，生產環境應限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 相關文檔

- **[系統架構總覽](./system-overview.md)** - 了解整體架構設計理念和技術棧
- **[組件詳細說明](./component-details.md)** - 深入了解各層組件的具體實現
- **[交互流程文檔](./interaction-flows.md)** - 詳細的用戶交互和系統流程
- **[部署指南](./deployment-guide.md)** - 環境配置和部署最佳實踐

---

**版本**: 2.4.3
**最後更新**: 2025年6月14日
**維護者**: Minidoracat
**API 版本**: v1
**協議支援**: MCP 2.0+, WebSocket, HTTP/1.1, Web Audio API
**v2.4.3 新功能**: 音效通知系統、會話管理重構、智能記憶功能、一鍵複製
**歷史功能**: 自動提交、提示詞管理、會話管理、語系切換優化
