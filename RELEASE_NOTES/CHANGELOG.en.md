# Changelog (English)

This document records all version updates for **MCP Feedback Enhanced**.

## [v2.8.5] - Unreleased - Statistics Panel, UI Language and Traditional Chinese Wording Fixes

### 🌟 Highlights
- The Detailed Statistics panel now shows the real status, session count, today's average duration, reconnect count and connection time, and the top-right reconnect status shows the actual attempt number.
- `MCP_LANGUAGE` now actually sets the web UI language on both the feedback and waiting pages (switching in the UI only lasts for the current page); times, dates, copied session content and previously hard-coded Chinese UI text follow the UI language and update as soon as you switch.
- The Traditional Chinese UI, and the Traditional Chinese messages the backend returns to the UI and the AI, now use Taiwan terminology.
- Feedback submitted manually during the auto-submit countdown is no longer recorded as auto-submitted.
- Native Windows with `WSLENV` set is no longer misdetected as WSL and no longer opens the browser through `cmd.exe`.

### 🐛 Bug Fixes
- **Detailed Statistics always showed "Waiting" and 1 session**: both fields copied from elements that no longer exist on the page, so they stayed at their defaults. Status now follows the current session (Submitted after you send feedback, back to Waiting when a new session arrives), Sessions is the number of entries in the session history (including the current one), and both update when you switch languages.
- **Today's average duration was always 0 and kept the old language's units after a switch**: the statistic only read a duration field that sessions from the server don't have, and it was only redrawn when the value changed. It now uses the same definition and the same rounding (truncation) as the session history duration (created time to end time, or to the feedback submission time when there is no end time), so a single session shows the same value in both places, and it switches units immediately.
- **Reconnect count reset to 0 after reconnecting, and connection time stuck at 00:00**: the reconnect count now accumulates for the page; connection time updates every second while connected, shows --:-- while disconnected, and restarts from the new connection.
- **Connection status could show "Reconnecting... (attempt {attempt})"**: the attempt number was not filled in, and switching languages while disconnected reapplied the raw string. It now shows the actual attempt number, restarting for each outage, also after a language switch.
- **Times and dates followed the browser locale**: the English UI could show "下午9:51:30". Times on the current session card, the session history and the "Feedback submitted" status, as well as prompt and custom audio dates, now follow the UI language and update as soon as you switch.
- **Copy Session Content / Copy User Content were hard-coded Simplified Chinese**: output now follows the UI language. Copied session content used to show user messages as [object Object] and raw status/created values; it now shows the message content and status text, and times in both use YYYY/MM/DD HH:MM:SS, matching the Session Details dialog.
- **Manual submissions during the auto-submit countdown were recorded as "Auto Submit"**: the frontend decided the submission method by whether the auto-submit countdown was running, so once a prompt was set to auto-submit and the countdown had started, clicking Submit stored `submission_method: auto` in the session history, session details, exported files and the server record. The method now comes from what actually triggered the submission: the countdown expiring records `auto`, the Submit button or Ctrl+Enter records `manual`, and feedback queued while the connection is not ready keeps its original method.
- **Icon buttons turned into text after translations were applied**: the auto-submit buttons in prompt settings had their ⏰/⏸️ icons replaced by labels such as "Set as Auto Submit", with a tooltip hard-coded in Chinese; the "Copy Session Content" and "Copy User Content" buttons on the session card had their 📋/📝 icon and label replaced by plain text, and their `aria-label` was hard-coded in Chinese and never changed with the language. The icons now stay, with the description in the tooltip and screen-reader label, following the UI language.
- **The page's `<html lang>` was always `zh-CN`**: both templates hard-coded `lang="zh-CN"` and only a language switch in the UI changed it, so the first load of a Traditional Chinese or English interface was declared as Simplified Chinese, and screen readers and browsers used the wrong language for speech, line breaking and font selection. The templates now default to `zh-TW`, matching the frontend default, and applying translations sets `lang` to the current interface language on the first load and on every language switch.
- **`MCP_LANGUAGE` now actually sets the web UI language** ([#189](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/189)): v2.7.1 only changed the backend detection order; the web UI was still driven by `language` in `ui_settings.json` or the browser language, so `MCP_LANGUAGE=en` / `zh-CN` still rendered Traditional Chinese. The server now passes the forced language to both the feedback page and the waiting page (`<html lang>` plus `data-forced-language`), so the first applied translation is already the forced language. While it is set, the language picker still works but only for the current page; reloading returns to the forced language, and `language` in `ui_settings.json` is never changed by switching, saving other settings, or resetting.
- **`MCP_LANGUAGE` only accepts `zh-TW`, `zh-CN`, and `en`**: after trimming whitespace the value must match exactly; values such as `ja`, `EN`, or `zh_TW` are treated as unset. The error handler's fallback path used to return the unvalidated value.
- **The waiting page (no session yet) is now localized**: "連線中..." and the waiting text were hard-coded in Traditional Chinese; they now follow `MCP_LANGUAGE` → `language` in `ui_settings.json` → browser language → Traditional Chinese.
- **Opening the page no longer writes the browser language into `ui_settings.json`**: it is saved only when the user switches language without `MCP_LANGUAGE` set.
- **Hard-coded Chinese in the UI**: the Session Details dialog's "(進行中)", "未知", content/character labels, copy buttons and toasts, the custom audio "Created / Format" labels and play/delete button tooltips, and the prompt picker's "Last Used" label are now translated; the play/delete icon buttons also have screen-reader labels.
- **Some messages showed raw keys or unfilled parameters**: added missing translations in all three locales (mostly Simplified Chinese system/error messages and session timeout; English session timeout and auto-submit hint). The session history saved, prompt applied and generic error messages used {{count}} while the front end replaces {count}, so the console showed "Session history saved ({4} sessions)"; fixed.
- **Traditional Chinese UI used Mainland Chinese terms**: the zh-TW translation file, the pages' initial text, and the fallback strings shown before translations load now use Taiwan terminology (e.g. 用戶→使用者 "user", 剪貼板→剪貼簿 "clipboard", 當前→目前 "current", 連接→連線 "connection", 超時→逾時 "timeout", 數據→資料 "data", 保存→儲存 "save", 點擊→點選 "click", 重置→重設 "reset", 模板→範本 "template", 本地儲存→本機儲存 "local storage"); the Simplified Chinese and English UIs are unchanged.
- **Backend messages in Traditional Chinese used Mainland Chinese terms**: session status messages (e.g. "等待使用者回饋", "已送出回饋，等待下次 MCP 呼叫", "使用者設定的會話逾時"), the feedback text returned to the AI ("=== 使用者回饋 ===", "使用者取消了回饋。", "使用者未提供任何回饋內容。", "完整 Base64 長度: N 字元"), the wait-timeout reason, and the zh-TW error messages (e.g. "網路連線出現問題", "操作逾時", "資料驗證失敗") now use Taiwan terminology. The context prefixes in error messages now follow the UI language — "檔案：" / "技術細節：" in Traditional Chinese, "文件：" / "技术细节：" in Simplified Chinese (which previously also showed the Traditional "技術細節：") — and are unchanged in English; log-only messages are unchanged.
- **About page still mentioned command execution, removed in v2.6.1**: the description now reflects current features.
- **Native Windows with `WSLENV` set was misdetected as WSL**: the browser was then opened through `cmd.exe`. `is_wsl_environment()` now only checks for WSL on Linux, and the duplicate implementation in `server.py` now uses the one in `web/utils/browser.py`.
- **`MCP_GZIP_LEVEL` had no effect**: the configured compression level (default 6) was never passed to the GZip middleware, so responses always used Starlette's default of 9. Responses now use the configured level, or 6 when unset.
- **`make test-func` always failed**: it ran `test` without arguments, which only prints usage and exits with code 1. It now runs `test --web` with the project .venv.
- **Freshly created temp files survived cleanup on Windows**: about 1 in 10 new files has an mtime slightly later than the current time, so the computed age was negative and `cleanup_temp_files(max_age=0)` (the full cleanup at exit) skipped them. The age is now never below 0.
- **Export filenames could be a day behind**: exported session history and single-session files used the UTC date in their filenames, so exporting between 00:00 and 08:00 in UTC+8 produced the previous day (e.g. exporting early on local Oct 26 gave `session-history-2026-10-25.json`). They now use the local date; timestamps inside the exported JSON stay in UTC ISO format.
- **Exporting a single session said the session history was exported**: the toast read "Session history exported successfully", as if the whole history had been exported; it now says "Session exported successfully". Added `sessionHistory.management.exportSingleSuccess` to all three locales.

### 📝 Documentation
- **Architecture docs did not match the code**: the deployment guide and API reference under `docs/architecture/` described a non-existent `web` subcommand, `--port`/`--session-retention` flags, `MCP_FEEDBACK_*` environment variables, a `config.json`, a `/health` endpoint and WebSocket messages such as `session_history`, and claimed session history lives in localStorage. They now describe the real subcommands (`server`, `test --web/--desktop`, `version`), the environment variables the code actually reads (`MCP_WEB_HOST`, `MCP_WEB_PORT`, etc.), `ui_settings.json` and `session_history.json` under `~/.config/mcp-feedback-enhanced/`, and the actual WebSocket message types and frontend method signatures (`getStats()`, a parameterless `exportSessionHistory()`). The architecture docs were also rechecked against this release's code: removed classes, methods and the `test --timeout` option are gone, `MCP_GZIP_LEVEL` is documented, the tooling section now describes the current pre-commit hooks (Ruff v0.17.2) and the Ruff and mypy checks in CI, and quoted UI text matches the current Traditional Chinese wording.
- **Environment detection, interaction flow and component docs**: remote (SSH etc.) detection only goes to the debug log and never creates an SSH tunnel; WSL is detected only on Linux and opens the Windows browser. The interaction-flow and component docs now use the real method names and states, and the reconnect and stats-panel docs match current behavior (the header retry count restarts on each disconnect, the panel's reconnect count accumulates for the page, and average duration uses the same definition as history durations).
- **System overview**: now describes the Web UI plus the Tauri desktop mode, and its architecture diagram includes the Tauri desktop shell and shows the real module connections (prompts, audio and textarea height are saved through the settings API, not over WebSocket). The "technical highlights" and "maintenance" sections no longer claim incremental updates, state rollback, log rotation, health checks or error statistics, none of which exist; the performance, security and requirements sections drop figures and features with no code behind them (such as "60% less memory", "first paint < 500 ms", "SQL injection protection" and "CORS") and describe the actual behavior instead; and the rest of the overview was rewritten to match the code: the single-active-session state diagram shows when sessions are actually cleaned up, the "persistent Web UI" section lists what really carries over between calls and what does not (a new session clears the input box and images), and unimplemented localization claims such as region-specific layouts and font tuning are gone. The component details' performance-test section now lists the tests that actually have time limits. References to the removed TabManager and the stale version footers are gone, and the architecture index lists the sections checked against main on 2026-10-26, with the commit they were checked against.
- **READMEs in all three languages**: environment detection now describes actual behavior, `test` examples pass `--web` (without it the command only prints help), and `MCP_WEB_PORT=0` is noted to let the OS pick a port; the FAQ entry for a non-existent "Always show window at primary screen center" setting is removed.
- **`MCP_LANGUAGE` and UI language docs**: the three READMEs and the deployment guide, component details, interaction flows and system overview under `docs/architecture/` now describe two separate orders: the web UI language is `MCP_LANGUAGE` → `language` in `ui_settings.json` → browser language → Traditional Chinese, and the language of error messages returned to the AI is `MCP_LANGUAGE` → `LANG` and related environment variables → system locale → Traditional Chinese. They note that only `zh-TW`, `zh-CN` and `en` are accepted (other values are ignored) and that, while it is set, switching in the UI only lasts for the current page, is not saved, and reloading returns to the forced language. `language.json` is removed from the config-file table, and the claim that the UI language lives in localStorage is corrected (localStorage only holds notification settings).
- **Traditional Chinese docs use Taiwan terminology**: README.zh-TW, all architecture docs under `docs/architecture/` (index, system overview, component details, interaction flows, API reference, deployment guide), the Traditional Chinese cache-management and SSH Remote guides, the desktop build and GitHub Actions workflow docs, and the release-notes guide and template now use Taiwan terms in prose, diagrams, and Chinese comments and sample strings inside code blocks (e.g. 使用者, 資料, 設定, 逾時, 呼叫, 互動, 智慧, 偵測, 通訊, 連接埠, 建置); the Traditional Chinese "交互流程文件" is renamed "互動流程文件". Code lines copied verbatim from the source or workflows are unchanged.
- **Desktop build guide troubleshooting matches actual output**: the error examples in `docs/DESKTOP_BUILD.md` now show what `scripts/build_desktop.py` actually prints, and the descriptions of `make clean-desktop` (cleans, then rebuilds the debug build) and `make dev-setup` (installs dev dependencies and pre-commit hooks) are corrected.

### 🧹 Cleanup
- Removed unused debounced session/status update wrappers from app.js, and handlers for the feedback_received and desktop_close_request messages, which the server never sends (including the unused feedback_received test fixture).
- Removed the WebSocket reconnect branch for a "會話更新" close reason the server never sends, and the unused connection-stats reset function.
- Removed the never-initialized tab-manager.js module (including its call to the non-existent /api/register-tab route) and `Utils.generateId`, which only it called.
- Removed `--timeout` from the `test` subcommand: it was never read, and `test --web`/`--desktop` already run until Ctrl+C. Passing `--timeout` now fails with `unrecognized arguments`.
- Removed backend code with no callers: `SessionCleanupManager`, `CompressionMonitor`, `FeedbackResult`, `WebFeedbackSession.set_error`/`set_expired`, the unused `fastmcp_settings` in `server.py` (FastMCP reads `FASTMCP_LOG_LEVEL` itself), and `_delayed_server_stop` in `main_routes.py`.
- Removed `ResourceManager.register_process` and the process tracking that depended on it (`unregister_process`, `cleanup_processes`, the process health check, the `processes` stats fields): nothing ever registered a process, so the table was always empty.
- Removed the always-empty global tab tracking (`WebUIManager.global_active_tabs`, `session.active_tabs`, `get_global_active_tabs_count`, `broadcast_to_active_tabs`): nothing writes to it since TabManager was removed.
- Removed `ErrorHandler`'s error solutions (`_ERROR_SOLUTIONS`, `get_error_solutions`, `get_i18n_error_solutions`) and `create_error_response`: only tests called them and they were never shown to users. Error-type messages now come straight from the built-in message table: the code first looked up `errors.types.*`, which no locale file has, and always fell back to the table; output is unchanged in all three languages.
- Removed unused parts of the Python `I18nManager`: the legacy key mapping (`_get_legacy_translation`, e.g. `btn_submit_feedback` → `buttons.submitFeedback`; no code passes legacy keys, and many of the mapped keys no longer exist); `get_language_display_name` and `get_language_info`, which only it used (the `languageNames.*` and `meta.displayName` keys it looked up exist in none of the three locales); and `reload_translations`, `add_language` and the module-level `reload_translations`, which had no callers.
- Removed message codes and translations left over from the removed command execution feature: backend `MessageCodes.COMMAND_*` and their legacy key mappings, frontend `MessageCodes.COMMAND`, the `error.command` fallback message, and `commandStatus.*`, `error.command`, `errors.command_failed` and `notifications.command_executed` in all three locales. The backend `MessageCodes` also lost 33 constants that were never sent and 5 `LEGACY_KEY_MAPPING` keys nothing passed in; the 25 codes the backend actually sends to the frontend are unchanged.
- Removed files no page loads: the frontend `static/js/modules/constants/message-codes.js` (nothing reads its `MessageCodes`, `createMessage` and related exports), and `templates/components/status-indicator.html` together with `status.completed.message` (all three locales), which only that template could use.
- Removed the unreachable fallback message table in `utils.js` (`getFallbackMessage`) and the message-code object branch of `showMessage`: every caller passes an already translated string and none passes a `{ code }` object, and `i18nManager` is created when `i18n.js` loads and still exists when loading translations fails, so the table was never used. Its `settings.*` keys never matched the `settingsAPI.*` codes the backend actually sends.
- Removed `scripts/validate_message_codes.py`, which always exited with code 1: none of what it reported reaches users (it compared against the frontend fallback table that is only used when i18n is not loaded, and the untranslated codes are only sent in notifications the frontend does not display), and neither the Makefile nor CI ran it.
- Removed translation keys that no code or template uses (82 in Traditional Chinese, 77 in Simplified Chinese, 78 in English), including the whole `about.contact`, `summary.*`, `themes.*`, `autoRefresh.*`, `connection.*`, `notifications.*` and `errors.*` groups, plus keys that existed in only one locale such as `app.author`, `app.credits` and `autoSubmit.autoCommitNoPrompt`. Each key was checked for dynamic key building, `data-i18n` attributes and backend message codes before removal.
- Function-level imports that can live at the top of the file were moved there; intentionally deferred imports (circular imports, Windows-only modules, the development desktop module added to sys.path at runtime, etc.) stay and now state why. Unused unpacked variables were renamed.
- The backend no longer reads or writes `~/.config/mcp-feedback-enhanced/language.json`: its only writer, `set_language()`, has had no callers since 2025-06, so the file only held stale values. The language of backend error messages is now `MCP_LANGUAGE` → `LANG` / `LC_ALL` / `LC_MESSAGES` / `LANGUAGE` → system locale → Traditional Chinese. Users who relied on that file to choose the language of error messages returned to the AI will now get it from those environment variables or the system locale; set `MCP_LANGUAGE` to pin it. Existing `language.json` files are left in place and simply ignored, and startup no longer creates the `~/.config/mcp-feedback-enhanced` directory.
- Removed the frontend's dead read of localStorage `language` (nothing in the project wrote it).

### 🔧 Other Changes
- `highlights.txt` and `release_body.md` are no longer tracked and are listed in `.gitignore`: publish.yml regenerates both on every release; they were only picked up by the release commit's `git add .`.
- Dev dependencies moved from the deprecated `[tool.uv] dev-dependencies` to the PEP 735 `[dependency-groups] dev`; `uv sync --dev` no longer prints the deprecation warning and installs the same packages.
- pre-commit now uses ruff v0.17.2 (the hook is renamed to `ruff-check`), matching `uv run ruff` and CI.
- Pinned the dev dependencies `ruff==0.17.2` and `mypy==2.4.0`: `uv.lock` is not committed, so CI resolves versions on every run, and the previous `>=` ranges could make CI fail on a new lint release without any code change, or disagree with local results. When upgrading ruff, change `pyproject.toml` and `.pre-commit-config.yaml` together.
- The Tests workflow now runs `ruff check`, `ruff format --check` and `mypy` on ubuntu; the existing mypy errors were fixed.

### ✅ Tests
- The desktop launch tests no longer replace `asyncio.sleep` for the whole process: doing so turned uvicorn server threads left over from earlier tests into busy loops fighting for the GIL, occasionally timing out the CI ubuntu job after 60 s; only the `desktop_app` module's own `asyncio` reference is replaced now.
- The `web_ui_manager` fixture now stops the uvicorn server a test started: the 8 server threads started by the integration tests used to stay alive until pytest exited.
- The i18n tests now use keys that exist in all three locales and require the result to differ from the key. The previous `common.*`, `error.connection` and similar keys were missing from the locale files, and the tests only passed because a missing key is returned as-is. The parameter test now checks that `{error}` in `error.generic` is replaced.
- The error message tests now check the built-in messages for all three languages, including that the three locales return different text, instead of mocking the function under test.
- New tests: `MCP_GZIP_LEVEL` levels 1 and 9 reach the GZip middleware and produce different compressed sizes for the same `styles.css`; the 16 message codes the backend returns to the frontend as `messageCode` must be translated in all three locales; a temp file whose mtime is in the future is still removed with `max_age=0`.
- The MCP integration tests now start the server with the current Python interpreter instead of `uv run`: when `pyproject.toml` had changed, `uv run` first synced `.venv` and rewrote the local `uv.lock`, and if an editor's language server was holding an executable in `.venv`, the sync failed and the 9 tests in `test_mcp_workflow.py` failed with it.
- New route tests: with a valid `MCP_LANGUAGE` both the feedback page and the waiting page carry the forced language, and neither does when it is invalid or unset; language-detection cases follow the new order and include invalid values; new test that an old `language.json` is ignored and no directory is created.
- Removed tests that only covered the dead code above.

---

## [v2.8.4] - 2026-10-25 - Session History Retention and Message Handling Fixes

### 🌟 Highlights
- Session history keeps earlier sessions after the MCP server restarts (#177); sessions a previous process left waiting for feedback show as "Disconnected".
- Session durations in history now come from the real creation and end times, and the retention period actually removes expired records.
- Durations in the English UI get spaces and singular/plural units (`7 seconds`, `1 minute 5 seconds`).
- A new-session notice is no longer swallowed by a heartbeat reply, so the page switches to the new session.
- After switching languages, the current session card and session history change to the new language immediately.

### 🐛 Bug Fixes
- **Session history kept only the most recent session (#177)**: the history list was built only from `/api/all-sessions`, which holds just the sessions in the current server process's memory. After restarting the MCP server, older sessions disappeared, and the next save overwrote them in `session_history.json`. History now merges the saved records with the live sessions (server data wins for the same session, no duplicates), applies the retention period, and saves the result back.
- **After a server restart, sessions left by the previous process showed "Waiting" indefinitely**: once history was merged with the saved records, a session that had not received feedback when its server process ended stayed in history as "Waiting" until the retention period expired, even though it can never receive feedback. When history loads and the live session list is read successfully, sessions that are not in it and have not finished are now marked "Disconnected" and saved back; submitted, completed, timed-out, error and expired sessions are left as they are, and nothing is marked if the live list cannot be read.
- **"About N minutes" in session history was an estimate**: without an end time, the duration was a fixed number derived from a hash of the session ID. Durations are now computed only from the session's creation and end time (falling back to the feedback submission time); if either is missing, no duration is shown.
- **Durations in the English UI ran together**: there were no spaces between numbers, units and parts, so session history and "Today's Average Duration" showed `7seconds` or `1minutes5seconds`. English now puts spaces between the number and unit and between parts, and uses the singular for a count of 1 (`1 minute 5 seconds`); Chinese stays compact (`7秒`, `1分鐘5秒`).
- **Session history retention had no effect**: timestamps were a mix of seconds and milliseconds, so the 72-hour retention effectively never expired anything. Comparisons now use seconds consistently, and records past the retention period are removed.
- **New-session notice could be swallowed by a heartbeat reply, leaving the page on the old session**: the frontend ran every WebSocket message through one shared 50ms debounce, so of two messages arriving within 50ms only the second was handled; a `session_updated` or `status_update` followed by `heartbeat_response` was dropped and the page never switched to the new session. Only the full-snapshot messages `status_update` and `session_updated` are now debounced, each by type, so bursts of the same type still collapse to the last one; `notification` and all other types are handled immediately, and different types no longer swallow each other.
- **Current session card did not follow a language switch**: prefixes such as "Session ID / Created Time / Project / AI Summary" and the duration units in history stayed in the previous language until a status change or reload. They now switch immediately.

### ✅ Tests
- `conftest.py` — removed the session-scoped `event_loop` fixture: no test used it, and pytest-asyncio 1.x no longer treats it as the event loop.
- Added `pytest-cov` to the dev dependencies: `make test-cov` from the README used to fail with `unrecognized arguments: --cov=...` (exit 4); after `uv sync --dev` it now prints the coverage table.
- New `Tests` workflow: runs the full pytest suite on ubuntu-latest and windows-latest for pushes and PRs to main; `test_resource_manager.py` now spawns its child process with `sys.executable` instead of relying on `python` being on PATH.

---

## [v2.8.3] - 2026-10-25 - Session Status After Submit and Duplicate Submissions

### 🌟 Highlights
- After you submit feedback, session history shows the session as "Submitted" instead of "Processing", and as "Completed" once the next MCP call arrives.
- The "Current Session" card on the Session Management tab shows the session's actual status on the server, and updates on reload or 🔄.
- After a page reload you can no longer submit feedback a second time, so a submission can no longer report success while never reaching the AI.

### 🐛 Bug Fixes
- **Submitting feedback left the session in `active`**: v2.6.0 (#78) inserted an `active` step between `waiting` and `feedback_submitted`, but nothing ever moves a session into `active`, so the single step taken on submit stopped at `active`. The session kept showing "Processing", the previous session was never marked `completed` on the next call, and the post-submit cleanup timer was not reset. Submitting from `waiting` now steps through `active` to `feedback_submitted`, keeping the one-way transition rule.
- **The "Current Session" card on the Session Management tab stuck at its placeholders**: the card relied only on session data the page kept in memory. After a reload that data was empty, and the server's `feedback_submitted` status was handled as "completed", which only updates existing data, so the card kept showing "Waiting", created time "--:--:--" and AI summary "Loading…". The 🔄 button just waited a second and fetched nothing. The card now uses the session marked current in `/api/all-sessions`, refetched on reload, on 🔄, after submitting feedback and when the next session arrives. Session history only re-rendered when the number of sessions changed, so it still showed "Waiting" after submitting; it now re-renders when a status changes too. The "Submitted" badge gets the same green style as "Completed" and is retranslated when you switch languages.
- **After a reload you could submit feedback a second time, and the second submission never reached the AI**: reloading the page reset the frontend's feedback state to "Waiting", so the submit button worked again; Ctrl+Enter only checked that the WebSocket was connected, so it resubmitted even without a reload. The server accepted it, overwrote the stored feedback and moved the session to `completed`, but the MCP call had already returned with the first submission, so nobody read the second one while the UI reported success. The server now ignores submissions once it has feedback, leaving the content and status untouched, and replies "Feedback already submitted, please wait for next MCP call". After a reload the frontend takes the server's status and shows "Submitted", and both the button and Ctrl+Enter are blocked. The next MCP call's new session submits as usual.

### ✅ Tests
- `conftest.py` — for the whole test run `USERPROFILE`/`HOME` point to a pytest temp directory (inherited by subprocesses), and before and after the tests it checks that `Path.home()`, the language settings file and `feedback_session.TEMP_DIR` are not under the real home directory, failing otherwise; running the tests no longer writes to your own settings.
- `helpers/mcp_client.py` — before starting the MCP server, `smart_browser_open`/`webbrowser.open` are replaced with stand-ins that only record the URL, so no real browser opens; the subprocess gets `MCP_TEST_MODE=true` and `MCP_WEB_PORT=0` and takes a port from the OS, so a busy port 8765 no longer gets the instance you are using shut down.
- `test_resource_manager.py` — registered pytest's own PID with `ResourceManager`, whose `atexit` cleanup then terminated pytest on exit, so on Windows the run ended with exit code 15 even when every test passed; it now registers a short-lived subprocess started by a fixture and clears the registry after each test.
- `test_web_ui.py` — new `test_second_submission_is_ignored`: a second submission must not overwrite the feedback, images or settings or advance the status, and only gets `feedback.alreadySubmitted` back. The existing `test_session_feedback_submission` asserts the session reaches `feedback_submitted` after submitting; it failed before the fix, with the session stuck in `active`, and passes now.
- Removed three outdated tests of implementations that no longer exist: `test_i18n_with_web_ui_manager` (`WebUIManager.i18n` was removed), `test_session_lifecycle` (`update_status` was replaced by the one-way `next_step`; creating and switching sessions is covered in `test_web_ui.py`) and `test_status_update_resets_timer` (it checked whether an internal Timer object was replaced).
- The `pytest.ini` header changed from `[tool:pytest]` to `[pytest]`: the whole file used to be ignored, and now `testpaths`, strict markers/config, `asyncio_mode=auto`, `timeout=60` and `filterwarnings` all take effect.
- The `dev` extras in `pyproject.toml` gain `pytest-timeout>=2.1.0`, so after `pip install -e ".[dev]"` the tests no longer fail with `Unknown config option` for the `timeout` setting.

---

## [v2.8.2] - 2026-10-25 - Blocking Cross-Site Writes to /api/*

### 🌟 Highlights
- Cross-origin pages can no longer rewrite settings, session history or the log level through `/api/*`, so they cannot turn on auto-submit for you.
- Every field in the session details dialog is escaped, so tampered session history is no longer executed as HTML.

### 🔒 Security
- **Cross-site writes to HTTP `/api/*` and stored XSS in session details fixed**: reported privately as `GHSA-x999-258q-h9mh`. The v2.6.1 Origin check only covered `/ws`; `/api/save-settings`, `/api/save-session-history`, `/api/add-user-message`, `/api/clear-settings` and `/api/log-level` checked neither `Origin` nor `Content-Type`, and `request.json()` parses the body whatever the declared type. A cross-origin `POST` with `Content-Type: text/plain` is a CORS simple request that browsers send without a preflight: the page cannot read the response, but the write happens. An attacker could enable auto-submit and swap the prompt so the legitimate WebSocket connection submits feedback on its own.
  - Every non-GET/HEAD/OPTIONS request to `/api/*` now goes through one middleware, so endpoints added later are covered too: an `Origin` that fails the same check as `/ws` gets **403**, and a `Content-Type` other than `application/json` gets **415**, which forces cross-origin requests into a preflight the server never approves. Non-browser clients without an `Origin` header and desktop WebView origins are still allowed.
  - When bound to `0.0.0.0` or `::`, the `Origin` host:port must now equal the request's `Host` header instead of matching on port alone; previously any site on the same port passed, for `/ws` as well.
  - The session details dialog interpolated `session_id`, `status`, `project_directory` and other fields into HTML unescaped, so a tampered `session_history.json` became stored DOM XSS; all of them are escaped now. The shared `escapeHtml` left quotes unescaped, letting attribute values break out; it now escapes `"` and `'` too. Stored prompt and custom-sound IDs, which also come from the settings file, are escaped the same way.
  - Thanks to the reporter for the detailed analysis.

### ✅ Tests
- `test_cross_site_writes.py` — replays the reported cross-origin requests against every write endpoint and checks for 403/415 with the files unchanged; same-origin JSON, desktop WebView and Origin-less requests still succeed; on a `0.0.0.0` bind only an `Origin` equal to `Host` passes, and `/ws` follows the same rule. Settings files are always written under `tmp_path`.
- `test_websocket_origin.py` — the case that locked in "port-only match on 0.0.0.0" now checks the `Host` header, with new cases for `::`, IPv6, and a missing or malformed `Host`.

---

## [v2.8.1] - 2026-09-07 - Desktop Fallback Follow-ups

### 🌟 Highlights
- stderr notices are now protected writes and never fall back to stdout (the MCP protocol channel) when `sys.stderr` is None.
- The desktop shell only counts as failed on a non-zero exit, so closing the window yourself no longer demotes the process to web mode; the failure reason is printed for the user.

### 🐛 Bug Fixes
- **Fallback notices now use a protected stderr write**: the two `sys.stderr.write` calls added in v2.8.0 were the first unguarded stderr writes on the request path; when the host has closed the stderr pipe (EPIPE) they turned the whole tool call into an exception, and `MCP_DESKTOP_MODE` was never cleared so the next call repeated it. They now go through `user_notice`, which fails silently like `debug_log`, and the desktop launch failure reason (exit code, stderr tail) is printed for the user — a Defender quarantine, a glibc mismatch and a Gatekeeper block each need a different remedy, so the reason is what makes a report actionable.
- **Only a non-zero exit counts as a launch failure**: v2.8.0 treated any exit during the observation window as failure, so a user closing the window within two seconds (exit 0) was demoted to web mode, contradicting the v2.7.2 "window closed" semantics. Exit 0 keeps the existing behaviour.
- **No stdout fallback when `sys.stderr` is None**: `print(file=sys.stderr)` falls back to `sys.stdout` under pythonw or when the host has closed stderr — that is the MCP protocol channel, and a single notice line breaks client parsing. `debug_log` and `user_notice` now share `_write_stderr`, which captures the stream first and returns when it is None.
- **Bounded stderr tail read**: the native process may hand its stderr write end to WebView descendants, and `read()` would wait for all of them to close; it now uses `communicate(timeout=1)` and reports only the exit code on timeout.

### 🔧 Other Changes
- README (three languages): the "Install as app" paragraph claimed "each call still opens a system browser tab", which is wrong while the tab keeps its connection (it is reused); reworded to "once the app window is closed the next call opens a normal browser tab"; "exits right after launch" is now "exits with an error right after launch".

### ✅ Tests
- `test_desktop_fallback.py` — stderr assertions now run with `MCP_DEBUG=false` (conftest enables debug by default, so the previous tests still passed if the URL regressed to debug-only output); the early-exit tests use a fake binary in a temp directory instead of the committed binary; new cases: a descendant holding stderr does not hang, exit 0 is not a failure, and the two launcher copies are byte-identical (`build_desktop.py` copying had let them drift once).
- `test_user_notice.py` — stdout must stay empty when `sys.stderr` is None (both `debug_log` and `user_notice`), `user_notice` ignores `MCP_DEBUG`, and a closed stderr does not raise.

---

## [v2.8.0] - 2026-09-07 - Desktop Application Enters Maintenance-Only

### 🌟 Highlights
- The desktop application (Tauri shell) is **maintenance-only** from this release: no new features, only security fixes and "cannot launch at all" compatibility fixes, scheduled for removal in v3. The binaries still ship with this release; to keep using it, pin the version in your IDE's MCP configuration (see "Desktop application maintenance status" in the README).
- When the desktop shell cannot start (quarantined by antivirus, glibc too old, blocked by Gatekeeper, exits right after launch) the server no longer waits silently until the timeout: the process falls back to the browser and prints the URL to stderr.

### 🐛 Bug Fixes
- **The desktop-mode browser fallback never worked**: on `launch_desktop_app` failure the code called `open_browser`, which skipped itself because of the very same `MCP_DESKTOP_MODE` variable, leaving the user with no UI at all until the timeout returned "no user response". The fallback now lives at the single dispatch point: desktop launch fails → drop `MCP_DESKTOP_MODE` for this process → use the existing `smart_open_browser` (active-tab detection and session-update notification included), so every later call goes straight to the web UI without retrying the desktop shell or opening another tab; restarting the MCP server re-reads the IDE configuration and retries the desktop shell.
- **A native process that exits right after launch now counts as a launch failure**: both Python launchers only did `Popen` and slept two seconds without checking the exit code, so a binary quarantined by Defender or missing glibc was still reported as "started". Exiting within the observation window is now a failure (with exit code and stderr tail) handed to the fallback above.
- **Browser launch failure is no longer silent**: when `webbrowser.open` returns False (e.g. a headless SSH host) or all three WSL launch methods fail, the URL is printed to stderr unconditionally so the user can open it manually, instead of only appearing with `MCP_DEBUG=true`.

### 🔧 Other Changes
- `build-desktop.yml` trigger paths exclude `src-tauri/python/**`: pure-Python launcher changes no longer trigger the four-platform native rebuild and binary commit.
- The two launcher copies (`src/mcp_feedback_enhanced/desktop_app/` and `src-tauri/python/`) are now identical, so `build_desktop.py` no longer reverts the shipped copy to the older code when it copies.
- README (three languages) gains a "Desktop application maintenance status" section with migration options; SECURITY.md adds the desktop component scope and splits the support table into "latest 2.x" vs "pinned older releases receive no back-ports".
- This release does **not** touch Rust, the native binaries, the desktop WebView Origin allow-list on `/ws`, or the renovate configuration.

### ✅ Tests
- `test_desktop_fallback.py` — with the desktop module missing the URL really reaches the browser and the process leaves desktop mode; a second call reuses the existing tab instead of retrying the desktop shell; a healthy desktop shell never touches the browser; a native process exiting right after launch is a failure; a browser that cannot be opened prints the URL to stderr. The tests only intercept the lowest-level `webbrowser.open` and keep the real desktop-mode guard; four of the five were confirmed failing before the fix.

---

## [v2.7.2] - 2026-09-07 - Explicit Wrap-up When Nobody Answers

### 🌟 Highlights
- On timeout or when the user closes the UI, the tool now returns an explicit "no user response — finish the task" instruction, and the tool description's usage rules allow stopping in that case, so clients no longer treat it as a generic error and retry forever (#125).
- Closing the feedback tab/window ends the wait after a 75-second grace period instead of blocking until the timeout (10 minutes by default) (#162).

### 🐛 Bug Fixes
- **Timeout now returns a stop instruction** ([#125](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/125)): the old code handed `TimeoutError` to `ErrorHandler`, which told the model "Operation timeout / Increase timeout settings / Retry the operation later" — and a client that follows that advice calls the tool again, looping forever while the user is away. Timeouts (and the UI-closed case below) now return "No user response (reason). Treat the user as away: finish the task now and do NOT call interactive_feedback again", in Chinese and English; the tool description's USAGE RULES now list "no user response" as a valid stopping condition so the description and the reply no longer contradict each other. Only the wait itself takes this path — a `TimeoutError` raised after feedback was received (saving to disk, image processing; `OSError` ETIMEDOUT included) is still treated as an error and never turns real feedback into "no response".
- **Closing the UI ends the wait** ([#162](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/162)): the frontend only cleaned up locally on close, so the backend never knew and `wait_for_feedback` sat there until the timeout. A 75-second grace timer now starts when the session's registered WebSocket disconnects and is cancelled by any reconnect (F5, a brief drop, another tab); only an unanswered grace period counts as "user closed the UI". Why 75 s: the backend registers only the newest connection, and an older tab is not detected as stale until its next application-level heartbeat (60 s), so the grace must exceed "one heartbeat period + the first reconnect" or the "open two tabs, close the newer one" case would declare the user gone. That is the only path it guarantees, on a healthy network; if the first reconnect fails and the full backoff sequence runs (1+2+4+8+16 s + jitter, another 31-36 s) the grace is exceeded and the session wraps up as disconnected. Feedback submission and giving up are linearized under one lock: `Timer.cancel()` cannot stop a callback that has already started, so the callback invalidates itself by identity check; submission is an atomic write, so whatever the waiter reads is complete feedback (never text without the images still being processed), and feedback that arrives always wins. Sessions that never had a frontend connection (e.g. no browser opened) keep the original timeout behaviour.
- The frontend's session-timeout notification (`user_timeout`) now records its reason first, so the text returned to the AI is no longer the default "waiting for feedback".

### ⚠️ Behaviour Change
- Any WebSocket interruption longer than 75 s — laptop sleep, the browser discarding a background tab, an SSH tunnel dropping — now ends the wait with "user closed the feedback UI" instead of running to the timeout. This is deliberate: closing the window and leaving the AI hanging for ten minutes is far more common and more annoying than the occasional early wrap-up.

### ✅ Tests
- `test_feedback_timeout.py` — the timeout reply must carry the stop instruction and must not suggest retrying; a `TimeoutError` after feedback arrived must not be reported as no response; the tool description must allow stopping on no response; disconnect grace: ends the wait within the grace window (not at the timeout), a reconnect within the window does not, no timer starts once feedback exists, feedback arriving after the callback wrote TIMEOUT still wins, and a callback firing mid-submission never yields partial feedback; the `/ws` wiring (registered-socket disconnect starts the grace, reconnect cancels it) is covered through `TestClient.websocket_connect`.
- Verified with a real MCP stdio round-trip plus Chromium: open UI → F5 → still waiting → close tab → stop instruction after the grace period; with no frontend at all, the timeout returns the same instruction.

---

## [v2.7.1] - 2026-09-06 - MCP_LANGUAGE Precedence & Linux Desktop Compatibility

### 🌟 Highlights
- `MCP_LANGUAGE` now truly forces the UI language — it is no longer overridden by a language previously saved from the UI (#189).
- The Linux desktop binary now runs on Ubuntu 22.04 / Debian 12 and newer (glibc requirement lowered from 2.39 to 2.34, #165).

### 🐛 Bug Fixes
- **`MCP_LANGUAGE` now has the highest priority** ([#189](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/189)): the README described it as "force UI language", yet the detection order put the language saved from the UI ahead of it, so `MCP_LANGUAGE=zh-CN` could still render Traditional Chinese. The order is swapped; with the variable set, the in-UI language picker only applies to the current session.
- **Linux desktop binary is now built on ubuntu-22.04** ([#165](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/165)): the ubuntu-latest build required `GLIBC_2.39` and only ran on Ubuntu 24.04+; the rebuilt binary tops out at `GLIBC_2.34`.
- **Fixed the desktop-binary commit step for single-platform builds**: `download-artifact` does not create a per-artifact subdirectory when only one artifact exists, so the directory-based copy loop reported 0/4 and skipped the commit. Binaries are now uploaded and located by their final file name.

### 🔧 Other Changes
- Fixed the renovate config warning (`vulnerabilityAlerts.prPriority` is not allowed; expressed via an `isVulnerabilityAlert` packageRule instead).
- Raised dependency lower bounds in one go to the last vulnerability-fix versions recorded by OSV (aiohttp 3.14.3, starlette 1.3.1, jinja2 3.1.6, tauri 2.11.1, tokio 1.44.2, …); resolved versions are unchanged. Renovate now uses `rangeStrategy=widen`, so in-range updates no longer bump the lower bound on every patch.

---

## [v2.7.0] - 2026-09-06 - Upgrade to fastmcp 4 / mcp 2

### 🌟 Highlights
- Upgraded to fastmcp 4.x and MCP Python SDK 2.x; the server still serves legacy-protocol clients, and tool contracts and return shapes are unchanged.
- Fixed a boundary condition in `ResourceManager` temp-file cleanup that caused a flaky test.

### 🔧 Other Changes
- **Upgraded `fastmcp` to 4.x and `mcp` to 2.x** (supersedes renovate [#239](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/239) and [#240](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/240)): mcp 1.x and fastmcp 3.x are now in security-fix-only maintenance mode. fastmcp 4 depends on `mcp>=2,<3`, so the two must move together — merging only one leaves the dependency set unresolvable and the package uninstallable (same failure class as #213/#217/#221/#228). The only server-side change is constructing `ImageContent` with mcp 2's canonical field name `mime_type`; the wire format is still `mimeType`. Verified `list_tools`/`get_system_info` over stdio, and the integration tests using a legacy-protocol (2024-11-05) client all pass.
- **Fixed the age boundary in `ResourceManager.cleanup_temp_files`**: `file_age > max_age` became `>=`. `cleanup_all` passes `max_age=0` to mean "remove everything", but a just-created file has an age of exactly 0 under Windows timestamp granularity and was skipped.

### ✅ Tests
- `test_image_content.py` — no longer tied to mcp 1's internal module name or the pre-snake_case `model_dump()` fields; verifies the wire contract via `type(...) is ImageContent` and `model_dump(by_alias=True)`.

---

## [v2.6.2] - 2026-08-25 - Timeout Clamping & Tool Contract

### 🐛 Bug Fixes
- **Clamped `interactive_feedback` timeout** ([#212](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/212)): clients sometimes pass an unusably small value — the report shows Cursor passing `timeout=1`, so the feedback UI expired before it could be used. The server now clamps to 60–86400 seconds. Clamping was chosen over pydantic `ge`/`le` validation because a validation failure aborts the whole tool call; for a human-in-the-loop tool, continuing with a safe value is more useful than failing.
- **Fixed the early-exit margin in `wait_for_feedback`**: the old logic used `max(timeout - 1, 5)` for `timeout <= 30`, which *extended* a 1-second timeout to 5 seconds — the opposite of finishing early to avoid racing the MCP-layer timeout.

### 🔧 Other Changes
- **Declared a precise tool return type** (`list[TextContent | ImageContent]` instead of bare `list`), related to [#234](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/234). A bare `list` gave FastMCP nothing to work with, so it generated a wrap-result `outputSchema` (`{"result": {"type": "array"}}` plus `x-fastmcp-wrap-result`) and additionally wrapped content blocks into `structuredContent`. With the precise annotation FastMCP recognises content blocks and that schema is gone.
  - This does **not** mean the violation in #234 was reproduced. Under FastMCP 3.4.7, both before and after this change, `CallToolResult` from `interactive_feedback` and `get_system_info` contained the schema-required `content` field. See the issue for the full investigation.

### ✅ Tests
- `test_feedback_timeout.py` — clamp bounds, bad-type tolerance, and that the margin never extends the wait
- `test_tool_contract.py` — guards the return annotation against regressing to a bare `list`

---

## [v2.6.1] - 2026-08-25 - Security Fix & Maintenance Resumed

### 🌟 Version Highlights
Removes the known command execution risk, fixes Cross-Site WebSocket Hijacking, and repairs
the compatibility break that made fresh installs completely unusable. Maintenance has resumed,
with scope currently focused on security and install-breaking compatibility issues.

### 🔒 Security
- **Command execution removed** ([#219](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/219)): earlier versions accepted a `run_command` message over the **unauthenticated** WebSocket endpoint `/ws` and executed it. The guard was a shell-metacharacter blocklist, but since execution used `shell=False`, metacharacters were never the risk — `cat`, `curl`, `wget`, `python`, and `powershell` passed straight through. The auto-command feature was also **enabled by default**.
  - The feature was **removed entirely** (backend handler, session methods, frontend UI, settings, i18n strings) rather than hardened. A blocklist cannot safely permit arbitrary executables.
  - Added `tests/unit/test_no_command_execution.py` to prevent reintroduction.
  - Affected versions: **2.6.0 and all earlier**. Please upgrade.
- **Cross-Site WebSocket Hijacking (CSWSH) fixed**: reported privately as `GHSA-cmr5-gpm3-79vf` (critical, CVSS 9.6) and `GHSA-2wx7-r4rh-f663` (high). Browsers are **not** restricted by the same-origin policy when opening a WebSocket, so a malicious page could make the victim's browser connect to `ws://127.0.0.1:<port>/ws` and send messages — `/ws` accepted any `Origin` and called `accept()` without validation. Combined with `run_command` above, this escalated to remote code execution; the loopback binding did not help, because the browser itself is local.
  - Fixed with two independent layers: (1) command execution removed entirely, eliminating the escalation path; (2) `/ws` now validates `Origin` **before** `accept()`, allowing only loopback origins on the server's own port, the bound host itself, and desktop WebView schemes. Non-browser clients without an `Origin` header (such as the desktop app) are still permitted, since a cross-origin page cannot suppress the header.
  - Cross-origin attempts are rejected with HTTP 403 before the handshake completes. `tests/unit/test_websocket_origin.py` uses the exact origins from the reported proofs of concept.
  - Thanks to both reporters for the detailed analysis and working PoCs.

### 🐛 Bug Fixes
- **Fixed Web UI returning 500** ([#213](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/213), [#217](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/217), [#221](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/221), [#228](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/228)): newer Starlette changed the `TemplateResponse` signature, so the old call raised `TypeError: unhashable type: 'dict'` and no page would load for anyone installing via `uvx @latest`. Credit to [#220](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/220) (also reported in [#214](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/214), [#215](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/215), [#216](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/216)).
- **Fixed missing `session_id` in template context**: `feedback.html` needs it to initialize the frontend, but it was never passed.
- **Fixed image serialization** ([#154](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/154), [#168](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/168), [#180](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/180) and related): switched to standard `mcp.types.ImageContent`. The old implementation returned `fastmcp.utilities.types.Image`, which fails on newer FastMCP with `Output validation error: outputSchema defined but no structured output returned`. Verified via a real MCP round-trip for PNG/JPEG/GIF/WebP. Credit to [#171](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/171).

### 🔧 Other Changes
- **Dependency upper bounds added** so an upstream breaking change cannot silently break installs again. `starlette` is now an explicit direct dependency.
- **Documentation corrected**: removed the "dramatically reducing platform costs" claim (Cursor moved to token-based pricing, so the premise no longer holds); `MCP_WEB_HOST=0.0.0.0` is no longer recommended and now carries a security warning pointing to SSH port forwarding.
- Added [SECURITY.md](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/SECURITY.md) covering supported versions, known risks, and reporting.
- Fixed `.gitignore` silently excluding the entire `tests/` suite via a repo-wide `test_*.py` rule.

### ⚠️ Known Unfixed Issues
Pre-existing limitations, outside the current maintenance scope:
- Web UI and WebSocket have **no authentication** (Origin validation stops malicious web pages, but not local processes)
- Pre-existing test failures around session status transitions, i18n environment detection, and cleanup timers

---

## [v2.5.6] - 2025-06-21 - Settings Save Mechanism Optimization & Interface Enhancement

### 🌟 Version Highlights
Refactored settings save mechanism to resolve language switching save issues, and added visual icons to settings interface for enhanced user experience.

### 🚀 Improvements
- 🔨 **Settings Save Mechanism Refactoring**: Completely removed localStorage dependency, switched to unified FastAPI backend save mechanism
  - Resolved settings not saving correctly during language switching
  - Removed debounce mechanism to ensure immediate settings save
  - Enhanced reliability and consistency of settings save
- ✨ **Settings Interface Enhancement**: Added corresponding icons to functional sections within settings tabs
  - Improved interface visual effects and user experience
  - More intuitive feature identification

### 🛠️ Technical Improvements
- 📊 **Unified Storage Architecture**: All settings now use JSON file storage for cross-environment consistency
- 🔧 **Code Simplification**: Removed complex localStorage-related code, reducing maintenance costs

---

## [v2.5.5] - 2025-06-21 - SSH Remote Development Support & Stability Enhancement

### 🌟 Version Highlights
Added SSH remote development environment support, resolving Web UI access issues in remote development scenarios. Enhanced macOS compilation support and desktop application stability for improved developer experience.

### ✨ New Features
- 🌐 **SSH Remote Development Support**: Added `MCP_WEB_HOST` environment variable for configuring web server host binding
  - Defaults to `127.0.0.1` for security
  - Can be set to `0.0.0.0` to allow remote access
  - Resolves access issues in remote development environments like Cursor SSH Remote
- 🍎 **Enhanced macOS Compilation Support**: Added `.cargo/config.toml` configuration file
  - Supports Intel (x86_64) and Apple Silicon (aarch64) architectures
  - Resolves macOS PyO3 undefined dynamic_lookup compilation issues
  - Follows PyO3 official recommended best practices

### 🚀 Improvements
- 📝 **Tool Documentation Optimization**: Moved LLM instructions to tool docstring for improved token efficiency
- 🎨 **Simplified User Configuration**: Removed complex Cursor rules configuration
- 📊 **Enhanced AI Work Summary Markdown**: Improved Markdown rendering effects and compatibility
- 🔄 **Session History Process Optimization**: Enhanced session saving and management mechanisms

### 🐛 Bug Fixes
- 🖥️ **Desktop Application MCP Protocol Fix**: Fixed MCP protocol communication pollution issues in desktop mode
- 📦 **Packaging Process Fix**: Fixed multi-platform desktop application packaging and publishing issues
- 🔧 **Release Process Optimization**: Improved stability of automated release workflows
- 🔥 **Removed ESC Shortcut**: Removed ESC shortcut functionality that could cause accidental closure

### 🛠️ Technical Improvements
- 🏗️ **Enhanced Build System**: Improved cross-platform compilation configuration and dependency management
- 📚 **Documentation Automation**: Enhanced tool self-documentation following FastMCP best practices
- 🔍 **Enhanced Debugging Features**: Added more detailed debugging information and error handling

### 📋 Usage Instructions
- **SSH Remote Development**: Set `"MCP_WEB_HOST": "0.0.0.0"` in MCP configuration to allow remote access
- **Local Development**: Keep default `"MCP_WEB_HOST": "127.0.0.1"` for security
- **macOS Development**: New compilation configuration will take effect automatically without additional setup

---

## [v2.5.0] - 2025-06-15 - Desktop Application & Performance Optimization

### 🌟 Version Highlights
Introducing cross-platform desktop application supporting Windows, macOS, and Linux. Significant performance improvements with debounce/throttle mechanisms and enhanced system stability.

### ✨ New Features
- 🖥️ **Desktop Application**: Native cross-platform desktop app based on Tauri framework, supporting Windows x64, macOS (Intel/Apple Silicon), Linux x64
- 📊 **Server-side Session History Storage**: Session records migrated from localStorage to server-side local file storage for improved data consistency and reliability
- 🔧 **Multi-platform Build Support**: Complete CI/CD pipeline supporting automated multi-platform desktop application builds
- 📝 **Desktop Mode Configuration**: Added `MCP_DESKTOP_MODE` environment variable for desktop/web mode switching
- 📋 **AI Work Summary Markdown Display**: Support for Markdown syntax rendering including headers, bold text, code blocks, lists, links and other formats

### 🚀 Improvements
- ⚡ **Significant Performance Enhancement**: Introduced debounce/throttle mechanisms to reduce unnecessary rendering and network requests
- 🌐 **Network Connection Stability**: Improved WebSocket reconnection mechanism with network status detection and intelligent reconnection
- 🎨 **UI Rendering Optimization**: Optimized rendering performance for session management, statistics, and status indicators
- 📱 **Responsive Improvements**: Adjusted heartbeat frequency and timeout thresholds to reduce system load
- 🔄 **Enhanced Modularity**: Optimized JavaScript module structure with better logging management

### 🐛 Bug Fixes
- 🌐 **Network Reconnection Improvements**: Optimized reconnection algorithm with exponential backoff strategy and random jitter
- 🖥️ **Desktop Mode Adaptation**: Fixed browser auto-launch issues in desktop mode
- 📊 **Rendering Performance Fixes**: Resolved duplicate rendering and unnecessary state update issues

### 🛠️ Technical Improvements
- 🏗️ **Build Process Optimization**: Added Makefile desktop application build commands supporting debug/release modes
- 📦 **Dependency Management**: Integrated Rust toolchain supporting cross-platform compilation and packaging
- 🔍 **Enhanced Development Tools**: Added environment checks, build validation, and cleanup tools
- 📚 **Documentation Enhancement**: Added desktop application build guide and workflow documentation
- 🔒 **Security Enhancement**: Introduced DOMPurify for XSS protection ensuring content security

### 📋 Usage Instructions
- **Desktop Mode**: Set `"MCP_DESKTOP_MODE": "true"` in MCP configuration (refer to `examples/mcp-config-desktop.json`)
- **Web Mode**: Set `"MCP_DESKTOP_MODE": "false"` in MCP configuration (default, refer to `examples/mcp-config-web.json`)
- **Test Desktop Mode**: `uvx mcp-feedback-enhanced@latest test --desktop`
- **Build Desktop Application**: `make build-desktop-release`

---

## [v2.4.3] - 2025-06-14 - Session Management Refactoring & Audio Notifications

### 🌟 Version Highlights
Migrated session management from sidebar to dedicated tab, resolving browser compatibility issues. Added audio notification system with custom audio support.

### ✨ New Features
- 🔊 **Audio Notification System**: Play audio alerts for session updates, supports built-in and custom audio uploads
- 📚 **Session History Management**: Local session record storage with export and cleanup functionality
- 💾 **Input Height Memory**: Automatically save and restore textarea input height settings
- 📋 **One-Click Copy**: Project path and session ID support click-to-copy

### 🚀 Improvements
- 📋 **Session Management Refactoring**: Migrated from sidebar to "Session Management" tab, fixing button click issues in small windows
- 🎨 **Interface Layout Optimization**: AI summary auto-expansion, submit button repositioning, removed redundant descriptions
- 🌐 **Multilingual Enhancement**: Added tooltip and button multilingual support

### 🐛 Bug Fixes
- Fixed current session details button unresponsive issue
- Fixed session details modal close delay issue
- Fixed audio notification language initialization issue
- Corrected auto-submit processing logic

---

## [v2.4.2] - Web-Only Architecture Refactoring & Smart Feature Enhancement

### 🌟 Version Highlights
This version underwent major architectural refactoring, **completely removing PyQt6 GUI dependencies** and transitioning to a pure Web UI architecture, dramatically simplifying deployment and maintenance. Additionally, multiple smart features were added, including prompt management, auto-submit, session management, and more, comprehensively enhancing user experience and work efficiency.

### 🔄 Major Architectural Changes
- 🏗️ **Complete PyQt6 GUI Removal**: Thoroughly removed desktop application dependencies, simplifying installation and deployment processes
- 🌐 **Pure Web UI Architecture**: Unified use of Web interface, supporting all platforms and environments
- 📦 **Dramatically Simplified Dependencies**: Removed PyQt6, related GUI libraries and other heavy dependencies, significantly reducing installation package size
- 🚀 **Simpler Deployment**: No need to consider GUI environment configuration, suitable for all development environments

### ✨ Brand New Features
- 📝 **Smart Prompt Management System**:
  - CRUD operations for common prompts (Create, Edit, Delete, Use)
  - Usage frequency statistics and intelligent sorting
  - Quick selection and one-click application functionality
  - Support for auto-submit marking and priority display
- ⏰ **Auto-Timed Submit Feature**:
  - Configurable countdown timer from 1-86400 seconds
  - Visual countdown display and status indicators
  - Deep integration with prompt management system
  - Support for pause, resume, and cancel operations
- 📊 **Session Management & Tracking**:
  - Real-time current session status display
  - Session history records and statistical analysis
  - Today's session count and average duration statistics
  - Session detail viewing and management functions
- 🔗 **Connection Monitoring System**:
  - Real-time WebSocket connection status monitoring
  - Latency measurement and connection quality indicators
  - Auto-reconnection mechanism and error handling
  - Detailed connection statistical information
- ⌨️ **Enhanced Shortcuts**: Added Ctrl+I quick focus input box feature (Thanks @penn201500)

### 🚀 Feature Improvements
- 🎨 **Comprehensive UI/UX Optimization**:
  - Added left session management panel with collapse/expand support
  - Top connection status bar with real-time system status display
  - Responsive design adapting to different screen sizes
  - Unified design language and visual style
- 🌐 **Enhanced Multi-language System**:
  - Optimized language switching mechanism with instant switching support
  - Added extensive translation text, improving localization coverage
  - Improved language selector UI with dropdown design
  - Fixed display issues during language switching
- 🖼️ **Image Settings Integration**:
  - Moved image settings from workspace to settings tab
  - Unified settings management interface
  - Improved organization and layout of setting items
- 📱 **Interface Layout Optimization**:
  - Adjusted layout to accommodate multi-language display requirements
  - Optimized button styles and spacing
  - Improved visual design of form elements
  - Enhanced accessibility and usability

### 🐛 Bug Fixes
- 🔧 **Session Management Fixes**:
  - Fixed session statistics information not updating correctly
  - Fixed session count calculation errors
  - Improved session state tracking mechanism
- 🎯 **Prompt Feature Fixes**:
  - Fixed common prompt management unable to correctly set auto-submit
  - Improved prompt selection and application logic
- 🌐 **Localization Switch Fixes**:
  - Fixed partial text not updating during language switching
  - Improved multi-language text loading mechanism
- 🏗️ **Architecture Stability Fixes**:
  - Fixed session management initialization issues
  - Improved error handling and resource cleanup
  - Optimized module loading order and dependencies

### 🛠️ Technical Improvements
- 📦 **Modular Architecture**:
  - Complete JavaScript code modular refactoring
  - Adopted ES6+ syntax and modern development patterns
  - Clear module separation and responsibility division
- 📊 **Performance Enhancement**:
  - Optimized WebSocket communication efficiency
  - Improved frontend resource loading speed
  - Reduced memory usage and CPU load

### 📚 Documentation Updates
- 📖 **Architecture Documentation Update**: Updated system architecture description to reflect Web-Only design
- 🔧 **Installation Guide Simplification**: Removed GUI-related installation steps and dependency descriptions
- 🖼️ **Screenshot Updates**: Updated all interface screenshots to showcase new Web UI design
- 📋 **Enhanced API Documentation**: Added API descriptions for new features like prompt management and auto-submit

---

## [v2.3.0] - System Stability & Resource Management Enhancement

### 🌟 Highlights
This version focuses on improving system stability and user experience, particularly solving the browser launch issue in Cursor SSH Remote environments.

### ✨ New Features
- 🌐 **SSH Remote Environment Support**: Solved Cursor SSH Remote browser launch issues with clear usage guidance
- 🛡️ **Error Message Improvements**: Provides more user-friendly error messages and solution suggestions when errors occur
- 🧹 **Auto-cleanup Features**: Automatically cleans temporary files and expired sessions to keep the system tidy
- 📊 **Memory Monitoring**: Monitors memory usage to prevent system resource shortage

### 🚀 Improvements
- 💾 **Resource Management Optimization**: Better system resource management for improved performance
- 🔧 **Enhanced Error Handling**: Provides clearer explanations and solutions when problems occur
- 🌐 **Connection Stability**: Improved Web UI connection stability
- 🖼️ **Image Upload Optimization**: Enhanced stability of image upload functionality
- 🎯 **Auto-focus Input Box**: Automatically focus on feedback input box when window opens, improving user experience (Thanks @penn201500)

### 🐛 Bug Fixes
- 🌐 **Connection Issues**: Fixed WebSocket connection related problems
- 🔄 **Session Management**: Fixed session state tracking issues
- 🖼️ **Image Processing**: Fixed event handling issues during image upload

---

## [v2.2.5] - WSL Environment Support & Cross-Platform Enhancement

### ✨ New Features
- 🐧 **WSL Environment Detection**: Automatically identifies WSL environments and provides specialized support logic
- 🌐 **Smart Browser Launching**: Automatically invokes Windows browser in WSL environments with multiple launch methods
- 🔧 **Cross-Platform Testing Enhancement**: Test functionality integrates WSL detection for improved test coverage

### 🚀 Improvements
- 🎯 **Environment Detection Optimization**: Improved remote environment detection logic, WSL no longer misidentified as remote environment
- 📊 **System Information Enhancement**: System information tool now displays WSL environment status
- 🧪 **Testing Experience Improvement**: Test mode automatically attempts browser launching for better testing experience

---

## [v2.2.4] - GUI Experience Optimization & Bug Fixes

### 🐛 Bug Fixes
- 🖼️ **Image Duplicate Paste Fix**: Fixed the issue where Ctrl+V image pasting in GUI would create duplicate images
- 🌐 **Localization Switch Fix**: Fixed image settings area text not translating correctly when switching languages
- 📝 **Font Readability Improvement**: Adjusted font sizes in image settings area for better readability

---

## [v2.2.3] - Timeout Control & Image Settings Enhancement

### ✨ New Features
- ⏰ **User Timeout Control**: Added customizable timeout settings with flexible range from 30 seconds to 2 hours
- ⏱️ **Countdown Timer**: Real-time countdown timer display at the top of the interface for visual time reminders
- 🖼️ **Image Size Limits**: Added image upload size limit settings (unlimited/1MB/3MB/5MB)
- 🔧 **Base64 Compatibility Mode**: Added Base64 detail mode to improve image recognition compatibility with AI models
- 🧹 **UV Cache Management Tool**: Added `cleanup_cache.py` script to help manage and clean UV cache space

### 🚀 Improvements
- 📚 **Documentation Structure Optimization**: Reorganized documentation directory structure, moved images to `docs/{language}/images/` paths
- 📖 **Cache Management Guide**: Added detailed UV Cache management guide with automated cleanup solutions
- 🎯 **Smart Compatibility Hints**: Automatically display Base64 compatibility mode suggestions when image upload fails

### 🐛 Bug Fixes
- 🛡️ **Timeout Handling Optimization**: Improved coordination between user-defined timeout and MCP system timeout
- 🖥️ **Interface Auto-close**: Fixed interface auto-close and resource cleanup logic after timeout
- 📱 **Responsive Layout**: Optimized timeout control component display on small screen devices

---

## [v2.2.2] - Timeout Auto-cleanup Fix

### 🐛 Bug Fixes
- 🔄 **Timeout Auto-cleanup**: Fixed GUI/Web UI not automatically closing after MCP session timeout (default 600 seconds)
- 🛡️ **Resource Management Optimization**: Improved timeout handling mechanism to ensure proper cleanup and closure of all UI resources on timeout
- ⚡ **Enhanced Timeout Detection**: Strengthened timeout detection logic to correctly handle timeout events in various scenarios

---

## [v2.2.1] - Window Optimization & Unified Settings Interface

### 🚀 Improvements
- 🖥️ **Window Size Constraint Removal**: Removed GUI main window minimum size limit from 1000×800 to 400×300
- 💾 **Real-time Window State Saving**: Implemented real-time saving mechanism for window size and position changes
- ⚙️ **Unified Settings Interface Optimization**: Improved GUI settings page configuration saving logic to avoid setting conflicts

### 🐛 Bug Fixes
- 🔧 **Window Size Constraint**: Fixed GUI window unable to resize to small dimensions issue
- 🛡️ **Setting Conflicts**: Fixed potential configuration conflicts during settings save operations

---

## [v2.2.0] - Layout & Settings UI Enhancements

### ✨ New Features
- 🎨 **Horizontal Layout Mode**: GUI & Web UI combined mode adds left-right layout option for summary and feedback

### 🚀 Improvements
- 🎨 **Improved Settings Interface**: Optimized the settings page for both GUI and Web UI
- ⌨️ **GUI Shortcut Enhancement**: Submit feedback shortcut now fully supports numeric keypad Enter key

### 🐛 Bug Fixes
- 🔧 **Image Duplication Fix**: Resolved Web UI image pasting duplication issue

---

## [v2.1.1] - Window Positioning Optimization

### ✨ New Features
- 🖥️ **Smart Window Positioning**: Added "Always show window at primary screen center" setting option
- 🌐 **Multi-Monitor Support**: Perfect solution for complex multi-monitor setups like T-shaped screen arrangements
- 💾 **Position Memory**: Auto-save and restore window position with intelligent visibility detection

---

## [v2.1.0] - Complete Refactored Version

### 🎨 Major Refactoring
- 🏗️ **Complete Refactoring**: GUI and Web UI adopt modular architecture
- 📁 **Centralized Management**: Reorganized folder structure, improved maintainability
- 🖥️ **Interface Optimization**: Modern design and improved user experience

### ✨ New Features
- 🍎 **macOS Interface Optimization**: Specialized improvements for macOS user experience
- ⚙️ **Feature Enhancement**: New settings options and auto-close page functionality
- ℹ️ **About Page**: Added about page with version info, project links, and acknowledgments

---

## [v2.0.14] - Shortcut & Image Feature Enhancement

### 🚀 Improvements
- ⌨️ **Enhanced Shortcuts**: Ctrl+Enter supports numeric keypad
- 🖼️ **Smart Image Pasting**: Ctrl+V directly pastes clipboard images

---

## [v2.0.9] - Multi-language Architecture Refactor

### 🔄 Refactoring
- 🌏 **Multi-language Architecture Refactor**: Support for dynamic loading
- 📁 **Modularized Language Files**: Modular organization of language files

---

## [v2.0.3] - Encoding Issues Fix

### 🐛 Critical Fixes
- 🛡️ **Complete Chinese Character Encoding Fix**: Resolved all Chinese display related issues
- 🔧 **JSON Parsing Error Fix**: Fixed data parsing errors

---

## [v2.0.0] - Web UI Support

### 🌟 Major Features
- ✅ **Added Web UI Support**: Support for remote environments
- ✅ **Auto Environment Detection**: Automatically choose appropriate interface
- ✅ **WebSocket Real-time Communication**: Real-time bidirectional communication

---

## Legend

| Icon | Meaning |
|------|---------|
| 🌟 | Version Highlights |
| ✨ | New Features |
| 🚀 | Improvements |
| 🐛 | Bug Fixes |
| 🔄 | Refactoring Changes |
| 🎨 | UI Optimization |
| ⚙️ | Settings Related |
| 🖥️ | Window Related |
| 🌐 | Multi-language/Network Related |
| 📁 | File Structure |
| ⌨️ | Shortcuts |
| 🖼️ | Image Features |
| 📝 | Prompt Management |
| ⏰ | Auto-Submit |
| 📊 | Session Management |
| 🔗 | Connection Monitoring |
| 🏗️ | Architecture Changes |
| 🛠️ | Technical Improvements |
| 📚 | Documentation Updates |

---

**Full Project Info:** [GitHub - mcp-feedback-enhanced](https://github.com/Minidoracat/mcp-feedback-enhanced)
