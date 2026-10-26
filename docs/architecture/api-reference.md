# API 參考文件

本文件提供 MCP Feedback Enhanced 的完整 API 參考，包括 MCP 工具、Web API、WebSocket 通訊協定和內部 API。

## 📡 MCP 工具 API

MCP Feedback Enhanced 基於 FastMCP 框架實作，提供標準的 MCP 協定支援。

### interactive_feedback

AI 助手與使用者進行互動式回饋的核心 MCP 工具。

#### 函式簽名
```python
async def interactive_feedback(
    project_directory: str = ".",
    summary: str = "我已完成了您請求的任務。",
    timeout: int = 600,
) -> list[TextContent | ImageContent]
```

#### 參數說明

| 參數 | 型別 | 必需 | 預設值 | 描述 |
|------|------|------|--------|------|
| `project_directory` | `str` | ❌ | `"."` | 專案目錄路徑，用於上下文顯示；路徑不存在時改用伺服器的工作目錄 |
| `summary` | `str` | ❌ | `"我已完成了您請求的任務。"` | AI 助手的工作摘要，向使用者說明目前狀態 |
| `timeout` | `int` | ❌ | `600` | 等待使用者回饋的逾時時間（秒），伺服器端鉗制在 60–86400，無法解析時用 600 |

#### 回傳值
MCP 內容列表：
- 有回饋時：第一項是彙整文字回饋與圖片資訊的 `TextContent`，之後每張圖片一個 `ImageContent`
- 等待逾時或使用者關閉介面：一個 `TextContent`，說明使用者未回應並要求 AI 結束任務、不要再呼叫本工具
- 使用者送出空白回饋：`TextContent("使用者未提供任何回饋內容。")`

#### 使用範例
```python
# 基本呼叫
result = await interactive_feedback(
    project_directory="./my-web-app",
    summary="我已完成登入功能的實作，包括表單驗證和錯誤處理。請檢查程式碼品質。"
)

# 自訂逾時
result = await interactive_feedback(
    project_directory="./complex-project",
    summary="重構完成，請詳細測試所有功能模組。",
    timeout=1200  # 20分鐘
)
```

#### 錯誤處理
工具不會把例外拋給 MCP 用戶端：逾時、使用者關閉介面與其他錯誤都轉成 `TextContent` 說明後回傳。

### get_system_info

```python
def get_system_info() -> str
```

回傳 JSON 字串，包含平台、Python 版本、是否為 WSL／遠端環境、介面類型與幾個環境偵測用的環境變數值。

## 🌐 Web API

### HTTP 端點

#### GET /
回饋頁面主入口。有活躍會話時渲染回饋頁面（`feedback.html`），沒有時渲染等待頁面（`index.html`）。

**回應**: `200 OK`（HTML）

#### GET /static/{path}
靜態資源服務（CSS、JS、圖片等）。

**參數**:
- `path`: 靜態資源路徑

**回應**: `200 OK` 或 `404 Not Found`

#### GET /api/translations
取得多語言翻譯資源。

**回應**: `200 OK`
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
取得目前會話狀態。

**回應**: `200 OK`
```json
{
    "has_session": true,
    "status": "active",
    "session_info": {
        "project_directory": "./my-project",
        "summary": "程式碼審查完成",
        "feedback_completed": false
    }
}
```

沒有活躍會話時回傳 `{"has_session": false, "status": "no_session", "messageCode": ...}`。

#### GET /api/current-session
取得目前會話詳細資訊。

**回應**: `200 OK`
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_directory": "./my-project",
    "summary": "程式碼審查完成",
    "feedback_completed": false,
    "images_count": 0
}
```

**錯誤回應**: `404 Not Found`
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
| GET | `/api/all-sessions` | 目前行程中所有會話的即時狀態（`{"sessions": [...]}`，含 `user_messages`） |
| POST | `/api/add-user-message` | 把一則使用者訊息記錄加到目前會話 |
| GET | `/api/load-settings` | 讀取 `~/.config/mcp-feedback-enhanced/ui_settings.json`，不存在時回 `{}` |
| POST | `/api/save-settings` | 以請求內容覆寫 `ui_settings.json` |
| POST | `/api/clear-settings` | 刪除 `ui_settings.json` |
| GET | `/api/load-session-history` | 讀取 `session_history.json`，回傳 `{"sessions": [...], "lastCleanup": ...}` |
| POST | `/api/save-session-history` | 把 `{"sessions": [...], "lastCleanup": ...}` 寫入 `session_history.json` |
| GET | `/api/log-level` | 讀取 `ui_settings.json` 的 `logLevel` |
| POST | `/api/log-level` | 更新 `ui_settings.json` 的 `logLevel` |

### WebSocket API

#### 連線端點
```
ws://127.0.0.1:{port}/ws
```

連線時必須已有活躍會話，否則以代碼 `4004` 關閉；瀏覽器帶來的 Origin 不是本服務時以代碼 `4003` 關閉。一個會話只保留最新的一條連線。

#### 訊息格式
所有訊息都是 JSON 物件，以 `type` 區分種類，其他欄位與 `type` 放在同一層，沒有 `data` 包裝：
```json
{
    "type": "heartbeat",
    "timestamp": 1703123456789
}
```

### 📤 用戶端 → 伺服器訊息

| `type` | 其他欄位 | 伺服器處理 |
|--------|----------|------------|
| `submit_feedback` | `feedback`、`images`、`settings` | 提交回饋，見下方說明 |
| `get_status` | 無 | 回傳 `status_update` |
| `heartbeat` | `timestamp` | 更新心跳時間，回傳 `heartbeat_response` |
| `pong` | `timestamp` | 回應伺服器的 `ping`，只寫除錯日誌 |
| `user_timeout` | `timestamp` | 前端的會話逾時到期；伺服器結束等待並清理會話 |
| `update_timeout_settings` | `settings.enabled`、`settings.seconds` | 更新會話逾時設定 |

其他 `type` 只寫除錯日誌，不做處理。

#### submit_feedback
提交使用者回饋。

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

**欄位說明**:
- `feedback`: 使用者回饋文字內容
- `images`: 圖片物件陣列；`data` 是不含 `data:` 前綴的 Base64。缺少 `name`、`data` 或 `size` 的項目會被略過
- `settings.image_size_limit`: 圖片大小上限（位元組），`0` 表示不限制；超過上限的圖片會被略過
- `settings.enable_base64_detail`: 是否在回給 AI 的文字中附上圖片的完整 Base64

### 📥 伺服器 → 用戶端訊息

| `type` | 欄位 | 何時傳送 |
|--------|------|----------|
| `connection_established` | `messageCode` | WebSocket 連線建立後 |
| `session_updated` | `action`（`"new_session_created"`）、`messageCode`、`session_info` | AI 再次呼叫 `interactive_feedback` 時通知既有分頁；連線時若有待送的會話更新也會送出 |
| `status_update` | `status_info` | 連線建立且沒有待送的會話更新時，或回應 `get_status` |
| `heartbeat_response` | `timestamp`（原樣回傳用戶端送來的值） | 回應 `heartbeat` |
| `ping` | `timestamp` | 伺服器檢查分頁是否仍連線時；用戶端回 `pong` |
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
        "message": "等待使用者回饋",
        "feedback_completed": false,
        "has_websocket": true,
        "created_at": 1703123456.789,
        "last_activity": 1703123456.789,
        "project_directory": "./my-project",
        "summary": "程式碼審查完成",
        "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

#### 會話歷史不走 WebSocket
沒有 `session_history` 訊息，自動提交、提示詞、音效、輸入框高度也都沒有對應的 WebSocket 訊息，這些都在前端處理，設定經 HTTP 存到 `ui_settings.json`。會話歷史由前端透過 HTTP 讀寫：
- `GET /api/load-session-history`、`POST /api/save-session-history`：存檔的歷史（`~/.config/mcp-feedback-enhanced/session_history.json`）
- `GET /api/all-sessions`：目前行程中的即時會話

## 🔧 內部 API

### WebUIManager API

#### create_session()
```python
def create_session(self, project_directory: str, summary: str) -> str
```

建立新的回饋會話並設為目前會話，回傳 `session_id`。

#### smart_open_browser()
```python
async def smart_open_browser(self, url: str) -> bool
```

智慧開啟瀏覽器，避免重複開啟。

**回傳值**:
- `True`: 桌面模式，或偵測到活躍分頁（已送 `session_updated` 通知該分頁），未開啟新視窗
- `False`: 開啟了新瀏覽器視窗

### WebFeedbackSession API

#### submit_feedback()
```python
async def submit_feedback(
    self,
    feedback: str,
    images: list[dict[str, Any]],
    settings: dict[str, Any] | None = None,
) -> None
```

提交使用者回饋到會話。同一會話重複提交會被忽略，並送出 `notification`（`severity: "warning"`）。

#### wait_for_feedback()
```python
async def wait_for_feedback(self, timeout: int = 600) -> dict[str, Any]
```

等待使用者回饋完成，回傳 `{"interactive_feedback": str, "images": list, "settings": dict}`。逾時或會話未取得回饋即結束時拋出 `TimeoutError`。

#### WebSocket 連線
沒有 `add_websocket()`。`/ws` 端點把連線直接指定給 `session.websocket`，新連線會取代舊連線。

### PromptManager API

#### addPrompt()
```javascript
PromptManager.prototype.addPrompt = function(name, content) // => Object
```

新增提示詞到管理器。

**參數**:
- `name`: 提示詞名稱（必須唯一）
- `content`: 提示詞內容

**回傳值**: 新建的提示詞物件。名稱或內容為空、名稱重複時拋出 `Error`。

#### updatePrompt()
```javascript
PromptManager.prototype.updatePrompt = function(id, name, content) // => Object
```

更新現有提示詞，回傳更新後的提示詞。找不到、名稱或內容為空、名稱重複時拋出 `Error`。

#### deletePrompt()
```javascript
PromptManager.prototype.deletePrompt = function(id) // => Object
```

刪除指定提示詞，回傳被刪除的提示詞。找不到時拋出 `Error`。

#### usePrompt()
```javascript
PromptManager.prototype.usePrompt = function(id) // => Object
```

使用提示詞（更新最近使用記錄），回傳該提示詞。找不到時拋出 `Error`。

#### getPromptsSortedByUsage()
```javascript
PromptManager.prototype.getPromptsSortedByUsage = function() // => Array<Object>
```

回傳排序後的提示詞副本：自動提交提示詞優先，其次依最近使用時間由新到舊，從未使用的排在後面並依建立時間由新到舊。

### SessionManager API（v2.4.3 重構增強）

#### getCurrentSession()
```javascript
SessionDataManager.prototype.getCurrentSession = function() // => Object|null
```

取得目前活躍會話資訊。`SessionManager.prototype.getCurrentSession()` 轉呼叫此方法。

#### getSessionHistory()
```javascript
SessionDataManager.prototype.getSessionHistory = function() // => Array<Object>
```

回傳目前會話歷史的副本，本身不過濾；儲存期限在載入時由 `cleanupExpiredSessions()` 套用。

#### getStats()
```javascript
SessionDataManager.prototype.getStats = function() // => { todayCount, averageDuration }
```

回傳統計資訊的副本：`todayCount` 是今日會話數，`averageDuration` 是今日會話的平均持續時間（秒）。沒有 `getSessionStats()`；`SessionManager.prototype.getStats()` 轉呼叫此方法。

#### exportSessionHistory()
```javascript
SessionDataManager.prototype.exportSessionHistory = function() // => string
```

沒有參數，只匯出 JSON。把全部會話歷史下載為 `session-history-YYYY-MM-DD.json`，回傳該檔名。檔案內容是 `{ exportedAt, sessionCount, sessions }`；只有開啟使用者訊息記錄時，各會話才包含 `user_messages` 與 `user_message_count`。`SessionManager.prototype.exportSessionHistory()` 轉呼叫此方法並顯示成功或失敗訊息；單一會話改用 `exportSingleSession(sessionId)`。

#### cleanupExpiredSessions()
```javascript
SessionDataManager.prototype.cleanupExpiredSessions = function() // => number
```

移除超過儲存期限的會話。儲存期限讀取設定 `sessionHistoryRetentionHours`（預設 72 小時），以秒比較；會話時間依序取 `saved_at`、`completed_at`、`created_at`（毫秒會先換成秒）。有清掉會話時立即呼叫 `saveToServer()` 存回 `/api/save-session-history`。`loadFromServer()` 合併存檔與即時會話後會呼叫它。

**回傳值**: 清理的會話數量

### AudioManager API（v2.4.3 新增）

#### playNotification()
```javascript
AudioManager.prototype.playNotification = function() // => undefined
```

播放選用的通知音效；音效通知停用時不播放，找不到選用的音效時改播 `default-beep`。

#### setEnabled()、setVolume()、setSelectedAudio()
```javascript
AudioManager.prototype.setEnabled = function(enabled)
AudioManager.prototype.setVolume = function(volume)
AudioManager.prototype.setSelectedAudio = function(audioId)
```

分別更新音效開關、音量與選用的音效，並存回設定。音量超出 0-100、或找不到指定音效時拋出 `Error`。沒有一次更新全部的 `updateSettings()`。

#### addCustomAudio()
```javascript
AudioManager.prototype.addCustomAudio = function(name, file) // => Promise<Object>
```

新增自訂音效。

**參數**:
- `name`: 音效名稱，不可和既有自訂音效重複，也不可和任一語言的預設音效名稱（例如「經典提示音」、"Classic Beep"）相同
- `file`: 瀏覽器的 `File` 物件，類型須為 `audio/mp3`、`audio/mpeg`、`audio/wav` 或 `audio/ogg`；會轉成 Base64 存進設定

**回傳值**: resolve 為新增的音效物件（`id`、`name`、`data`、`mimeType`、`createdAt`、`isDefault: false`）；名稱或檔案為空、格式不支援、名稱重複時 reject。

#### removeCustomAudio()
```javascript
AudioManager.prototype.removeCustomAudio = function(audioId) // => Object
```

刪除自訂音效，回傳被刪除的音效。找不到時拋出 `Error`。

#### getAllAudios()
```javascript
AudioManager.prototype.getAllAudios = function() // => Array<Object>
```

取得所有可用音效（內建 + 自訂）。

### TextareaHeightManager API（v2.4.3 新增）

#### registerTextarea()
```javascript
TextareaHeightManager.prototype.registerTextarea = function(elementId, settingKey) // => boolean
```

註冊 textarea 元素進行高度管理，並套用 `settingKey` 已儲存的高度。高度變化經 500 毫秒 debounce 後以 `settingsManager.set(settingKey, height)` 儲存；沒有公開的 `saveHeight()`／`loadHeight()`。

#### unregisterTextarea()
```javascript
TextareaHeightManager.prototype.unregisterTextarea = function(elementId) // => boolean
```

取消註冊 textarea 元素。

### AutoSubmitManager API

`FeedbackApp.initializeAutoSubmitManager()` 建立的物件（`app.autoSubmitManager`），不是獨立類別。

#### start()
```javascript
start: function(timeoutSeconds, promptId)
```

啟動自動提交倒數計時器。

#### stop()
```javascript
stop: function()
```

停止自動提交倒數計時器。

#### pause()、resume()、togglePause()
```javascript
pause: function()
resume: function()
togglePause: function()
```

暫停、繼續或切換倒數。沒有 `updateSettings()`；自動提交設定存在 `ui_settings.json` 的 `autoSubmitEnabled`、`autoSubmitTimeout`、`autoSubmitPromptId`。

## 📊 狀態碼和錯誤碼

### HTTP 狀態碼
- `200 OK`: 請求成功
- `400 Bad Request`: `POST /api/log-level` 的等級無效
- `403 Forbidden`: 非 GET/HEAD/OPTIONS 的 `/api/*` 請求 Origin 不受信任
- `404 Not Found`: 資源不存在，或 `/api/current-session`、`/api/add-user-message` 沒有活躍會話
- `415 Unsupported Media Type`: 非 GET/HEAD/OPTIONS 的 `/api/*` 請求不是 `application/json`
- `500 Internal Server Error`: 伺服器內部錯誤

### WebSocket 關閉碼與錯誤通知
- `4003`: Origin 不受信任
- `4004`: 沒有活躍會話

沒有 `error` 訊息類型或錯誤碼列舉；伺服器以 `notification` 訊息的 `code` 與 `severity` 告知前端。

### 會話狀態
```python
class SessionStatus(Enum):
    WAITING = "waiting"                        # 等待中
    ACTIVE = "active"                          # 活躍狀態
    FEEDBACK_SUBMITTED = "feedback_submitted"  # 已提交反饋
    COMPLETED = "completed"                    # 已完成
    ERROR = "error"                            # 錯誤（終態）
    TIMEOUT = "timeout"                        # 超時（終態）
    EXPIRED = "expired"                        # 已過期（終態）
```

會話歷史沿用這些狀態值；載入歷史時，不在即時清單裡的未結束會話會被標為 `closed`。

### 提示詞與自動提交
沒有提示詞狀態或自動提交狀態的列舉。提示詞以布林欄位 `isAutoSubmit` 標示自動提交；自動提交設定是 `ui_settings.json` 的 `autoSubmitEnabled`、`autoSubmitTimeout`、`autoSubmitPromptId`。

### 音效通知
沒有音效通知狀態的列舉，開關是設定 `audioNotificationEnabled`。

### 隱私等級（v2.4.3 新增）
設定 `userMessagePrivacyLevel` 的字串值：
- `full`: 完整記錄
- `basic`: 基本記錄
- `disabled`: 停用記錄

## 🔒 安全考慮

### 輸入驗證
- 回饋內容沒有長度限制
- 圖片大小限制：由設定 `imageSizeLimit` 決定，可選不限制（預設）、1MB、3MB、5MB；伺服器依 `settings.image_size_limit` 略過超過上限的圖片
- 圖片數量限制：前端最多 10 張
- 支援的圖片格式：前端接受任何 `image/*` 類型
- 提示詞：名稱與內容不可為空、名稱不可重複，沒有長度或數量上限
- **音效檔案限制（v2.4.3 新增）**：
  - 支援格式：MP3, WAV, OGG（`audio/mp3`、`audio/mpeg`、`audio/wav`、`audio/ogg`）
  - 名稱不可重複，沒有檔案大小、數量或名稱長度上限
- **會話歷史限制（v2.4.3 新增）**：
  - 預設儲存期限：72 小時
  - 可選儲存期限：24 小時、72 小時、7 天（168 小時）、30 天（720 小時）
  - 單個會話的使用者訊息數沒有上限

### 資源保護
- WebSocket 連線：每個會話只保留最新的一條連線
- 會話逾時自動清理
- 記憶體使用監控

### 跨域設定
沒有 CORS 中介層，伺服器不核准任何跨來源請求。非 GET/HEAD/OPTIONS 的 `/api/*` 與 `/ws` 會檢查 Origin，詳見 [部署指南的安全設定](./deployment-guide.md#安全設定)。

---

## 📚 相關文件

- **[系統架構總覽](./system-overview.md)** - 了解整體架構設計理念和技術棧
- **[元件詳細說明](./component-details.md)** - 深入了解各層元件的具體實作
- **[互動流程文件](./interaction-flows.md)** - 詳細的使用者互動和系統流程
- **[部署指南](./deployment-guide.md)** - 環境設定和部署最佳實踐
