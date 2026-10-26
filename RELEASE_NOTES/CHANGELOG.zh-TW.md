# 更新日誌 (繁體中文)

本文件記錄了 **MCP Feedback Enhanced** 的所有版本更新內容。

## [v2.8.5] - 未發布 - 統計面板、介面語言與繁中用語修正

### 🌟 版本亮點
- 詳細統計面板的狀態、會話數、今日平均持續時間、重新連線次數與連線時間反映實際狀況；右上角的重新連線狀態顯示實際次數。
- `MCP_LANGUAGE` 現在真的決定網頁介面語言（回饋頁與等待頁），介面切換只在目前頁面有效；時間、日期、複製的會話內容，以及原本寫死中文的介面文字，依介面語言顯示，切換語言後立即生效。
- 繁中介面，以及後端回給介面與 AI 的繁中訊息，改用台灣用語。
- 自動提交倒數期間手動送出的回饋，不再被記成自動提交。
- 原生 Windows 設了 `WSLENV` 時，不再被誤判成 WSL 而改用 `cmd.exe` 開瀏覽器。

### 🐛 問題修復
- **詳細統計面板的「狀態」永遠是「等待中」、「會話」永遠是 1**：兩個欄位原本從頁面上已不存在的元素複製，一直停在預設值。現在「狀態」跟著目前會話（送出回饋後變成已提交，新會話進來變回等待中），「會話」是會話歷史清單的筆數（含目前會話），切換語言時一起換。
- **「今日平均持續時間」一直是 0，切換語言後單位也沒換**：統計只看伺服器回傳的會話沒有的 duration 欄位，數值沒變時也不會重繪。現在和會話歷史的持續時間用同一個定義（建立時間到結束時間，沒有結束時間時用送出回饋的時間），捨去方式也相同（只有一個會話時兩邊顯示一樣），切換語言後立即換成新語言的單位。
- **「重新連線」次數在恢復連線後歸零、「連線時間」連線後停在 00:00**：「重新連線」現在是整頁累計；「連線時間」連線期間每秒更新，斷線時顯示 --:--，重新連線後從新連線起算。
- **右上角連線狀態顯示「重連中... (第{attempt}次)」**：重新連線時沒代入次數，斷線期間切換語言也會套上原字串。現在顯示「重新連線中... (第3次)」這類實際次數，每次斷線重新起算，切換語言後同樣代入。
- **時間與日期跟著瀏覽器語系**：英文介面也顯示「下午9:51:30」。目前會話卡片、會話歷史、「回饋已提交」的時間，以及提示詞與自訂音效的日期，改依介面語言格式化，切換語言後立即生效。
- **複製會話內容、複製使用者內容寫死簡中**：現在依介面語言輸出。複製會話內容的使用者訊息原本顯示成 [object Object]，狀態與建立時間是原始值；現在顯示訊息內容與狀態文字，時間和複製使用者內容一樣改用會話詳情視窗的 YYYY/MM/DD HH:MM:SS。
- **自動提交倒數期間手動送出，被記成「自動提交」**：前端用「自動提交倒數是否正在跑」判斷提交方式，只要有提示詞設成自動提交、倒數開始後手動按送出，會話歷史、會話詳情、匯出檔與伺服器記錄的 `submission_method` 都是 `auto`。現在依實際觸發來源記錄：倒數到期自動送出記 `auto`，按送出按鈕或 Ctrl+Enter 記 `manual`；連線還沒就緒、先暫存再送出的回饋也保留原本的方式。
- **圖示按鈕在套用翻譯後變成文字**：提示詞設定的自動提交按鈕，⏰／⏸️ 圖示被換成「設定為自動提交」等字樣，提示也寫死中文；會話卡片的「複製會話內容」「複製使用者內容」按鈕，📋／📝 圖示連同文字一起被換成純文字，`aria-label` 寫死中文，切換語言也不會換。現在圖示保留，說明放在滑鼠提示與螢幕閱讀器標籤，並依介面語言顯示。
- **頁面的 `<html lang>` 一直是 `zh-CN`**：兩個範本寫死 `lang="zh-CN"`，第一次開頁時也不會更新，只有在介面上切換語言才會改；繁中或英文介面被宣告成簡中，螢幕閱讀器與瀏覽器會用錯的語言朗讀、斷字與選字型。現在範本預設 `zh-TW`（與前端預設語言一致），套用翻譯時一併把 `lang` 設成目前的介面語言，第一次載入與切換語言都會更新。
- **`MCP_LANGUAGE` 現在真的決定網頁介面語言**（[#189](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/189)）：v2.7.1 只調整了後端偵測順序，網頁介面仍由 `ui_settings.json` 的 `language` 或瀏覽器語言決定，設了 `MCP_LANGUAGE=en`／`zh-CN` 畫面還是繁中。現在伺服器把指定語言帶進回饋頁與等待頁（`<html lang>` 與 `data-forced-language`），第一次套用翻譯就是指定語言。指定期間語言選單仍可切換，但只在目前頁面有效，重新整理後回到指定語言；`ui_settings.json` 的 `language` 不會被切換、改其他設定或重設改動。
- **`MCP_LANGUAGE` 只接受 `zh-TW`、`zh-CN`、`en`**：去掉前後空白後必須完全相符，`ja`、`EN`、`zh_TW` 等值一律當作沒設。原本錯誤處理的備援路徑會直接回傳未驗證的值。
- **等待頁（還沒有會話時）支援三語**：等待說明原本寫死繁中，現在照 `MCP_LANGUAGE` → `ui_settings.json` 的 `language` → 瀏覽器語言 → 繁中的順序顯示。右上角的連線燈號一併移除：等待頁不建立 WebSocket，燈號永遠是紅色「連線中...」；也不再載入只有回饋頁用得到的腳本。
- **第一次開頁不再把瀏覽器語言寫進 `ui_settings.json`**：只有使用者在沒設 `MCP_LANGUAGE` 時切換語言才會存。
- **介面上寫死的中文**：會話詳情視窗的「(進行中)」、「未知」、「內容」、「字元」、複製按鈕與提示訊息，自訂音效清單的「建立於／格式」與播放／刪除按鈕提示，以及提示詞選擇視窗的「最近使用」改用翻譯；播放／刪除兩個圖示按鈕也加上螢幕閱讀器標籤。重設設定的確認框、測試通知失敗的提示、自動提交暫停的原因與狀態按鈕的「秒」、自動提交時間的驗證錯誤、圖片移除按鈕的提示與螢幕閱讀器標籤、提示詞視窗的關閉按鈕與空狀態、音效名稱輸入視窗，以及新增或上傳時提示詞、音效名稱重複等錯誤訊息，也改用翻譯。英文的自動提交暫停訊息原本直接把原因黏在 "Auto submit paused" 後面，現在是完整句子。
- **英文或簡中介面下，空白的 AI 摘要被存成介面文字**：AI 傳來空白摘要時，前端改讀會話卡片上的「AI 摘要: …」再用繁中字串去掉標籤；英文或簡中介面比對失效，摘要變成 "AI Summary: Loading..." 之類的文字，出現在會話卡片、歷史、詳情與匯出。現在直接使用伺服器的摘要與專案目錄，空白摘要依介面語言顯示「無摘要」。
- **開著自動提交時切換語言，狀態按鈕顯示成「已停用」**：按鈕範本固定套用「已停用」的翻譯，每次切換語言都會蓋掉「已啟用 (30秒)」。現在切換語言時依按鈕目前的狀態與秒數重畫，啟用與停用都跟著介面語言。
- **英文或簡中介面可以把自訂音效取成和預設音效相同的名稱**：重名檢查只比對繁中名稱「經典提示音」等，英文介面取名 "Classic Beep" 不會被擋，選單裡出現兩個同名音效。現在三種語言的預設音效名稱都算重名。
- **部分訊息顯示 key 名稱或未代入的參數**：補齊三個語系缺少的翻譯（簡中缺最多，例如系統與錯誤訊息、會話逾時；英文缺會話逾時與自動提交提示）。會話歷史已儲存、套用提示詞、一般錯誤三則訊息的參數寫成 {{count}}，與前端的 {count} 不符，console 會顯示「會話歷史已保存（{4} 個會話）」，現已修正。
- **繁中介面使用大陸用語**：繁中翻譯檔、頁面初始文字與翻譯尚未載入時的備用文字，把大陸用語換成台灣用語，例如「用戶」改「使用者」、「剪貼板」改「剪貼簿」、「當前會話」改「目前會話」、「連接」改「連線」、「超時」改「逾時」、「數據」改「資料」、「保存」改「儲存」、「點擊」改「點選」、「重置設定」改「重設設定」、「提示詞模板」改「提示詞範本」、「本地儲存」改「本機儲存」；「會話」維持不變。
- **後端回給介面與 AI 的繁中訊息使用大陸用語**：會話狀態訊息（例如「等待使用者回饋」「已送出回饋，等待下次 MCP 呼叫」「使用者設定的會話逾時」）、回給 AI 的回饋文字（「=== 使用者回饋 ===」「使用者取消了回饋。」「使用者未提供任何回饋內容。」「完整 Base64 長度: N 字元」）、等待逾時原因與繁中錯誤訊息（例如「網路連線出現問題」「操作逾時」「資料驗證失敗」）改用台灣用語；錯誤訊息的上下文前綴依介面語言分開，繁中為「檔案：」「技術細節：」，簡中為「文件：」「技术细节：」（簡中原本也會顯示繁體的「技術細節：」），英文不變；只寫進日誌的訊息不變。
- **關於頁仍寫著已在 v2.6.1 移除的「命令執行」**：描述改為目前的功能。
- **原生 Windows 設了 `WSLENV` 時被誤判成 WSL**：瀏覽器因此改用 `cmd.exe` 開啟。現在 `is_wsl_environment()` 只在 Linux 上判斷，`server.py` 重複的實作改用 `web/utils/browser.py` 的同一個函式。
- **`MCP_GZIP_LEVEL` 沒有作用**：設定讀到的壓縮等級（預設 6）沒有傳給 GZip 中介層，回應一直用 Starlette 預設的 9 壓縮。現在照設定的等級壓縮，未設定時改用 6。
- **`make test-func` 一定失敗**：它執行不帶參數的 `test`，只會印出說明並以 exit 1 結束。現在改跑 `test --web`（用專案的 .venv）。
- **Windows 上剛建立的暫存檔清不掉**：剛建立的檔案約有 1 成機率 mtime 比目前時間晚一點，計算出的年齡是負數，`cleanup_temp_files(max_age=0)`（程式結束時的全面清理）因此漏刪。現在年齡不會小於 0。
- **匯出的檔名日期少一天**：匯出會話歷史與單一會話時，檔名原本取 UTC 日期，台灣時間 00:00–08:00 匯出會少一天（例如本機 10/26 凌晨匯出得到 `session-history-2026-10-25.json`）；現在改用本機日期。匯出內容裡的時間欄位維持 UTC ISO 格式。
- **匯出單一會話後提示「會話歷史已匯出」**：容易誤以為匯出了整份歷史；改成「會話已匯出」，三個語系新增 `sessionHistory.management.exportSingleSuccess`。

### 📝 文件
- **架構文件與實作不符**：`docs/architecture/` 的部署指南與 API 參考文件寫了不存在的 `web` 子命令、`--port`／`--session-retention` 等參數、`MCP_FEEDBACK_*` 環境變數、`config.json`、`/health` 端點，以及 `session_history` 等 WebSocket 訊息，還說會話歷史存在 localStorage。現在改成實際的子命令（`server`、`test --web/--desktop`、`version`）、實際讀取的環境變數（`MCP_WEB_HOST`、`MCP_WEB_PORT` 等）、`~/.config/mcp-feedback-enhanced/` 下的 `ui_settings.json` 與 `session_history.json`，以及實際的 WebSocket 訊息類型與前端方法簽章（`getStats()`、無參數的 `exportSessionHistory()`）。架構文件也對照這一版的程式碼重新核對：移除已刪除的類別、方法與 `test --timeout` 參數，補上 `MCP_GZIP_LEVEL` 環境變數，開發工具段改寫成目前的 pre-commit（Ruff v0.17.2）與 CI 的 Ruff、mypy 檢查，引用的介面文字改成目前的繁中用語。
- **環境偵測、互動流程文件與元件詳細說明**：SSH 等遠端偵測只寫進除錯日誌，不會自動建立 SSH 隧道；WSL 只在 Linux 判斷並改用 Windows 瀏覽器開啟。互動流程文件與元件詳細說明改用實際的方法名與狀態；重新連線與統計面板的說明改成目前行為（右上角重新連線次數每次斷線重算、面板重新連線次數整頁累計、平均持續時間與歷史持續時間同一定義）。
- **系統架構總覽**：改正為 Web UI 加 Tauri 桌面模式，架構圖補上 Tauri 桌面殼並改成實際的模組連線（提示詞、音效、輸入框高度經設定 API 存檔，不走 WebSocket）；「技術亮點」與「維護特性」移除程式沒有的增量更新、狀態回滾、日誌輪轉、健康檢查與錯誤統計等說法；「效能」「安全性」「環境需求」刪掉沒有程式依據的數字與功能（例如「減少 60% 記憶體」「首屏 < 500ms」「SQL 注入防護」「CORS」），改寫成實際行為；其餘段落也對照實作改寫：單一活躍會話的狀態圖改成實際的清理時機，「持久化 Web UI」改寫成實際跨呼叫保留與不保留的內容（新會話會清空輸入框與圖片），刪掉「地區特定的 UI 佈局」「字體和排版優化」等沒有實作的本地化說法。元件詳細說明的「效能測試」改列實際有時間門檻的測試。另外移除已刪除的 TabManager 與各文件結尾過期的版本標示，架構文件索引列出已在 2026-10-26 對照 main 程式碼核對過的段落與對照的 commit。
- **三語 README**：環境偵測描述改成實際行為，`test` 範例補上 `--web`（不帶參數只會印出說明），並註明 `MCP_WEB_PORT=0` 由系統分配埠；刪除不存在的「總是在主螢幕中心顯示視窗」設定問答。
- **`MCP_LANGUAGE` 與介面語言的說明**：三語 README 與 `docs/architecture/` 的部署指南、元件詳細說明、互動流程文件、系統架構總覽，把語言分成兩條順序：網頁介面語言是 `MCP_LANGUAGE` → `ui_settings.json` 的 `language` → 瀏覽器語言 → 繁中，回給 AI 的錯誤訊息語言是 `MCP_LANGUAGE` → `LANG` 等環境變數 → 系統 locale → 繁中；註明只接受 `zh-TW`、`zh-CN`、`en`，其他值會被忽略，指定時介面切換只在目前頁面有效、不存檔，重新整理就回到指定語言。設定檔表格刪掉 `language.json`，並更正「localStorage 存介面語言」的說法（localStorage 只存通知設定）。
- **繁中文件改用台灣用語**：README.zh-TW、`docs/architecture/` 全部架構文件（索引、系統架構總覽、元件詳細說明、互動流程文件、API 參考文件、部署指南）、繁中 Cache 管理與 SSH Remote 指南、桌面建置與 GitHub Actions 工作流程說明、發佈說明管理文件與範本，敘述、圖表，以及程式碼區塊裡的中文註解與範例字串，都改用台灣用語（例如使用者、資料、設定、逾時、呼叫、互動、智慧、偵測、通訊、連接埠、建置）；「交互流程文件」改名為「互動流程文件」。和原始碼或 workflow 逐字相同的程式碼行維持原樣。
- **桌面建置指南故障排除範例對齊實際輸出**：`docs/DESKTOP_BUILD.md` 的錯誤訊息範例改成 `scripts/build_desktop.py` 實際印出的內容；建置失敗的解決步驟改成 `make clean-desktop` 清理後再 `make build-desktop`；修正 `make dev-setup`（安裝開發依賴與 pre-commit hooks）的說明。

### 🧹 程式碼清理
- 刪除 app.js 沒有呼叫者的會話更新與狀態更新防抖包裝，以及伺服器從不傳送的 feedback_received、desktop_close_request 訊息處理（含測試資料裡沒有測試使用的 feedback_received fixture）。
- 刪除 WebSocket 重新連線中處理「會話更新」關閉原因的分支（伺服器從不送這個原因），以及沒有呼叫端的連線統計重設函式。
- 刪除從未啟用的分頁管理模組 tab-manager.js（含呼叫已不存在路由的 /api/register-tab），以及只有它呼叫的 `Utils.generateId`。
- `test` 子命令刪除 `--timeout`：這個參數從來沒有被讀取，`test --web`／`--desktop` 本來就持續執行到 Ctrl+C。之後再帶 `--timeout` 會出現 `unrecognized arguments`。
- 刪除沒有呼叫者的後端程式碼：`SessionCleanupManager`、`CompressionMonitor`、`FeedbackResult`、`WebFeedbackSession.set_error`／`set_expired`、`server.py` 算完沒用到的 `fastmcp_settings`（FastMCP 會自己讀 `FASTMCP_LOG_LEVEL`），以及 `main_routes.py` 的 `_delayed_server_stop`。
- 刪除 `ResourceManager.register_process` 與跟著失去作用的處理程序追蹤（`unregister_process`、`cleanup_processes`、處理程序健康檢查、`processes` 統計欄位）：沒有任何地方註冊處理程序，追蹤表永遠是空的。
- 刪除永遠是空的全域分頁追蹤狀態（`WebUIManager.global_active_tabs`、`session.active_tabs`、`get_global_active_tabs_count`、`broadcast_to_active_tabs`）：TabManager 刪除後沒有任何東西會寫入。
- 刪除 `ErrorHandler` 的錯誤解決建議（`_ERROR_SOLUTIONS`、`get_error_solutions`、`get_i18n_error_solutions`）與 `create_error_response`：只有測試呼叫，正式流程不會顯示。錯誤類型的使用者訊息改為直接取內建訊息表：原本先查語系檔裡不存在的 `errors.types.*`，每次都退回內建表；三種語言的輸出不變。
- 刪除 Python `I18nManager` 用不到的部分：舊格式 key 對應（`_get_legacy_translation`，例如 `btn_submit_feedback` → `buttons.submitFeedback`，沒有任何程式傳舊格式 key，不少對應的新 key 也早已不存在）；`get_language_display_name` 與只被它使用的 `get_language_info`（查的 `languageNames.*`、`meta.displayName` 在三個語系都不存在）；沒有呼叫者的 `reload_translations`、`add_language` 與模組層級的 `reload_translations`。
- 刪除命令執行功能移除後留下的訊息代碼與翻譯：後端 `MessageCodes.COMMAND_*` 與對應的舊 key 映射、前端 `MessageCodes.COMMAND`、備用訊息表的 `error.command`，以及三個語系的 `commandStatus.*`、`error.command`、`errors.command_failed`、`notifications.command_executed`。後端 `MessageCodes` 另外刪除從來沒有送出過的 33 個常數，以及 `LEGACY_KEY_MAPPING` 中沒有人傳入的 5 個舊 key；後端實際送給前端的 25 個代碼不變。
- 刪除沒有任何頁面載入的檔案：前端 `static/js/modules/constants/message-codes.js`（`MessageCodes`、`createMessage` 等匯出沒有任何讀取者），以及 `templates/components/status-indicator.html` 和只有它會用到的 `status.completed.message`（三個語系）。
- 刪除 `utils.js` 走不到的備用訊息表（`getFallbackMessage`）與 `showMessage` 的訊息代碼物件分支：所有呼叫者都傳已翻譯好的字串，沒有人傳 `{ code }` 物件；`i18nManager` 在 `i18n.js` 載入時就建立，翻譯檔載入失敗時它也還在，不會落到這張表。表裡的 `settings.*` 也從來對不上後端實際送的 `settingsAPI.*`。
- 刪除每次都以 exit 1 結束的 `scripts/validate_message_codes.py`：它列出的缺漏都不會顯示給使用者（比對的是只在 i18n 未載入時才用到的前端備用訊息表，缺翻譯的代碼也只隨前端不顯示的通知送出），Makefile 與 CI 也沒有執行它。
- 刪除三個語系中沒有任何程式或範本使用的翻譯 key（繁中 82 個、簡中 77 個、英文 78 個），包括 `about.contact`、`summary.*`、`themes.*`、`autoRefresh.*`、`connection.*`、`notifications.*`、`errors.*` 等整段，以及只存在於單一語系的 `app.author`、`app.credits`、`autoSubmit.autoCommitNoPrompt` 等。刪除前逐一確認沒有動態組字、`data-i18n` 屬性或後端訊息代碼會用到。
- 函式內的 import 能移到檔頭的都移上去，刻意延遲的匯入（循環匯入、只在 Windows 有的模組、執行時才加進 sys.path 的開發環境桌面模組等）保留並註明理由；未使用的解包變數改名。
- 後端不再讀寫 `~/.config/mcp-feedback-enhanced/language.json`：寫入它的 `set_language()` 自 2025-06 起就沒有呼叫者，檔案只會殘留舊值。後端錯誤訊息的語言改為 `MCP_LANGUAGE` → `LANG`／`LC_ALL`／`LC_MESSAGES`／`LANGUAGE` → 系統語言 → 繁中；原本靠這個檔決定 AI 收到的錯誤訊息語言的使用者，會改看上述環境變數或系統語言，需要固定語言請設 `MCP_LANGUAGE`。既有的 `language.json` 不會被刪除，只是不再讀取；啟動時也不再建立 `~/.config/mcp-feedback-enhanced` 資料夾。
- 刪除前端讀取 localStorage `language` 的死路徑（全專案沒有寫入者）。
- 刪除前端沒有呼叫者的工具函式：`StatusUtils.formatStatusChangeLog`、`getStatusDescription`、`isValidStatusTransition` 與 `TimeUtils.formatRelativeTime`；其中幾個還帶著寫死的繁中字串。刪除前以全 repo 文字搜尋確認沒有呼叫或字串引用。

### 🔧 其他變更
- `highlights.txt`、`release_body.md` 移出版控並加進 `.gitignore`：兩者每次發版都由 publish.yml 重新產生，之前只是被發版 commit 的 `git add .` 一起帶進來。
- 開發依賴從已棄用的 `[tool.uv] dev-dependencies` 遷到 PEP 735 的 `[dependency-groups] dev`，`uv sync --dev` 不再印出棄用警告，裝到的套件不變。
- pre-commit 的 ruff 改用 v0.17.2（hook 名稱跟著改為 `ruff-check`），與 `uv run ruff`、CI 的結果一致。
- 開發依賴的 ruff、mypy 釘成 `ruff==0.17.2`、`mypy==2.4.0`：`uv.lock` 不進版控，CI 每次都重新解析版本，原本的 `>=` 會讓 lint 工具出新版時 CI 在程式碼沒變的情況下失敗，本機與 CI 的結果也可能不同。升級 ruff 時，`pyproject.toml` 與 `.pre-commit-config.yaml` 要一起改。
- Tests workflow 在 ubuntu 加上 `ruff check`、`ruff format --check` 與 `mypy`；原本既有的 mypy 錯誤已修正。
- `make clean-desktop`（`scripts/build_desktop.py --clean`）只清理、不建置：原本清理完會接著檢查 Rust 並建置桌面應用程式。`*.egg-info` 原本寫成字面路徑，一直清不到；現在改清 `src-tauri/src/` 底下的 egg-info，也就是以 setuptools 建置 `src-tauri` 時產生的位置（根目錄用 hatchling，不會產生 egg-info）。

### ✅ 測試
- 桌面啟動測試不再把整個行程的 `asyncio.sleep` 換成立即回傳：之前會讓前面測試留下的 uvicorn 伺服器執行緒變成忙迴圈搶 GIL，CI 的 ubuntu job 偶爾因此逾時 60 秒；現在只替換 `desktop_app` 模組自己的 `asyncio` 參照。
- `web_ui_manager` fixture 結束時停掉測試啟動的 uvicorn 伺服器：之前整合測試開的 8 個伺服器執行緒都活到 pytest 結束。
- i18n 測試改用三個語系都存在的 key，並要求翻譯結果不是 key 本身：原本的 `common.*`、`error.connection` 等 key 在語系檔裡不存在，測試只因為找不到 key 時會回傳 key 本身才通過。帶參數的翻譯改測 `error.generic` 的 `{error}` 有被替換。
- 錯誤訊息測試改為實際比對三種語言的內建訊息、檢查三個語系的文字各不相同，不再 mock 掉被測函式。
- 新增測試：`MCP_GZIP_LEVEL` 的等級 1 與 9 會傳到 GZip 中介層，同一份 `styles.css` 壓出來的大小不同；後端以 `messageCode` 回給前端顯示的 16 個訊息代碼，三個語系都要有翻譯；mtime 在未來的暫存檔，`max_age=0` 仍會被清掉。
- MCP 整合測試改用目前的 Python 直譯器啟動伺服器，不再透過 `uv run`：之前 `pyproject.toml` 有變動時，`uv run` 會先同步 `.venv` 並重寫本機的 `uv.lock`；`.venv` 裡的執行檔被編輯器的語言伺服器占用時同步失敗，`test_mcp_workflow.py` 的 9 個測試跟著失敗。
- 新增路由測試：合法 `MCP_LANGUAGE` 時回饋頁與等待頁都帶指定語言，不合法或沒設時不帶；語言偵測案例改為新順序並加入不合法值；新增舊 `language.json` 不生效、不建資料夾的測試。
- 刪除只測上述死碼的測試。

---

## [v2.8.4] - 2026-10-25 - 會話歷史保留與訊息處理修正

### 🌟 版本亮點
- 重開 MCP 伺服器後，會話歷史保留先前的會話（#177）；前一個行程留下、沒等到回饋的會話顯示「已斷線」。
- 會話歷史的持續時間改用真實的建立與結束時間，保存期限也真的會清掉過期記錄。
- 英文介面的持續時間加上空格與單複數（`7 seconds`、`1 minute 5 seconds`）。
- 新會話通知不再被心跳回應蓋掉，頁面會切到新會話。
- 切換語言後，當前會話卡片與會話歷史立即換成新語言。

### 🐛 問題修復
- **會話歷史只保存最近一次的記錄（#177）**：歷史清單原本只拿 `/api/all-sessions`，那裡只有目前伺服器行程記憶體裡的會話；重開 MCP 伺服器後舊會話就看不到，下一次存檔還會把 `session_history.json` 裡的舊會話洗掉。現在會合併存檔與目前的會話，同一個會話以伺服器資料為準、不重複，套用保存期限後再存回去。
- **重開伺服器後，前一個行程留下的會話一直顯示「等待中」**：合併存檔後，伺服器行程結束時還沒收到回饋的會話會帶著「等待中」留在歷史裡，直到保存期限到期，但它已經不會再收到回饋。現在載入歷史時，只要目前的會話清單讀取成功，不在清單裡且還沒結束的會話就標成「已斷線」並存回去；已提交、已完成、逾時、錯誤、已過期的會話不變，清單讀取失敗時不標記。
- **會話歷史的「約 N 分鐘」是估算值**：沒有結束時間時，持續時間是用會話 ID 雜湊算出來的固定數字。現在只用會話的建立時間與結束時間（沒有結束時間時用送出回饋的時間）計算，兩者缺一就不顯示。
- **英文介面的持續時間黏在一起**：數字、單位與各段之間沒有空格，會話歷史與「今日平均時長」顯示成 `7seconds`、`1minutes5seconds`。現在英文在數字與單位、各段之間加空格，數量為 1 時用單數（`1 minute 5 seconds`）；中文維持 `7秒`、`1分鐘5秒`。
- **會話歷史保存期限沒有作用**：時間戳有的是秒、有的是毫秒，比較時單位不一致，72 小時的期限實際上幾乎不會過期。現在統一以秒比較，超過期限的記錄會被清掉。
- **新會話通知可能被心跳回應蓋掉，頁面停在舊會話**：前端把所有 WebSocket 訊息放進同一個 50ms 防抖，50ms 內收到兩則時只處理後一則；新會話的 `session_updated` 或 `status_update` 後面緊接 `heartbeat_response`，前一則就被丟掉，頁面不會切到新會話。現在只有 `status_update`、`session_updated` 這兩種整份快照的訊息依類型各自防抖，同類連發仍只處理最後一則；`notification` 等其他類型直接處理，不同類型不再互相吃掉。
- **切換語言後當前會話卡片沒有跟著換**：「會話 ID／建立時間／專案／AI 摘要」等前綴與歷史的持續時間單位停在原本的語言，要等狀態變化或重新載入才更新。現在切換語言後立即換成新語言。

### ✅ 測試
- `conftest.py` —— 刪除 session 級的 `event_loop` fixture：沒有測試用到，pytest-asyncio 1.x 也不會拿它當事件迴圈。
- 開發依賴補上 `pytest-cov`：README 教的 `make test-cov` 之前會以 `unrecognized arguments: --cov=...` 失敗（exit 4），現在 `uv sync --dev` 後就能跑出覆蓋率表。
- 新增 `Tests` workflow：push 與 PR 到 main 時在 ubuntu-latest 與 windows-latest 跑完整 pytest；`test_resource_manager.py` 改用 `sys.executable` 啟動子行程，不再依賴 PATH 上有沒有 `python`。

---

## [v2.8.3] - 2026-10-25 - 送出後的會話狀態與重複提交

### 🌟 版本亮點
- 送出回饋後，會話歷史顯示「回饋已提交」而不是「處理中」，下一次 MCP 呼叫進來後變成「已完成」。
- 會話管理頁的「當前會話」卡片顯示伺服器上的實際狀態，重新載入或按 🔄 都會更新。
- 重新整理頁面後不能再送第二次回饋，不會再出現顯示送出成功、內容卻沒送到 AI 的情況。

### 🐛 問題修復
- **送出回饋後會話停在 `active`**：v2.6.0（#78）在 `waiting` 與 `feedback_submitted` 之間插入了 `active`，但沒有任何程式把會話推到 `active`，送出時只走一步，就停在 `active`。會話因此一直顯示「處理中」，下一次呼叫時舊會話不會變成 `completed`，送出後的清理計時器也不會重設。現在從 `waiting` 送出會經過 `active` 進入 `feedback_submitted`，仍遵守單向流轉規則。
- **會話管理頁的「當前會話」卡片停在預設值**：卡片只靠前端記憶的會話資料，重新載入後這份資料是空的，而伺服器送來的 `feedback_submitted` 狀態被當成「已完成」處理，只會更新已存在的資料，卡片就一直顯示「等待中」、建立時間「--:--:--」、AI 摘要「載入中…」；右上角 🔄 只是等一秒，什麼都沒抓。現在卡片改用 `/api/all-sessions` 裡標記為目前的會話：重新載入、按 🔄、送出回饋、下一個會話進來都會重抓伺服器資料。會話歷史原本只在筆數變化時重繪，送出後仍顯示「等待中」，現在狀態變了也會重繪。「回饋已提交」標籤補上與「已完成」相同的綠色樣式，切換語言時也會重新翻譯。
- **重新整理後還能再送一次回饋，第二次的內容送不到 AI**：重新載入頁面後，前端的回饋狀態重設成「等待中」，送出按鈕又能按；Ctrl+Enter 也只檢查 WebSocket 有沒有連上，沒重新整理也能重送。伺服器收到後照單全收，覆寫了回饋內容並把會話推到 `completed`，但 MCP 呼叫早已拿第一次的回饋返回，第二次的內容沒人讀到，介面卻顯示送出成功。現在伺服器收過回饋後會忽略之後的提交、不改內容也不推進狀態，並回覆「回饋已提交，請等待下次 MCP 調用」；前端重新載入時依伺服器狀態顯示「已提交」，按鈕與 Ctrl+Enter 都會擋下。下一次 MCP 呼叫的新會話照常送出。

### ✅ 測試
- `conftest.py` —— 整個測試階段把 `USERPROFILE`／`HOME` 指到 pytest 暫存目錄（子行程一併繼承），測試前後確認 `Path.home()`、語言設定檔與 `feedback_session.TEMP_DIR` 都不在真的家目錄底下，否則直接失敗；跑測試不再寫到使用者自己的設定。
- `helpers/mcp_client.py` —— 啟動 MCP 伺服器前把 `smart_browser_open`／`webbrowser.open` 換成只記錄網址的替身，不再開出真的瀏覽器；子行程加上 `MCP_TEST_MODE=true` 與 `MCP_WEB_PORT=0`，改由系統配埠，8765 被佔用時不會再把使用者正在用的實例關掉。
- `test_resource_manager.py` —— 原本把 pytest 自己的 PID 登記進 `ResourceManager`，它在 `atexit` 的清理會在 pytest 結束時終止這個行程，Windows 上即使全部通過也以 exit code 15 結束；改登記 fixture 開的短命子行程，每個測試後清空登記。
- `test_web_ui.py` —— 新增 `test_second_submission_is_ignored`：第二次提交不得覆寫回饋、圖片與設定，也不得推進狀態，只回 `feedback.alreadySubmitted`。既有的 `test_session_feedback_submission` 斷言送出後進入 `feedback_submitted`，修正前停在 `active` 而失敗，現在通過。
- 刪除三個測已移除實作的過時測試：`test_i18n_with_web_ui_manager`（`WebUIManager.i18n` 已移除）、`test_session_lifecycle`（`update_status` 已換成單向的 `next_step`，建立與切換會話由 `test_web_ui.py` 涵蓋）、`test_status_update_resets_timer`（測的是內部 Timer 物件有沒有換新）。
- `pytest.ini` 檔頭從 `[tool:pytest]` 改成 `[pytest]`：原本整份設定都被略過，現在 `testpaths`、strict markers／config、`asyncio_mode=auto`、`timeout=60`、`filterwarnings` 都會生效。
- `pyproject.toml` 的 `dev` extras 補上 `pytest-timeout>=2.1.0`，用 `pip install -e ".[dev]"` 安裝後跑測試，不再因 `timeout` 設定報 `Unknown config option`。

---

## [v2.8.2] - 2026-10-25 - 擋下跨站寫入 /api/*

### 🌟 版本亮點
- 跨站網頁不能再透過 `/api/*` 改寫設定、會話歷史或日誌等級，也就無法替使用者開啟自動提交。
- 會話詳情彈窗的欄位全部轉義，被竄改的會話歷史不會再當成 HTML 執行。

### 🔒 安全修復
- **修復跨站寫入 HTTP `/api/*` 與會話詳情的 stored XSS**：私下回報的 `GHSA-x999-258q-h9mh`。v2.6.1 的 Origin 檢查只涵蓋 `/ws`；`/api/save-settings`、`/api/save-session-history`、`/api/add-user-message`、`/api/clear-settings`、`/api/log-level` 既不看 Origin 也不看 Content-Type，`request.json()` 又不管宣告的型別照樣解析。`Content-Type: text/plain` 的跨站 POST 是 CORS simple request，瀏覽器不做 preflight 直接送出：網頁讀不到回應，但寫入會生效。攻擊者可藉此打開自動提交、換掉提示詞，讓合法的 WebSocket 連線自動送出回饋。
  - 所有打 `/api/*` 的非 GET／HEAD／OPTIONS 請求改走同一個 middleware，之後新增的端點也自動受保護：Origin 沒通過與 `/ws` 相同的檢查回 **403**；Content-Type 不是 `application/json` 回 **415**，逼跨站請求先 preflight，而伺服器不核准任何 CORS。未帶 Origin 的非瀏覽器客戶端與桌面 WebView 來源照舊放行。
  - 綁 `0.0.0.0` 或 `::` 時，Origin 的 host:port 必須等於請求的 Host header，不再只比埠；舊版任何同埠的外站都能通過，`/ws` 也一樣。
  - 會話詳情彈窗原本直接把 `session_id`、`status`、`project_directory` 等欄位插進 HTML，被竄改的 `session_history.json` 會變成 stored DOM XSS；現在全部轉義。共用的 `escapeHtml` 原本不轉義引號，放進屬性的值可以逃逸出去，改為連 `"`、`'` 一起轉義；同樣來自設定檔的提示詞 ID、自訂音效 ID 也一併轉義。
  - 感謝回報者提供詳盡的分析。

### ✅ 測試
- `test_cross_site_writes.py` —— 對每個寫入端點重放回報中的跨站請求，確認回 403／415 且檔案不變；同源 JSON、桌面 WebView、未帶 Origin 的請求照常成功；綁 `0.0.0.0` 時 Origin 等於 Host 才放行，`/ws` 也走同一條規則。設定檔一律寫在 `tmp_path`。
- `test_websocket_origin.py` —— 原本把「綁 0.0.0.0 只比埠」鎖成預期的案例改為 Host header 比對，新增 `::`、IPv6、Host 缺漏或格式錯誤的案例。

---

## [v2.8.1] - 2026-09-07 - 桌面回退的收尾修正

### 🌟 版本亮點
- stderr 提示改為受保護寫入，且 `sys.stderr` 為 None 時絕不改寫 stdout（MCP 協定通道）。
- 桌面殼只在非零退出時才算啟動失敗，使用者自己關窗不再被降級成 Web；失敗原因會印給使用者。

### 🐛 問題修復
- **降級提示改為受保護的 stderr 寫入**：v2.8.0 新增的兩處 `sys.stderr.write` 是 request path 上第一個未包 try/except 的 stderr 輸出；宿主已關閉 stderr pipe（EPIPE）時會讓整個 tool call 以例外結束，且 `MCP_DESKTOP_MODE` 來不及清掉、下次呼叫重演。改用與 `debug_log` 同樣靜默失敗的 `user_notice`，並把桌面啟動失敗的原因（exit code、stderr 尾段）一併印給使用者——Defender 隔離、glibc、Gatekeeper 三者處置完全不同，沒有原因就無法回報。
- **只有非零退出才算啟動失敗**：v2.8.0 把觀察期內任何退出都當失敗，使用者在視窗出現後兩秒內自己關掉（exit 0）也會被降級成 Web、與 v2.7.2 的關窗收尾語意衝突。現在 exit 0 沿用既有語意。
- **`sys.stderr` 為 None 時不再改寫 stdout**：`print(file=sys.stderr)` 在 pythonw 或宿主關閉 stderr 時會退回 `sys.stdout`——那是 MCP 協定通道，一行提示就足以讓客戶端解析失敗。`debug_log` 與 `user_notice` 改共用 `_write_stderr`，先抓住 stream、None 即返回。
- **stderr 尾段讀取加上限**：native 可能把 stderr 寫端留給 WebView 等後代程序，`read()` 會等到它們全部關閉；改用 `communicate(timeout=1)`，逾時只報 exit code。

### 🔧 其他變更
- README 三語：「安裝為應用程式」段落的「每次呼叫仍會開系統瀏覽器分頁」不符實際（分頁保持連線時會重用），改為「關掉應用程式視窗後下次呼叫會開在一般瀏覽器分頁」；「隨即退出」改為「隨即出錯退出」。

### ✅ 測試
- `test_desktop_fallback.py` —— stderr 斷言改在 `MCP_DEBUG=false` 下執行（conftest 預設開 debug，原測試在退回只印 debug log 時仍會通過）；早退測試改用暫存目錄的假 binary，不再依賴入庫的真 binary；新增：後代握著 stderr 不卡住、exit 0 不算失敗、兩份 launcher 位元組一致（`build_desktop.py` 複製曾讓兩份漂移）。
- `test_user_notice.py` —— `sys.stderr` 為 None 時 stdout 必須為空（`debug_log` 與 `user_notice` 皆測）、`user_notice` 不受 `MCP_DEBUG` 影響、stderr 已關閉時不拋出。

---

## [v2.8.0] - 2026-09-07 - 桌面應用程式進入僅維護狀態

### 🌟 版本亮點
- 桌面應用程式（Tauri 殼）自本版起 **maintenance-only**：不再新增功能，只修安全問題與完全無法啟動的相容性問題，預計 v3 移除；binary 仍隨本版出貨，想繼續使用請在 IDE 的 MCP 設定釘住版本（見 README「桌面應用程式維護狀態」）。
- 桌面殼起不來時（被防毒隔離、glibc 太舊、Gatekeeper 擋下、啟動後隨即退出）不再空等到逾時：本 process 自動改走瀏覽器，並把網址印到 stderr。

### 🐛 問題修復
- **桌面模式的瀏覽器回退從未生效**：`launch_desktop_app` 失敗時呼叫的 `open_browser` 會因為同一個 `MCP_DESKTOP_MODE` 環境變數而直接略過，使用者面前什麼都沒有，只能等到 timeout 收到「使用者未回應」。現在改在唯一的分流點處理：桌面啟動失敗 → 清掉本 process 的 `MCP_DESKTOP_MODE` → 走既有 `smart_open_browser`（含活躍分頁偵測與會話更新通知），之後每次呼叫都直接走 Web，不會再試桌面、再開新分頁；重啟 MCP 伺服器會重新讀 IDE 設定再試桌面。
- **native 啟動後隨即退出現在算啟動失敗**：兩份 Python launcher 原本只 `Popen` 再等兩秒，不看退出碼，被 Defender 隔離或缺 glibc 時仍回報「啟動成功」。現在觀察期內退出即失敗（附 exit code 與 stderr 尾段），交給上述回退。
- **瀏覽器也開不了時不再靜默**：`webbrowser.open` 回傳 False（例如無桌面環境的 SSH 主機）或 WSL 三種開啟方式全失敗時，無條件把網址印到 stderr，讓使用者能手動開啟；不再只在 `MCP_DEBUG=true` 時看得到。

### 🔧 其他變更
- `build-desktop.yml` 的觸發路徑排除 `src-tauri/python/**`：純 Python launcher 變更不再觸發四平台 native 重建與 binary 提交。
- 兩份 launcher（`src/mcp_feedback_enhanced/desktop_app/` 與 `src-tauri/python/`）同步為同一份；`build_desktop.py` 複製時不會再把發佈版退回舊寫法。
- README 三語新增「桌面應用程式維護狀態」與遷移說明；SECURITY.md 新增桌面元件維護範圍，支援版本表區分「最新 2.x」與「釘住的舊版不回補修正」。
- 本版**不**改 Rust、不改 native binary、不改 `/ws` 的桌面 WebView Origin 白名單、不改 renovate 設定。

### ✅ 測試
- `test_desktop_fallback.py` —— 桌面模組缺失時真的把網址交給瀏覽器並離開桌面模式、第二次呼叫重用既有分頁而非重試桌面、桌面健康時完全不碰瀏覽器、native 隨即退出視為失敗、瀏覽器開不了時網址印到 stderr。測試只攔最底層的 `webbrowser.open`，保留真實的桌面模式判斷，修正前四項確認失敗。

---

## [v2.7.2] - 2026-09-07 - 無人回應時明確收尾

### 🌟 版本亮點
- 等待逾時或使用者關閉介面時，工具改回傳明確的「使用者未回應，請結束任務」指令，工具描述的使用規則同步允許在此情況停止呼叫，客戶端不再把它當一般錯誤無限重試（#125）。
- 使用者關掉回饋分頁／視窗後，75 秒內未重新連線即結束等待，不再空等到 timeout（預設 10 分鐘）才回應（#162）。

### 🐛 問題修復
- **逾時回傳改為結束指令**（[#125](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/125)）：舊版把 `TimeoutError` 交給 `ErrorHandler`，回給模型的是「操作超時／增加超時時間設置／稍後重試」——客戶端照做就是再呼叫一次本工具，使用者不在時形成死循環。現在逾時（或下述的使用者關閉介面）回傳「使用者未回應（原因）。請視為使用者已離開：直接結束本次任務並輸出最終總結，不要再次呼叫 interactive_feedback」，附英文對照；工具描述的 USAGE RULES 也把「使用者未回應」列為可停止呼叫的條件，避免描述與回傳互相矛盾。只有等待本身的 `TimeoutError` 走這條路——取得回饋之後的存檔／圖片處理若拋出 `TimeoutError`（含 `OSError` 的 ETIMEDOUT），仍視為錯誤，不會把已到手的回饋說成沒回應。
- **關閉介面即結束等待**（[#162](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/162)）：舊版前端關閉時只清理本地資源，後端不知情，`wait_for_feedback` 一直等到 timeout。現在會話登記的 WebSocket 斷線後啟動 75 秒寬限計時器，期間重新連上（F5、短暫斷線、另一個分頁）即取消，逾期未重連才視為使用者關閉介面。75 秒的依據：後端只登記最新一條連線，舊分頁要等下一次應用層心跳（60 秒）才會被判定失效並重連，寬限必須大於「一次心跳週期 + 首次重連」，否則「開兩個分頁、關掉後開的那個」會把還在的使用者判成離開。這只保證正常網路下的路徑；首次重連就失敗而走完整個退避序列（1+2+4+8+16 秒 + jitter，再 31-36 秒）會超過寬限，視同斷線收尾。提交回饋與放棄等待在同一把 lock 下線性化：`Timer.cancel()` 攔不住已開始的回呼，故回呼以身分比對作廢；提交是原子寫入，等待端讀到回饋就是完整回饋（不會文字有了、圖片還沒處理完），回饋送達一律為準。從未有前端連上的情況（例如沒開瀏覽器）維持原本的 timeout 行為。
- 前端「會話超時」通知（`user_timeout`）現在會先寫明原因，回給 AI 的文字不再是預設的「等待用戶回饋」。

### ⚠️ 行為變更
- 任何超過 75 秒的 WebSocket 中斷——筆電休眠、瀏覽器丟棄背景分頁、SSH 轉送斷線——現在都會以「使用者已關閉回饋介面」結束等待，而不是等到 timeout。這是刻意的取捨：關掉視窗卻讓 AI 空等十分鐘，比偶爾提早收尾更常見也更惱人。

### ✅ 測試
- `test_feedback_timeout.py` —— 逾時回傳必含結束指令且不再建議重試；取得回饋後的 `TimeoutError` 不得被當成沒回應；工具描述允許在沒回應時停止；斷線寬限：在寬限內（而非 timeout）結束等待、期間重連不結束、已有回饋時不啟動、回呼寫入 TIMEOUT 後才送達的回饋仍為準、回呼在提交寫到一半時到期不得回傳半套回饋；`/ws` 端點的接線（登記連線斷開啟動寬限、重連取消）以 `TestClient.websocket_connect` 覆蓋。
- 以真實 MCP stdio round-trip 加 Chromium 驗證：開介面 → F5 → 仍在等待 → 關閉分頁 → 寬限到期後收到結束指令；無前端連線時逾時同樣收到結束指令。

---

## [v2.7.1] - 2026-09-06 - MCP_LANGUAGE 優先序與 Linux 桌面相容性

### 🌟 版本亮點
- `MCP_LANGUAGE` 真正成為強制指定——不再被介面中先前保存的語言蓋掉（#189）。
- Linux 桌面 binary 可在 Ubuntu 22.04 / Debian 12 以上執行（glibc 需求由 2.39 降至 2.34，#165）。

### 🐛 問題修復
- **`MCP_LANGUAGE` 改為最高優先**（[#189](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/189)）：README 把它描述為「強制指定介面語言」，但偵測順序卻讓介面中保存的語言排在它前面，設了 `MCP_LANGUAGE=zh-CN` 仍會顯示繁中。順序對調；設定環境變數後，介面中的語言選擇只在當次會話生效。
- **Linux 桌面 binary 改在 ubuntu-22.04 建置**（[#165](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/165)）：原本在 ubuntu-latest 建出的檔案需要 `GLIBC_2.39`，只能在 Ubuntu 24.04+ 執行；重建後最高需求降為 `GLIBC_2.34`。
- **修正桌面 binary 提交流程在單平台建置時失效**：`download-artifact` 只有單一 artifact 時不會建立子目錄，原本靠目錄名辨識平台的複製步驟會回報 0/4 並跳過提交。改為以最終檔名上傳與搜尋。

### 🔧 其他變更
- 修正 renovate 設定警告（`vulnerabilityAlerts.prPriority` 不合法，改以 `isVulnerabilityAlert` packageRule 表達）。
- 依賴下限一次提高到 OSV 記錄的最後漏洞修補版本（aiohttp 3.14.3、starlette 1.3.1、jinja2 3.1.6、tauri 2.11.1、tokio 1.44.2 等），實際鎖定版本不變；renovate 改用 `rangeStrategy=widen`，範圍內的更新不再逐個 patch 提高下限。

---

## [v2.7.0] - 2026-09-06 - 升級至 fastmcp 4 / mcp 2

### 🌟 版本亮點
- 升級至 fastmcp 4.x 與 MCP Python SDK 2.x；伺服器對舊協定客戶端維持相容，工具與回傳格式不變。
- 修正 `ResourceManager` 臨時檔清理的邊界條件，消除一個隨機失敗的測試。

### 🔧 其他變更
- **升級 `fastmcp` 至 4.x、`mcp` 至 2.x**（取代 renovate [#239](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/239)、[#240](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/240)）：mcp 1.x 與 fastmcp 3.x 已進入僅收安全修補的維護模式。fastmcp 4 依賴 `mcp>=2,<3`，兩者必須一起升級 —— 只合併其中一個會讓依賴無法解析、套件裝不起來（與 #213/#217/#221/#228 同類問題）。伺服器程式碼只需把 `ImageContent` 的建構參數改為 mcp 2 的正式欄位名 `mime_type`；wire 格式仍為 `mimeType`。以 stdio 實測 `list_tools`／`get_system_info`，舊協定（2024-11-05）客戶端的整合測試全數通過。
- **修正 `ResourceManager.cleanup_temp_files` 的年齡邊界**：`file_age > max_age` 改為 `>=`。`cleanup_all` 以 `max_age=0` 表示「清理所有檔案」，但剛建立的檔案在 Windows 時間精度下年齡恰為 0，會被漏掉。

### ✅ 測試
- `test_image_content.py` —— 不再綁定 mcp 1 的內部模組名與 snake_case 之前的 `model_dump()` 欄位；改以 `type(...) is ImageContent` 與 `model_dump(by_alias=True)` 驗證 wire 契約。

---

## [v2.6.2] - 2026-08-25 - timeout 鉗制與工具回傳契約

### 🐛 問題修復
- **鉗制 `interactive_feedback` 的 timeout**（[#212](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/212)）：客戶端有時會傳入不合理的小值 —— 回報中 Cursor 傳過 `timeout=1`，使用者還沒看清介面就「操作超時」。現在伺服器端會鉗制到 60–86400 秒。選擇鉗制而非 pydantic 的 `ge`/`le` 驗證，是因為驗證失敗會讓整個 tool call 中斷；對 human-in-the-loop 工具來說，以安全值繼續比中斷更有用。
- **修正 `wait_for_feedback` 的提前結束邏輯**：舊版對 `timeout <= 30` 使用 `max(timeout - 1, 5)`，在 `timeout=1` 時反而把等待「延長」到 5 秒，與提前結束、避免與 MCP 層超時競爭的本意相反。

### 🔧 其他變更
- **精確宣告工具回傳型別**（由裸 `list` 改為 `list[TextContent | ImageContent]`），與 [#234](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/234) 相關。模糊的 `list` 讓 FastMCP 無法判斷內容型別，只能生成 wrap-result 的 `outputSchema`（`{"result": {"type": "array"}}` 加上 `x-fastmcp-wrap-result`），並把 content blocks 額外包成 `structuredContent`。宣告精確型別後 FastMCP 正確識別為 content blocks，該 schema 消失。
  - 這**不等於** #234 報告的違規已重現。實測 FastMCP 3.4.7 下，修復前後 `interactive_feedback` 與 `get_system_info` 的 `CallToolResult` 都含 schema 要求的 `content` 欄位。完整調查說明留在該 issue。

### ✅ 測試
- `test_feedback_timeout.py` —— 鉗制邊界、壞型別容錯、margin 不得延長等待
- `test_tool_contract.py` —— 守住回傳註解，避免退回裸 `list`

---

## [v2.6.1] - 2026-08-25 - 安全修復與維護恢復

### 🌟 版本亮點
移除已知的命令執行風險，並修復讓新安裝完全無法使用的相容性問題。專案恢復維護，目前範圍聚焦在「安全 + 裝了就壞的相容性」。

### 🔒 安全修復
- **移除命令執行功能**（[#219](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/219)）：舊版可透過**未認證**的 WebSocket `/ws` 端點發送 `run_command` 訊息並執行任意程序。原本的防護是 shell metacharacter blocklist，但因為使用 `shell=False`，metacharacter 本來就不是風險點——`cat`、`curl`、`wget`、`python`、`powershell` 等可直接執行。且自動執行命令功能**預設為啟用**。
  - 此功能已**完整移除**（後端處理器、session 方法、前端 UI、設定項、i18n 文案），而非加強 blocklist。blocklist 無法安全地允許任意執行檔。
  - 新增 `tests/unit/test_no_command_execution.py` 防止重新引入。
  - 影響版本：**2.6.0 及之前所有版本**。請升級。

- **修復 Cross-Site WebSocket Hijacking（CSWSH）**：私下回報的 `GHSA-cmr5-gpm3-79vf`（critical）與 `GHSA-2wx7-r4rh-f663`（high）。瀏覽器開啟 WebSocket **不受 same-origin policy 限制**，因此惡意網頁可讓使用者的瀏覽器連上 `ws://127.0.0.1:<port>/ws` 並送訊息 —— 舊版 `/ws` 接受任何 Origin 就直接 `accept()`，配合上述 `run_command` 可升級為遠端程式碼執行；綁定 loopback 並不能防止這點，因為瀏覽器本身就在本機。
  - 修復採兩層獨立防禦：(1) 命令執行已完全移除，升級路徑消失；(2) `/ws` 在 `accept()` **之前**驗證 Origin，僅允許本服務埠上的 loopback 來源、綁定主機自身、以及桌面 WebView scheme；未帶 Origin 的非瀏覽器客戶端（如桌面應用）仍放行，因為跨站頁面無法移除該 header。
  - 跨站連線在握手完成前即以 HTTP 403 拒絕。`tests/unit/test_websocket_origin.py` 使用回報者 PoC 中的實際來源作為測試案例。
  - 感謝兩位回報者提供詳盡分析與可運作的 PoC。

### 🐛 問題修復
- **修復 Web UI 直接回傳 500**（[#213](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/213)、[#217](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/217)、[#221](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/221)、[#228](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/228)）：新版 Starlette 變更 `TemplateResponse` 簽名，舊呼叫方式會拋出 `TypeError: unhashable type: 'dict'`，導致以 `uvx @latest` 安裝的使用者完全無法開啟頁面。感謝 [#220](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/220)（[#214](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/214)、[#215](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/215)、[#216](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/216) 亦回報同一問題）。
- **修復 `session_id` 未帶入 template**：`feedback.html` 需要它初始化前端，但 context 從未提供。
- **修復圖片序列化錯誤**（[#154](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/154)、[#168](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/168)、[#180](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/180) 等）：改用標準 `mcp.types.ImageContent`。舊實作回傳 `fastmcp.utilities.types.Image`，在 FastMCP 3.x 會失敗於 `Output validation error: outputSchema defined but no structured output returned`。已用真實 MCP round-trip 驗證 PNG/JPEG/GIF/WebP。感謝 [#171](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/171)。

### 🔧 其他變更
- **依賴加上版本上限**：避免上游破壞性變更再次讓安裝失效。`starlette` 改為顯式直接依賴。
- **文件修正**：移除「大幅節省平台成本」宣稱（Cursor 已改為 token 計費，前提不成立）；`MCP_WEB_HOST=0.0.0.0` 不再作為推薦解法，改標示安全警告並建議 SSH 端口轉發。
- 新增 [SECURITY.md](../SECURITY.md)：維護範圍、已知風險、回報管道。

### ⚠️ 已知未修問題
以下為既有限制，不在目前的維護範圍內：
- Web UI 與 WebSocket **無認證機制**、無 Origin 驗證
- 會話狀態流轉、i18n 環境偵測、cleanup timer 相關的既有測試失敗

---

## [v2.6.0] - 2025-06-28 - 智能會話管理與自動化功能強化

### 🌟 版本亮點
大幅強化會話管理功能，新增自動執行命令、匯出功能和通知系統，提供更智能的開發體驗。

### ✨ 新功能
- 🚀 **自動執行命令**: 新建會話和提交後可自動執行預設命令
- 📊 **會話匯出功能**: 支援將會話記錄匯出為多種格式
- ⏸️ **自動提交控制**: 新增暫停和開始按鈕，讓使用者更好控制自動提交時機
- 🔔 **系統通知**: 新增系統級通知功能，重要事件即時提醒

### 🚀 改進功能
- ⏱️ **會話超時機制優化**: 重新設計會話管理，提供更彈性的設定選項
- 🌏 **多語系強化**: 重構多語系架構，通知系統也完整支援多語言
- 🎨 **介面簡化**: 大幅簡化使用者介面，提升使用體驗

### 🐛 問題修復
- 修復命令執行功能的相關問題
- 修正 WebSocket 狀態檢測的導入錯誤
- 完善會話歷史的多語言支援

---

## [v2.5.6] - 2025-06-21 - 設定保存機制優化與介面美化

### 🌟 版本亮點
重構設定保存機制，解決語系切換保存問題，並為設定介面增加視覺化圖標，提升使用者體驗。

### 🚀 改進功能
- 🔨 **設定保存機制重構**: 完全移除 localStorage 依賴，改用統一的 FastAPI 後端保存機制
  - 解決語系切換時設定無法正確保存的問題
  - 移除防抖機制，確保設定即時保存
  - 提升設定保存的可靠性和一致性
- ✨ **設定介面美化**: 為設定頁籤內的各功能區塊新增對應圖標
  - 提升介面視覺效果和使用者體驗
  - 更直觀的功能識別

### 🛠️ 技術改進
- 📊 **統一存儲架構**: 所有設定統一使用 JSON 檔案存儲，確保跨環境一致性
- 🔧 **程式碼簡化**: 移除複雜的 localStorage 相關程式碼，降低維護成本

---

## [v2.5.5] - 2025-06-21 - SSH 遠端開發支援與穩定性增強

### 🌟 版本亮點
新增 SSH 遠端開發環境支援，解決遠端開發時無法存取 Web UI 的問題。同時改進 macOS 編譯支援和桌面應用穩定性，提升開發者體驗。

### ✨ 新功能
- 🌐 **SSH 遠端開發支援**: 新增 `MCP_WEB_HOST` 環境變數，支援設定 Web 伺服器主機綁定
  - 預設為 `127.0.0.1` 確保安全性
  - 可設定為 `0.0.0.0` 允許遠端存取
  - 解決 Cursor SSH Remote 等遠端開發環境的存取問題
- 🍎 **macOS 編譯支援增強**: 新增 `.cargo/config.toml` 配置檔案
  - 支援 Intel (x86_64) 和 Apple Silicon (aarch64) 架構
  - 解決 macOS 上 PyO3 undefined dynamic_lookup 編譯問題
  - 遵循 PyO3 官方推薦的最佳實踐

### 🚀 改進功能
- 📝 **工具文檔優化**: 將 LLM 指令移至工具 docstring，提升 token 效率
- 🎨 **使用者配置簡化**: 移除複雜的 Cursor 規則配置
- 📊 **AI 工作摘要 Markdown 增強**: 改進 Markdown 渲染效果和相容性
- 🔄 **會話歷史流程優化**: 改進會話保存和管理機制

### 🐛 問題修復
- 🖥️ **桌面應用 MCP 協議修復**: 修正桌面模式下 MCP 協議通訊污染問題
- 📦 **打包流程修復**: 修正多平台桌面應用打包和發布問題
- 🔧 **發布流程優化**: 改進自動化發布工作流程的穩定性
- 🔥 **移除 ESC 快捷鍵**: 移除可能造成意外關閉的 ESC 快捷鍵功能

### 🛠️ 技術改進
- 🏗️ **構建系統增強**: 改進跨平台編譯配置和相依性管理
- 📚 **文檔自動化**: 改進工具自我文檔化，遵循 FastMCP 最佳實踐
- 🔍 **調試功能增強**: 新增更詳細的調試訊息和錯誤處理

### 📋 使用說明
- **SSH 遠端開發**: 在 MCP 配置中設定 `"MCP_WEB_HOST": "0.0.0.0"` 允許遠端存取
- **本地開發**: 保持預設 `"MCP_WEB_HOST": "127.0.0.1"` 確保安全性
- **macOS 開發**: 新的編譯配置將自動生效，無需額外設定

---

## [v2.5.0] - 2025-06-15 - 桌面應用程式與效能優化

### 🌟 版本亮點
全新推出跨平台桌面應用程式，支援 Windows、macOS、Linux 三大平台。同時大幅提升系統效能與穩定性，引入防抖/節流機制優化用戶體驗。

### ✨ 新功能
- 🖥️ **桌面應用程式**: 基於 Tauri 框架的原生桌面應用，支援 Windows x64、macOS (Intel/Apple Silicon)、Linux x64
- 📊 **會話歷史本地檔案存儲**: 會話記錄從 localStorage 改為伺服器端本地檔案保存，支援跨環境數據一致性
- 🔧 **多平台構建支援**: 完整的 CI/CD 流程，支援自動化多平台桌面應用構建
- 📝 **桌面模式配置**: 新增 `MCP_DESKTOP_MODE` 環境變數，支援桌面/Web 模式切換
- 📋 **AI 工作摘要 Markdown 顯示**: 支援 Markdown 語法渲染，包含標題、粗體、程式碼區塊、列表、連結等格式

### 🚀 改進功能
- ⚡ **效能大幅提升**: 引入防抖/節流機制，減少不必要的渲染和網路請求
- 🌐 **網路連接穩定性**: 改進 WebSocket 重連機制，支援網路狀態檢測和智能重連
- 📊 **會話歷史存儲改進**: 從 localStorage 改為伺服器端本地檔案存儲，提升跨環境一致性
- 🎨 **UI 渲染優化**: 優化會話管理、統計資訊、狀態指示器的渲染效能
- 📱 **響應式改進**: 調整心跳頻率和超時閾值，減少系統負載
- 🔄 **模組化增強**: JavaScript 模組結構優化，支援更好的日誌管理

### 🐛 問題修復
- 🌐 **網路重連改進**: 優化重連算法，採用指數退避策略和隨機抖動
- 🖥️ **桌面模式適配**: 修復桌面模式下瀏覽器自動開啟的問題
- 📊 **渲染效能修復**: 解決重複渲染和不必要的狀態更新問題

### 🛠️ 技術改進
- 🏗️ **構建流程優化**: 新增 Makefile 桌面應用構建命令，支援 debug/release 模式
- 📦 **依賴管理**: 整合 Rust 工具鏈，支援跨平台編譯和打包
- 🔍 **開發工具增強**: 新增環境檢查、構建驗證、清理工具
- 📚 **文檔完善**: 新增桌面應用構建指南和工作流程說明
- 🔒 **安全性增強**: 引入 DOMPurify 進行 XSS 防護，確保內容安全

### 📋 使用說明
- **桌面模式**: 在 MCP 配置中設定 `"MCP_DESKTOP_MODE": "true"` (參考 `examples/mcp-config-desktop.json`)
- **Web 模式**: 在 MCP 配置中設定 `"MCP_DESKTOP_MODE": "false"` (預設，參考 `examples/mcp-config-web.json`)
- **測試桌面模式**: `uvx mcp-feedback-enhanced@latest test --desktop`
- **構建桌面應用**: `make build-desktop-release`

---

## [v2.4.3] - 2025-06-14 - 會話管理重構與音效通知

### 🌟 版本亮點
將會話管理從左側邊欄遷移到獨立頁籤，解決瀏覽器相容性問題。新增音效通知系統，支援自訂音效。

### ✨ 新功能
- 🔊 **音效通知系統**: 會話更新時播放音效提醒，支援內建音效和自訂音效上傳
- 📚 **會話歷史管理**: 本地保存會話記錄，支援匯出和清理功能
- 💾 **輸入框高度記憶**: 自動保存和恢復文字輸入框的高度設定
- 📋 **一鍵複製**: 專案路徑和會話ID支援點擊複製

### 🚀 改進功能
- 📋 **會話管理重構**: 從左側邊欄遷移到「會話管理」頁籤，解決小視窗下按鈕無法點擊的問題
- 🎨 **介面佈局優化**: AI摘要區域自動擴展，提交按鈕位置調整，移除多餘描述文字
- 🌐 **多語言增強**: 新增tooltip和按鈕的多語言支援

### 🐛 問題修復
- 修復當前會話詳細資訊按鈕無反應問題
- 修復會話詳情彈窗關閉延遲問題
- 修復音效通知語系初始化問題
- 修正自動提交處理邏輯

---

## [v2.4.2] - Web-Only 架構重構與智能功能增強

### 🌟 版本亮點
本版本進行了重大架構重構，**完全移除 PyQt6 GUI 依賴**，轉為純 Web UI 架構，大幅簡化部署和維護。同時新增多項智能功能，包括提示詞管理、自動提交、會話管理等，全面提升用戶體驗和工作效率。

### 🔄 重大架構變更
- 🏗️ **完全移除 PyQt6 GUI**: 徹底移除桌面應用程式依賴，簡化安裝和部署流程
- 🌐 **純 Web UI 架構**: 統一使用 Web 介面，支援所有平台和環境
- 📦 **依賴大幅簡化**: 移除 PyQt6、相關 GUI 庫等重型依賴，安裝包體積顯著減小
- 🚀 **部署更簡單**: 無需考慮 GUI 環境配置，適用於所有開發環境

### ✨ 全新功能
- 📝 **智能提示詞管理系統**:
  - 常用提示詞的 CRUD 操作（新增、編輯、刪除、使用）
  - 使用頻率統計和智能排序
  - 快速選擇和一鍵應用功能
  - 支援自動提交標記和優先顯示
- ⏰ **自動定時提交功能**:
  - 可設定 1-86400 秒的倒數計時器
  - 視覺化倒數顯示和狀態指示
  - 與提示詞管理系統深度整合
  - 支援暫停、恢復、取消操作
- 📊 **會話管理與追蹤**:
  - 當前會話狀態即時顯示
  - 會話歷史記錄和統計分析
  - 今日會話數量和平均時長統計
  - 會話詳情查看和管理功能
- 🔗 **連線監控系統**:
  - WebSocket 連線狀態即時監控
  - 延遲測量和連線品質指示
  - 自動重連機制和錯誤處理
  - 詳細的連線統計資訊
- ⌨️ **快捷鍵增強**: 新增 Ctrl+I 快速聚焦輸入框功能 (感謝 @penn201500)

### 🚀 功能改進
- 🎨 **UI/UX 全面優化**:
  - 新增左側會話管理面板，支援收合/展開
  - 頂部連線狀態列，即時顯示系統狀態
  - 響應式設計，適配不同螢幕尺寸
  - 統一的設計語言和視覺風格
- 🌐 **多語言系統增強**:
  - 優化語言切換機制，支援即時切換
  - 新增大量翻譯文本，提升本地化覆蓋率
  - 改進語言選擇器 UI，使用下拉選單設計
  - 修復語言切換時的顯示問題
- 🖼️ **圖片設定整合**:
  - 將圖片設定從工作區移至設定頁籤
  - 統一的設定管理介面
  - 改進設定項目的組織和佈局
- 📱 **介面佈局優化**:
  - 調整版面配置，符合多語言顯示需求
  - 優化按鈕樣式和間距
  - 改進表單元素的視覺設計
  - 增強可訪問性和易用性

### 🐛 問題修復
- 🔧 **會話管理修復**:
  - 修復會話統計資訊無法正確更新的問題
  - 修復會話數量計算錯誤
  - 改進會話狀態追蹤機制
- 🎯 **提示詞功能修復**:
  - 修復常用提示詞管理無法正確設定自動提交的問題
  - 改進提示詞選擇和應用邏輯
- 🌐 **語系切換修復**:
  - 修復語言切換時部分文字未更新的問題
  - 改進多語言文本的載入機制
- 🏗️ **架構穩定性修復**:
  - 修復會話管理初始化問題
  - 改進錯誤處理和資源清理
  - 優化模組載入順序和依賴關係

### 🛠️ 技術改進
- 📦 **模組化架構**:
  - JavaScript 代碼完全模組化重構
  - 採用 ES6+ 語法和現代化開發模式
  - 清晰的模組分離和職責劃分
- 📊 **效能提升**:
  - 優化 WebSocket 通信效率
  - 改進前端資源載入速度
  - 減少記憶體使用和 CPU 負載

### 📚 文檔更新
- 📖 **架構文檔更新**: 更新系統架構說明，反映 Web-Only 設計
- 🔧 **安裝指南簡化**: 移除 GUI 相關安裝步驟和依賴說明
- 🖼️ **截圖更新**: 更新所有介面截圖，展示新的 Web UI 設計
- 📋 **API 文檔增強**: 新增提示詞管理、自動提交等新功能的 API 說明

---

## [v2.3.0] - 系統穩定性與資源管理增強

### 🌟 亮點
本版本專注於提升系統穩定性和使用體驗，特別解決了 Cursor SSH Remote 環境下無法啟動瀏覽器的問題。

### ✨ 新功能
- 🌐 **SSH Remote 環境支援**: 解決 Cursor SSH Remote 無法啟動瀏覽器的問題，提供清晰的使用指引
- 🛡️ **錯誤提示改善**: 當發生錯誤時，提供更友善的錯誤訊息和解決建議
- 🧹 **自動清理功能**: 自動清理臨時文件和過期會話，保持系統整潔
- 📊 **記憶體監控**: 監控記憶體使用情況，防止系統資源不足

### 🚀 改進功能
- 💾 **資源管理優化**: 更好地管理系統資源，提升運行效率
- 🔧 **錯誤處理增強**: 遇到問題時提供更清楚的說明和解決方案
- 🌐 **連線穩定性**: 改善 Web UI 的連線穩定性
- 🖼️ **圖片上傳優化**: 改善圖片上傳功能的穩定性
- 🎯 **自動聚焦輸入框**: 回饋視窗開啟時自動聚焦到輸入框，提升用戶體驗 (感謝 @penn201500)

### 🐛 問題修復
- 🌐 **連線問題**: 修復 WebSocket 連線的相關問題
- 🔄 **會話管理**: 修復會話狀態追蹤的問題
- 🖼️ **圖片處理**: 修復圖片上傳時的事件處理問題

---

## [v2.2.5] - WSL 環境支援與跨平台增強

### ✨ 新功能
- 🐧 **WSL 環境檢測**: 自動識別 WSL 環境，提供專門的支援邏輯
- 🌐 **智能瀏覽器啟動**: WSL 環境下自動調用 Windows 瀏覽器，支援多種啟動方式
- 🔧 **跨平台測試增強**: 測試功能整合 WSL 檢測，提升測試覆蓋率

### 🚀 改進功能
- 🎯 **環境檢測優化**: 改進遠端環境檢測邏輯，WSL 不再被誤判為遠端環境
- 📊 **系統資訊增強**: 系統資訊工具新增 WSL 環境狀態顯示
- 🧪 **測試體驗提升**: 測試模式下自動嘗試啟動瀏覽器，提供更好的測試體驗

---

## [v2.2.4] - GUI 體驗優化與問題修復

### 🐛 問題修復
- 🖼️ **圖片重複貼上修復**: 解決 GUI 介面中使用 Ctrl+V 複製貼上圖片時出現重複貼上的問題
- 🌐 **語系切換修復**: 修復圖片設定區域在語言切換時文字沒有正確翻譯的問題
- 📝 **字體可讀性改善**: 調整圖片設定區域的字體大小，提升文字可讀性

---

## [v2.2.3] - 超時控制與圖片設定增強

### ✨ 新功能
- ⏰ **用戶超時控制**: 新增可自訂的超時設定功能，支援 30 秒至 2 小時的彈性設定
- ⏱️ **倒數計時器**: 介面頂部顯示即時倒數計時器，提供視覺化的時間提醒
- 🖼️ **圖片大小限制**: 新增圖片上傳大小限制設定（無限制/1MB/3MB/5MB）
- 🔧 **Base64 相容模式**: 新增 Base64 詳細模式，提升部分 AI 模型的圖片識別相容性
- 🧹 **UV Cache 管理工具**: 新增 `cleanup_cache.py` 腳本，協助管理和清理 UV cache 空間

### 🚀 改進功能
- 📚 **文檔結構優化**: 重新整理文檔目錄結構，將圖片移至 `docs/{語言}/images/` 路徑
- 📖 **Cache 管理指南**: 新增詳細的 UV Cache 管理指南，包含自動化清理方案
- 🎯 **智能相容性提示**: 當圖片上傳失敗時自動顯示 Base64 相容模式建議

### 🐛 問題修復
- 🛡️ **超時處理優化**: 改進用戶自訂超時與 MCP 系統超時的協調機制
- 🖥️ **介面自動關閉**: 修復超時後介面自動關閉和資源清理邏輯
- 📱 **響應式佈局**: 優化超時控制元件在小螢幕設備上的顯示效果

---

## [v2.2.2] - 超時自動清理修復

### 🐛 問題修復
- 🔄 **超時自動清理**: 修復 GUI/Web UI 在 MCP session timeout (預設 600 秒) 後沒有自動關閉的問題
- 🛡️ **資源管理優化**: 改進超時處理機制，確保在超時時正確清理和關閉所有 UI 資源
- ⚡ **超時檢測增強**: 加強超時檢測邏輯，確保在各種情況下都能正確處理超時事件

---

## [v2.2.1] - 視窗優化與統一設定接口

### 🚀 改進功能
- 🖥️ **視窗大小限制解除**: 解除 GUI 主視窗最小大小限制，從 1000×800 降至 400×300
- 💾 **視窗狀態實時保存**: 實現視窗大小與位置的即時保存機制，支援防抖延遲
- ⚙️ **統一設定接口優化**: 改進 GUI 設定版面的配置保存邏輯，避免設定衝突

### 🐛 問題修復
- 🔧 **視窗大小限制**: 解決 GUI 視窗無法調整至小尺寸的問題
- 🛡️ **設定衝突**: 修復設定保存時可能出現的配置衝突問題

---

## [v2.2.0] - 佈局與設定界面優化

### ✨ 新功能
- 🎨 **水平佈局模式**: GUI 與 Web UI 的合併模式新增摘要與回饋的左右佈局選項

### 🚀 改進功能
- 🎨 **設定界面改進**: 優化了 GUI 與 Web UI 的設定頁面，提升佈局清晰度
- ⌨️ **快捷鍵完善**: 提交回饋快捷鍵現已完整支援數字鍵盤的 Enter 鍵

### 🐛 問題修復
- 🔧 **圖片重複貼上**: 解決了在 Web UI 文字輸入區使用 Ctrl+V 貼上圖片時的重複問題

---

## [v2.1.1] - 視窗定位優化

### ✨ 新功能
- 🖥️ **智能視窗定位**: 新增「總是在主螢幕中心顯示視窗」設定選項
- 🌐 **多螢幕支援**: 完美解決 T 字型螢幕排列等複雜多螢幕環境的視窗定位問題
- 💾 **位置記憶**: 自動保存和恢復視窗位置，智能檢測視窗可見性

---

## [v2.1.0] - 全面重構版

### 🎨 重大重構
- 🏗️ **全面重構**: GUI 和 Web UI 採用模組化架構
- 📁 **集中管理**: 重新組織資料夾結構，提升維護性
- 🖥️ **界面優化**: 現代化設計和改進的用戶體驗

### ✨ 新功能
- 🍎 **macOS 界面優化**: 針對 macOS 用戶體驗進行專項改進
- ⚙️ **功能增強**: 新增設定選項和自動關閉頁面功能
- ℹ️ **關於頁面**: 新增關於頁面，包含版本資訊、專案連結和致謝內容

---

## [v2.0.14] - 快捷鍵與圖片功能增強

### 🚀 改進功能
- ⌨️ **增強快捷鍵**: Ctrl+Enter 支援數字鍵盤
- 🖼️ **智能圖片貼上**: Ctrl+V 直接貼上剪貼簿圖片

---

## [v2.0.9] - 多語言架構重構

### 🔄 重構
- 🌏 **多語言架構重構**: 支援動態載入
- 📁 **語言檔案模組化**: 模組化組織語言檔案

---

## [v2.0.3] - 編碼問題修復

### 🐛 重要修復
- 🛡️ **完全修復中文字符編碼問題**: 解決所有中文顯示相關問題
- 🔧 **解決 JSON 解析錯誤**: 修復資料解析錯誤

---

## [v2.0.0] - Web UI 支援

### 🌟 重大功能
- ✅ **新增 Web UI 支援**: 支援遠端環境使用
- ✅ **自動環境檢測**: 自動選擇合適的界面
- ✅ **WebSocket 即時通訊**: 實現即時雙向通訊

---

## 圖例說明

| 圖示 | 意義 |
|------|------|
| 🌟 | 版本亮點 |
| ✨ | 新功能 |
| 🚀 | 改進功能 |
| 🐛 | 問題修復 |
| 🔄 | 重構變更 |
| 🎨 | 界面優化 |
| ⚙️ | 設定相關 |
| 🖥️ | 視窗相關 |
| 🌐 | 多語言/網路相關 |
| 📁 | 檔案結構 |
| ⌨️ | 快捷鍵 |
| 🖼️ | 圖片功能 |
| 📝 | 提示詞管理 |
| ⏰ | 自動提交 |
| 📊 | 會話管理 |
| 🔗 | 連線監控 |
| 🏗️ | 架構變更 |
| 🛠️ | 技術改進 |
| 📚 | 文檔更新 |

---

**完整專案資訊：** [GitHub - mcp-feedback-enhanced](https://github.com/Minidoracat/mcp-feedback-enhanced)
