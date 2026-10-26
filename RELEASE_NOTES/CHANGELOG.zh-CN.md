# 更新日志 (简体中文)

本文件记录了 **MCP Feedback Enhanced** 的所有版本更新内容。

## [v2.8.5] - 未发布 - 统计面板、界面语言与繁中用语修正

### 🌟 版本亮点
- 详细统计面板的状态、会话数、今日平均时长、重连次数与连接时间反映实际情况；右上角的重连状态显示实际次数。
- `MCP_LANGUAGE` 现在真正决定网页界面语言（反馈页与等待页），界面切换只在当前页面有效；时间、日期、复制的会话内容，以及原本写死中文的界面文字，按界面语言显示，切换语言后立即生效。
- 繁体中文界面，以及后端回给界面与 AI 的繁体中文消息，改用台湾用语。
- 自动提交倒计时期间手动提交的反馈，不再被记成自动提交。
- 原生 Windows 设置了 `WSLENV` 时，不再被误判成 WSL 而改用 `cmd.exe` 打开浏览器。

### 🐛 问题修复
- **详细统计面板的「状态」永远是「等待中」、「会话」永远是 1**：两个字段原本从页面上已不存在的元素复制，一直停在默认值。现在「状态」跟随当前会话（提交反馈后变为已提交，新会话进来变回等待中），「会话」是会话历史列表的条数（含当前会话），切换语言时一起切换。
- **「今日平均时长」一直是 0，切换语言后单位也没变**：统计只看服务器返回的会话里没有的 duration 字段，数值不变时也不会重绘。现在与会话历史的持续时间使用同一个定义（创建时间到结束时间，没有结束时间时用提交反馈的时间），舍去方式也相同（只有一个会话时两边显示一致），切换语言后立即换成新语言的单位。
- **「重连」次数在恢复连接后归零、「连接时间」连接后停在 00:00**：「重连」现在是整页累计；「连接时间」连接期间每秒更新，断线时显示 --:--，重连后从新连接开始计算。
- **右上角连接状态显示「重连中... (第{attempt}次)」**：重连时没有代入次数，断线期间切换语言也会套上原字符串。现在显示「重连中... (第3次)」这类实际次数，每次断线重新计算，切换语言后同样代入。
- **时间与日期跟随浏览器语言**：英文界面也显示「下午9:51:30」。当前会话卡片、会话历史、「反馈已提交」的时间，以及提示词与自定义音效的日期，改为按界面语言格式化，切换语言后立即生效。
- **复制会话内容、复制用户内容写死简中**：现在按界面语言输出。复制会话内容的用户消息原本显示为 [object Object]，状态与创建时间是原始值；现在显示消息内容与状态文字，时间和复制用户内容一样改用会话详情窗口的 YYYY/MM/DD HH:MM:SS。
- **自动提交倒计时期间手动提交，被记成「自动提交」**：前端用「自动提交倒计时是否正在运行」判断提交方式，只要有提示词设为自动提交、倒计时开始后手动点击提交，会话历史、会话详情、导出文件与服务器记录的 `submission_method` 都是 `auto`。现在按实际触发来源记录：倒计时到期自动提交记 `auto`，点击提交按钮或 Ctrl+Enter 记 `manual`；连接尚未就绪、先暂存再提交的反馈也保留原来的方式。
- **图标按钮在套用翻译后变成文字**：提示词设置的自动提交按钮，⏰／⏸️ 图标被换成「设定为自动提交」等字样，提示也写死中文；会话卡片的「复制会话内容」「复制用户内容」按钮，📋／📝 图标连同文字一起被替换成纯文本，`aria-label` 写死中文，切换语言也不会变。现在图标保留，说明放在鼠标提示与屏幕阅读器标签，并按界面语言显示。
- **页面的 `<html lang>` 一直是 `zh-CN`**：两个模板写死 `lang="zh-CN"`，第一次打开页面时也不会更新，只有在界面上切换语言才会改；繁中或英文界面被声明为简中，屏幕阅读器与浏览器会用错误的语言朗读、断词与选择字体。现在模板默认 `zh-TW`（与前端默认语言一致），应用翻译时一并把 `lang` 设为当前界面语言，首次加载与切换语言都会更新。
- **`MCP_LANGUAGE` 现在真正决定网页界面语言**（[#189](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/189)）：v2.7.1 只调整了后端检测顺序，网页界面仍由 `ui_settings.json` 的 `language` 或浏览器语言决定，设置 `MCP_LANGUAGE=en`／`zh-CN` 后界面仍是繁中。现在服务器把指定语言带进反馈页与等待页（`<html lang>` 与 `data-forced-language`），第一次套用翻译就是指定语言。指定期间语言菜单仍可切换，但只在当前页面有效，刷新后回到指定语言；`ui_settings.json` 的 `language` 不会因切换、修改其他设置或重置而改变。
- **`MCP_LANGUAGE` 只接受 `zh-TW`、`zh-CN`、`en`**：去掉首尾空白后必须完全一致，`ja`、`EN`、`zh_TW` 等值一律视为未设置。原本错误处理的备用路径会直接返回未验证的值。
- **等待页（尚无会话时）支持三语**：等待说明原本写死为繁中，现在按 `MCP_LANGUAGE` → `ui_settings.json` 的 `language` → 浏览器语言 → 繁中的顺序显示。右上角的连接指示灯一并移除：等待页不建立 WebSocket，指示灯始终是红色「连接中...」；也不再加载只有反馈页用得到的脚本。
- **首次打开页面不再把浏览器语言写入 `ui_settings.json`**：只有在未设置 `MCP_LANGUAGE` 时用户切换语言才会保存。
- **界面上写死的中文**：会话详情窗口的「(进行中)」、「未知」、「内容」、「字符」、复制按钮与提示消息，自定义音效列表的「创建于／格式」与播放／删除按钮提示，以及提示词选择窗口的「最近使用」改用翻译；播放／删除两个图标按钮也加上屏幕阅读器标签。重置设定的确认框、测试通知失败的提示、自动提交暂停的原因与状态按钮的「秒」、自动提交时间的验证错误、图片移除按钮的提示与屏幕阅读器标签、提示词窗口的关闭按钮与空状态、音效名称输入窗口，以及新增或上传时提示词、音效名称重复等错误消息，也改用翻译。英文的自动提交暂停消息原本直接把原因接在 "Auto submit paused" 后面，现在是完整句子。
- **英文或简中界面下，空白的 AI 总结被存成界面文字**：AI 传来空白总结时，前端改读会话卡片上的「AI 总结: …」再用繁中字符串去掉标签；英文或简中界面比对失效，总结变成 "AI Summary: Loading..." 之类的文字，出现在会话卡片、历史、详情与导出。现在直接使用服务器的总结与项目目录，空白总结按界面语言显示「无总结」。
- **开着自动提交时切换语言，状态按钮显示成「已停用」**：按钮模板固定套用「已停用」的翻译，每次切换语言都会盖掉「已启用 (30秒)」。现在切换语言时按按钮当前的状态与秒数重绘，启用与停用都跟着界面语言。
- **英文或简中界面可以把自定义音效取成和默认音效相同的名称**：重名检查只比对繁中名称「經典提示音」等，英文界面取名 "Classic Beep" 不会被拦下，下拉菜单里出现两个同名音效。现在三种语言的默认音效名称都算重名。
- **部分消息显示 key 名称或未代入的参数**：补齐三个语言缺少的翻译（简中缺得最多，例如系统与错误消息、会话超时；英文缺会话超时与自动提交提示）。会话历史保存、套用提示词、通用错误三条消息的参数写成 {{count}}，与前端的 {count} 不符，console 会显示「会话历史已保存（{4} 个会话）」，现已修正。
- **繁体中文界面使用大陆用语**：繁体中文翻译文件、页面初始文字与翻译尚未加载时的备用文字，把大陆用语换成台湾用语，例如「用戶」改「使用者」、「剪貼板」改「剪貼簿」、「當前會話」改「目前會話」、「連接」改「連線」、「超時」改「逾時」、「數據」改「資料」、「保存」改「儲存」、「點擊」改「點選」、「重置設定」改「重設設定」、「提示詞模板」改「提示詞範本」、「本地儲存」改「本機儲存」；简体中文与英文界面不受影响。
- **后端回给界面与 AI 的繁体中文消息使用大陆用语**：会话状态消息（如「等待使用者回饋」「已送出回饋，等待下次 MCP 呼叫」「使用者設定的會話逾時」）、回给 AI 的反馈文字（「=== 使用者回饋 ===」「使用者取消了回饋。」「使用者未提供任何回饋內容。」「完整 Base64 長度: N 字元」）、等待超时原因与繁体中文错误消息（如「網路連線出現問題」「操作逾時」「資料驗證失敗」）改用台湾用语；错误消息的上下文前缀按界面语言区分，繁体中文为「檔案：」「技術細節：」，简体中文为「文件：」「技术细节：」（简体中文原本也会显示繁体的「技術細節：」），英文不变；只写入日志的消息不变。
- **关于页仍写着已在 v2.6.1 移除的「命令执行」**：描述改为当前的功能。
- **原生 Windows 设置了 `WSLENV` 时被误判成 WSL**：浏览器因此改用 `cmd.exe` 打开。现在 `is_wsl_environment()` 只在 Linux 上判断，`server.py` 重复的实现改用 `web/utils/browser.py` 的同一个函数。
- **`MCP_GZIP_LEVEL` 没有作用**：配置读到的压缩等级（默认 6）没有传给 GZip 中间件，响应一直用 Starlette 默认的 9 压缩。现在按设置的等级压缩，未设置时改用 6。
- **`make test-func` 一定失败**：它执行不带参数的 `test`，只会打印说明并以 exit 1 结束。现在改跑 `test --web`（使用项目的 .venv）。
- **Windows 上刚创建的临时文件清不掉**：刚创建的文件约有 1 成概率 mtime 比当前时间晚一点，计算出的年龄为负数，`cleanup_temp_files(max_age=0)`（程序结束时的全面清理）因此漏删。现在年龄不会小于 0。
- **导出的文件名日期少一天**：导出会话历史与单个会话时，文件名原本取 UTC 日期，北京时间 00:00–08:00 导出会少一天（例如本地 10/26 凌晨导出得到 `session-history-2026-10-25.json`）；现在改用本地日期。导出内容中的时间字段仍为 UTC ISO 格式。
- **导出单个会话后提示「会话历史已导出」**：容易误以为导出了全部历史；改为「会话已导出」，三个语言新增 `sessionHistory.management.exportSingleSuccess`。

### 📝 文档
- **架构文档与实现不符**：`docs/architecture/` 的部署指南与 API 参考写了不存在的 `web` 子命令、`--port`／`--session-retention` 等参数、`MCP_FEEDBACK_*` 环境变量、`config.json`、`/health` 端点，以及 `session_history` 等 WebSocket 消息，还说会话历史存在 localStorage。现在改成实际的子命令（`server`、`test --web/--desktop`、`version`）、实际读取的环境变量（`MCP_WEB_HOST`、`MCP_WEB_PORT` 等）、`~/.config/mcp-feedback-enhanced/` 下的 `ui_settings.json` 与 `session_history.json`，以及实际的 WebSocket 消息类型与前端方法签名（`getStats()`、无参数的 `exportSessionHistory()`）。架构文档也对照这一版的代码重新核对：移除已删除的类、方法与 `test --timeout` 参数，补上 `MCP_GZIP_LEVEL` 环境变量，开发工具段改写成当前的 pre-commit（Ruff v0.17.2）与 CI 的 Ruff、mypy 检查，引用的界面文字改成当前的繁中用语。
- **环境检测、交互流程与组件说明**：SSH 等远程检测只写进调试日志，不会自动建立 SSH 隧道；WSL 只在 Linux 判断并改用 Windows 浏览器打开。交互流程与组件说明改用实际的方法名与状态；重连与统计面板的说明改成当前行为（右上角重连次数每次断线重算、面板重连次数整页累计、平均时长与历史持续时间同一定义）。
- **系统架构总览**：改正为 Web UI 加 Tauri 桌面模式，架构图补上 Tauri 桌面壳并改成实际的模块连接（提示词、音效、输入框高度经设置 API 保存，不走 WebSocket）；「技术亮点」与「维护特性」移除程序没有的增量更新、状态回滚、日志轮转、健康检查与错误统计等说法；「性能」「安全性」「环境需求」删掉没有代码依据的数字与功能（例如「减少 60% 内存」「首屏 < 500ms」「SQL 注入防护」「CORS」），改写成实际行为；其余段落也对照实现改写：单一活跃会话的状态图改成实际的清理时机，「持久化 Web UI」改写成实际跨调用保留与不保留的内容（新会话会清空输入框与图片），删掉「地区特定的 UI 布局」「字体和排版优化」等没有实现的本地化说法。组件详细说明的「性能测试」改列实际有时间门槛的测试。另外移除已删除的 TabManager 与各文档结尾过期的版本标示，架构文档索引列出已在 2026-10-26 对照 main 代码核对过的段落与对照的 commit。
- **三语 README**：环境检测描述改成实际行为，`test` 示例补上 `--web`（不带参数只会打印说明），并注明 `MCP_WEB_PORT=0` 由系统分配端口；删除不存在的「总是在主屏幕中心显示窗口」设置问答。
- **`MCP_LANGUAGE` 与界面语言的说明**：三语 README 与 `docs/architecture/` 的部署指南、组件详细说明、交互流程文档、系统架构总览，把语言分成两条顺序：网页界面语言是 `MCP_LANGUAGE` → `ui_settings.json` 的 `language` → 浏览器语言 → 繁中，返回给 AI 的错误信息语言是 `MCP_LANGUAGE` → `LANG` 等环境变量 → 系统 locale → 繁中；注明只接受 `zh-TW`、`zh-CN`、`en`，其他值会被忽略，指定时界面切换只在当前页面有效、不保存，刷新后回到指定语言。配置文件表格删去 `language.json`，并更正「localStorage 保存界面语言」的说法（localStorage 只保存通知设置）。
- **繁体中文文档改用台湾用语**：README.zh-TW、`docs/architecture/` 全部架构文档（索引、系统架构总览、组件详细说明、交互流程、API 参考、部署指南）、繁体中文 Cache 管理与 SSH Remote 指南、桌面构建与 GitHub Actions 工作流程说明、发布说明管理文档与模板，叙述、图表，以及代码块里的中文注释与示例字符串，都改用台湾用语（例如使用者、资料、设定、逾时、呼叫、互动、智慧、侦测、通讯、连接埠、建置）；繁体中文的「交互流程文档」改名为「互動流程文件」。与源码或 workflow 逐字相同的代码行保持不变。
- **桌面构建指南故障排除示例对齐实际输出**：`docs/DESKTOP_BUILD.md` 的错误信息示例改为 `scripts/build_desktop.py` 实际打印的内容；修正 `make clean-desktop`（清理后会接着重新构建 Debug 版本）与 `make dev-setup`（安装开发依赖与 pre-commit hooks）的说明。

### 🧹 代码清理
- 删除 app.js 中没有调用者的会话更新与状态更新防抖包装，以及服务器从不发送的 feedback_received、desktop_close_request 消息处理（含测试数据里没有测试使用的 feedback_received fixture）。
- 删除 WebSocket 重连中处理「会话更新」关闭原因的分支（服务器从不发送该原因），以及没有调用方的连接统计重置函数。
- 删除从未启用的标签页管理模块 tab-manager.js（含调用已不存在路由的 /api/register-tab），以及只有它调用的 `Utils.generateId`。
- `test` 子命令删除 `--timeout`：这个参数从未被读取，`test --web`／`--desktop` 本来就持续运行到 Ctrl+C。之后再带 `--timeout` 会出现 `unrecognized arguments`。
- 删除没有调用者的后端代码：`SessionCleanupManager`、`CompressionMonitor`、`FeedbackResult`、`WebFeedbackSession.set_error`／`set_expired`、`server.py` 算完没用到的 `fastmcp_settings`（FastMCP 会自己读取 `FASTMCP_LOG_LEVEL`），以及 `main_routes.py` 的 `_delayed_server_stop`。
- 删除 `ResourceManager.register_process` 与随之失去作用的进程追踪（`unregister_process`、`cleanup_processes`、进程健康检查、`processes` 统计字段）：没有任何地方注册进程，追踪表永远是空的。
- 删除永远为空的全局标签页追踪状态（`WebUIManager.global_active_tabs`、`session.active_tabs`、`get_global_active_tabs_count`、`broadcast_to_active_tabs`）：TabManager 删除后没有任何东西会写入。
- 删除 `ErrorHandler` 的错误解决建议（`_ERROR_SOLUTIONS`、`get_error_solutions`、`get_i18n_error_solutions`）与 `create_error_response`：只有测试调用，正式流程不会显示。错误类型的用户消息改为直接取内置消息表：原本先查语言文件里不存在的 `errors.types.*`，每次都退回内置表；三种语言的输出不变。
- 删除 Python `I18nManager` 用不到的部分：旧格式 key 映射（`_get_legacy_translation`，例如 `btn_submit_feedback` → `buttons.submitFeedback`，没有任何代码传入旧格式 key，不少映射的新 key 也早已不存在）；`get_language_display_name` 与只被它使用的 `get_language_info`（查的 `languageNames.*`、`meta.displayName` 在三个语言都不存在）；没有调用者的 `reload_translations`、`add_language` 与模块级的 `reload_translations`。
- 删除命令执行功能移除后遗留的消息代码与翻译：后端 `MessageCodes.COMMAND_*` 与对应的旧 key 映射、前端 `MessageCodes.COMMAND`、备用消息表的 `error.command`，以及三个语言的 `commandStatus.*`、`error.command`、`errors.command_failed`、`notifications.command_executed`。后端 `MessageCodes` 另外删除从未发送过的 33 个常量，以及 `LEGACY_KEY_MAPPING` 中没有人传入的 5 个旧 key；后端实际发送给前端的 25 个代码不变。
- 删除没有任何页面加载的文件：前端 `static/js/modules/constants/message-codes.js`（`MessageCodes`、`createMessage` 等导出没有任何读取者），以及 `templates/components/status-indicator.html` 和只有它会用到的 `status.completed.message`（三个语言）。
- 删除 `utils.js` 走不到的备用消息表（`getFallbackMessage`）以及 `showMessage` 的消息代码对象分支：所有调用者都传入已翻译的字符串，没有人传 `{ code }` 对象；`i18nManager` 在 `i18n.js` 加载时就创建，翻译文件加载失败时它仍然存在，不会落到这张表。表里的 `settings.*` 也从来对不上后端实际发送的 `settingsAPI.*`。
- 删除每次都以 exit 1 结束的 `scripts/validate_message_codes.py`：它列出的缺漏都不会显示给用户（比对的是只在 i18n 未加载时才用到的前端备用消息表，缺翻译的代码也只随前端不显示的通知发送），Makefile 与 CI 也没有执行它。
- 删除三个语言中没有任何代码或模板使用的翻译 key（繁中 82 个、简中 77 个、英文 78 个），包括 `about.contact`、`summary.*`、`themes.*`、`autoRefresh.*`、`connection.*`、`notifications.*`、`errors.*` 等整段，以及只存在于单一语言的 `app.author`、`app.credits`、`autoSubmit.autoCommitNoPrompt` 等。删除前逐一确认没有动态拼接、`data-i18n` 属性或后端消息代码会用到。
- 函数内的 import 能移到文件开头的都移上去，刻意延迟的导入（循环导入、只在 Windows 存在的模块、运行时才加入 sys.path 的开发环境桌面模块等）保留并注明理由；未使用的解包变量改名。
- 后端不再读写 `~/.config/mcp-feedback-enhanced/language.json`：写入它的 `set_language()` 自 2025-06 起就没有调用者，文件只会残留旧值。后端错误消息的语言改为 `MCP_LANGUAGE` → `LANG`／`LC_ALL`／`LC_MESSAGES`／`LANGUAGE` → 系统语言 → 繁中；原本依赖该文件决定 AI 收到的错误消息语言的用户，会改为依据上述环境变量或系统语言，需要固定语言请设置 `MCP_LANGUAGE`。已有的 `language.json` 不会被删除，只是不再读取；启动时也不再创建 `~/.config/mcp-feedback-enhanced` 目录。
- 删除前端读取 localStorage `language` 的无效路径（全项目没有写入方）。
- 删除前端没有调用者的工具函数：`StatusUtils.formatStatusChangeLog`、`getStatusDescription`、`isValidStatusTransition` 与 `TimeUtils.formatRelativeTime`；其中几个还带着写死的繁中字符串。删除前以全仓库文本搜索确认没有调用或字符串引用。

### 🔧 其他变更
- `highlights.txt`、`release_body.md` 移出版本控制并加入 `.gitignore`：两者每次发布都由 publish.yml 重新生成，之前只是被发布 commit 的 `git add .` 一起带进来。
- 开发依赖从已弃用的 `[tool.uv] dev-dependencies` 迁移到 PEP 735 的 `[dependency-groups] dev`，`uv sync --dev` 不再输出弃用警告，安装的包不变。
- pre-commit 的 ruff 改用 v0.17.2（hook 名称随之改为 `ruff-check`），与 `uv run ruff`、CI 的结果一致。
- 开发依赖的 ruff、mypy 固定为 `ruff==0.17.2`、`mypy==2.4.0`：`uv.lock` 不纳入版本控制，CI 每次都重新解析版本，原本的 `>=` 会让 lint 工具发布新版时 CI 在代码没变的情况下失败，本地与 CI 的结果也可能不同。升级 ruff 时，`pyproject.toml` 与 `.pre-commit-config.yaml` 要一起改。
- Tests workflow 在 ubuntu 加上 `ruff check`、`ruff format --check` 与 `mypy`；原有的 mypy 错误已修正。

### ✅ 测试
- 桌面启动测试不再把整个进程的 `asyncio.sleep` 换成立即返回：之前会让前面测试留下的 uvicorn 服务器线程变成忙循环抢 GIL，CI 的 ubuntu job 偶尔因此超时 60 秒；现在只替换 `desktop_app` 模块自己的 `asyncio` 引用。
- `web_ui_manager` fixture 结束时停掉测试启动的 uvicorn 服务器：之前集成测试开的 8 个服务器线程都活到 pytest 结束。
- i18n 测试改用三个语言都存在的 key，并要求翻译结果不是 key 本身：原来的 `common.*`、`error.connection` 等 key 在语言文件里不存在，测试只因为找不到 key 时会返回 key 本身才通过。带参数的翻译改为测试 `error.generic` 的 `{error}` 被替换。
- 错误消息测试改为实际比对三种语言的内置消息、检查三个语言的文字各不相同，不再 mock 被测函数。
- 新增测试：`MCP_GZIP_LEVEL` 的等级 1 与 9 会传到 GZip 中间件，同一份 `styles.css` 压缩后的大小不同；后端以 `messageCode` 返回给前端显示的 16 个消息代码，三个语言都要有翻译；mtime 在未来的临时文件，`max_age=0` 仍会被清掉。
- MCP 集成测试改用当前的 Python 解释器启动服务器，不再通过 `uv run`：之前 `pyproject.toml` 有变动时，`uv run` 会先同步 `.venv` 并重写本地的 `uv.lock`；`.venv` 里的可执行文件被编辑器的语言服务器占用时同步失败，`test_mcp_workflow.py` 的 9 个测试随之失败。
- 新增路由测试：合法 `MCP_LANGUAGE` 时反馈页与等待页都带指定语言，不合法或未设置时不带；语言检测用例改为新顺序并加入不合法值；新增旧 `language.json` 不生效、不创建目录的测试。
- 删除只测上述死代码的测试。

---

## [v2.8.4] - 2026-10-25 - 会话历史保留与消息处理修正

### 🌟 版本亮点
- 重启 MCP 服务器后，会话历史保留之前的会话（#177）；上一个进程留下、没等到反馈的会话显示「已断线」。
- 会话历史的持续时间改用真实的创建与结束时间，保存期限也真的会清除过期记录。
- 英文界面的持续时间加上空格与单复数（`7 seconds`、`1 minute 5 seconds`）。
- 新会话通知不再被心跳响应覆盖，页面会切换到新会话。
- 切换语言后，当前会话卡片与会话历史立即换成新语言。

### 🐛 问题修复
- **会话历史只保存最近一次的记录（#177）**：历史列表原本只取 `/api/all-sessions`，那里只有当前服务器进程内存里的会话；重启 MCP 服务器后旧会话就看不到，下一次保存还会把 `session_history.json` 里的旧会话覆盖掉。现在会合并存档与当前会话，同一个会话以服务器数据为准、不重复，应用保存期限后再存回去。
- **重启服务器后，上一个进程留下的会话一直显示「等待中」**：合并存档后，服务器进程结束时还没收到反馈的会话会带着「等待中」留在历史里，直到保存期限到期，但它已经不会再收到反馈。现在加载历史时，只要当前会话列表读取成功，不在列表里且尚未结束的会话就标为「已断线」并存回去；已提交、已完成、超时、错误、已过期的会话不变，列表读取失败时不标记。
- **会话历史的「约 N 分钟」是估算值**：没有结束时间时，持续时间是用会话 ID 哈希算出的固定数字。现在只用会话的创建时间与结束时间（没有结束时间时用提交反馈的时间）计算，两者缺一就不显示。
- **英文界面的持续时间粘在一起**：数字、单位与各段之间没有空格，会话历史与「今日平均时长」显示成 `7seconds`、`1minutes5seconds`。现在英文在数字与单位、各段之间加空格，数量为 1 时用单数（`1 minute 5 seconds`）；中文保持 `7秒`、`1分钟5秒`。
- **会话历史保存期限不起作用**：时间戳有的是秒、有的是毫秒，比较时单位不一致，72 小时的期限实际上几乎不会过期。现在统一以秒比较，超过期限的记录会被清除。
- **新会话通知可能被心跳响应覆盖，页面停在旧会话**：前端把所有 WebSocket 消息放进同一个 50ms 防抖，50ms 内收到两条时只处理后一条；新会话的 `session_updated` 或 `status_update` 后面紧跟 `heartbeat_response`，前一条就被丢掉，页面不会切换到新会话。现在只有 `status_update`、`session_updated` 这两种完整快照的消息按类型各自防抖，同类连发仍只处理最后一条；`notification` 等其他类型直接处理，不同类型不再互相吞掉。
- **切换语言后当前会话卡片没有跟着切换**：「会话 ID／建立时间／项目／AI 总结」等前缀与历史的持续时间单位停留在原来的语言，要等状态变化或重新加载才更新。现在切换语言后立即换成新语言。

### ✅ 测试
- `conftest.py` —— 删除 session 级的 `event_loop` fixture：没有测试用到，pytest-asyncio 1.x 也不会拿它当事件循环。
- 开发依赖补上 `pytest-cov`：README 教的 `make test-cov` 之前会以 `unrecognized arguments: --cov=...` 失败（exit 4），现在 `uv sync --dev` 后就能跑出覆盖率表。
- 新增 `Tests` workflow：push 与 PR 到 main 时在 ubuntu-latest 与 windows-latest 跑完整 pytest；`test_resource_manager.py` 改用 `sys.executable` 启动子进程，不再依赖 PATH 上有没有 `python`。

---

## [v2.8.3] - 2026-10-25 - 提交后的会话状态与重复提交

### 🌟 版本亮点
- 提交反馈后，会话历史显示「反馈已提交」而不是「处理中」，下一次 MCP 调用到来后变为「已完成」。
- 会话管理页的「当前会话」卡片显示服务器上的实际状态，重新加载或点 🔄 都会更新。
- 刷新页面后不能再提交第二次反馈，不会再出现显示提交成功、内容却没送到 AI 的情况。

### 🐛 问题修复
- **提交反馈后会话停在 `active`**：v2.6.0（#78）在 `waiting` 与 `feedback_submitted` 之间插入了 `active`，但没有任何代码把会话推进到 `active`，提交时只走一步，便停在 `active`。会话因此一直显示「处理中」，下一次调用时旧会话不会变成 `completed`，提交后的清理计时器也不会重置。现在从 `waiting` 提交会经过 `active` 进入 `feedback_submitted`，仍遵守单向流转规则。
- **会话管理页的「当前会话」卡片停在默认值**：卡片只依赖前端记住的会话数据，重新加载后这份数据是空的，而服务器发来的 `feedback_submitted` 状态被当作「已完成」处理，只会更新已存在的数据，卡片便一直显示「等待中」、创建时间「--:--:--」、AI 摘要「加载中…」；右上角 🔄 只是等一秒，什么都没获取。现在卡片改用 `/api/all-sessions` 中标记为当前的会话：重新加载、点 🔄、提交反馈、下一个会话到来都会重新获取服务器数据。会话历史原本只在条数变化时重绘，提交后仍显示「等待中」，现在状态变化也会重绘。「反馈已提交」标签补上与「已完成」相同的绿色样式，切换语言时也会重新翻译。
- **刷新后还能再提交一次反馈，第二次的内容送不到 AI**：重新加载页面后，前端的反馈状态重置为「等待中」，提交按钮又能点；Ctrl+Enter 也只检查 WebSocket 是否已连接，不刷新也能重复提交。服务器收到后照单全收，覆盖了反馈内容并把会话推进到 `completed`，但 MCP 调用早已拿着第一次的反馈返回，第二次的内容没人读取，界面却显示提交成功。现在服务器收到过反馈后会忽略之后的提交，不改内容也不推进状态，并回复「反馈已提交，请等待下次 MCP 调用」；前端重新加载时按服务器状态显示「已提交」，按钮与 Ctrl+Enter 都会拦下。下一次 MCP 调用的新会话照常提交。

### ✅ 测试
- `conftest.py` —— 整个测试阶段把 `USERPROFILE`／`HOME` 指向 pytest 临时目录（子进程一并继承），测试前后确认 `Path.home()`、语言设置文件与 `feedback_session.TEMP_DIR` 都不在真实的主目录下，否则直接失败；运行测试不再写入用户自己的设置。
- `helpers/mcp_client.py` —— 启动 MCP 服务器前把 `smart_browser_open`／`webbrowser.open` 换成只记录网址的替身，不再打开真实的浏览器；子进程加上 `MCP_TEST_MODE=true` 与 `MCP_WEB_PORT=0`，改由系统分配端口，8765 被占用时不会再把用户正在使用的实例关掉。
- `test_resource_manager.py` —— 原本把 pytest 自己的 PID 登记进 `ResourceManager`，它在 `atexit` 中的清理会在 pytest 结束时终止这个进程，Windows 上即使全部通过也以 exit code 15 结束；改为登记 fixture 启动的短命子进程，每个测试后清空登记。
- `test_web_ui.py` —— 新增 `test_second_submission_is_ignored`：第二次提交不得覆盖反馈、图片与设置，也不得推进状态，只返回 `feedback.alreadySubmitted`。现有的 `test_session_feedback_submission` 断言提交后进入 `feedback_submitted`，修复前停在 `active` 而失败，现在通过。
- 删除三个测试已移除实现的过时测试：`test_i18n_with_web_ui_manager`（`WebUIManager.i18n` 已移除）、`test_session_lifecycle`（`update_status` 已换成单向的 `next_step`，创建与切换会话由 `test_web_ui.py` 覆盖）、`test_status_update_resets_timer`（测的是内部 Timer 对象是否换新）。
- `pytest.ini` 文件头从 `[tool:pytest]` 改为 `[pytest]`：原本整份配置都被忽略，现在 `testpaths`、strict markers／config、`asyncio_mode=auto`、`timeout=60`、`filterwarnings` 都会生效。
- `pyproject.toml` 的 `dev` extras 补上 `pytest-timeout>=2.1.0`，用 `pip install -e ".[dev]"` 安装后运行测试，不再因 `timeout` 配置报 `Unknown config option`。

---

## [v2.8.2] - 2026-10-25 - 挡下跨站写入 /api/*

### 🌟 版本亮点
- 跨站网页不能再通过 `/api/*` 改写设置、会话历史或日志级别，也就无法替用户开启自动提交。
- 会话详情弹窗的字段全部转义，被篡改的会话历史不会再被当成 HTML 执行。

### 🔒 安全修复
- **修复跨站写入 HTTP `/api/*` 与会话详情的 stored XSS**：私下报告的 `GHSA-x999-258q-h9mh`。v2.6.1 的 Origin 检查只覆盖 `/ws`；`/api/save-settings`、`/api/save-session-history`、`/api/add-user-message`、`/api/clear-settings`、`/api/log-level` 既不看 Origin 也不看 Content-Type，`request.json()` 又不管声明的类型照样解析。`Content-Type: text/plain` 的跨站 POST 是 CORS simple request，浏览器不做 preflight 直接发出：网页读不到响应，但写入会生效。攻击者可借此打开自动提交、换掉提示词，让合法的 WebSocket 连接自动发送反馈。
  - 所有访问 `/api/*` 的非 GET／HEAD／OPTIONS 请求改走同一个 middleware，之后新增的端点也自动受保护：Origin 没通过与 `/ws` 相同的检查返回 **403**；Content-Type 不是 `application/json` 返回 **415**，迫使跨站请求先 preflight，而服务器不批准任何 CORS。未带 Origin 的非浏览器客户端与桌面 WebView 来源照旧放行。
  - 绑定 `0.0.0.0` 或 `::` 时，Origin 的 host:port 必须等于请求的 Host header，不再只比较端口；旧版任何同端口的外站都能通过，`/ws` 也一样。
  - 会话详情弹窗原本直接把 `session_id`、`status`、`project_directory` 等字段插进 HTML，被篡改的 `session_history.json` 会变成 stored DOM XSS；现在全部转义。共用的 `escapeHtml` 原本不转义引号，放进属性的值可以逃逸出去，改为连 `"`、`'` 一起转义；同样来自设置文件的提示词 ID、自定义音效 ID 也一并转义。
  - 感谢报告者提供详尽的分析。

### ✅ 测试
- `test_cross_site_writes.py` —— 对每个写入端点重放报告中的跨站请求，确认返回 403／415 且文件不变；同源 JSON、桌面 WebView、未带 Origin 的请求照常成功；绑定 `0.0.0.0` 时 Origin 等于 Host 才放行，`/ws` 也走同一条规则。设置文件一律写在 `tmp_path`。
- `test_websocket_origin.py` —— 原本把「绑定 0.0.0.0 只比较端口」锁成预期的用例改为 Host header 比对，新增 `::`、IPv6、Host 缺失或格式错误的用例。

---

## [v2.8.1] - 2026-09-07 - 桌面回退的收尾修正

### 🌟 版本亮点
- stderr 提示改为受保护写入，且 `sys.stderr` 为 None 时绝不改写 stdout（MCP 协议通道）。
- 桌面壳只在非零退出时才算启动失败，用户自己关窗不再被降级成 Web；失败原因会打印给用户。

### 🐛 问题修复
- **降级提示改为受保护的 stderr 写入**：v2.8.0 新增的两处 `sys.stderr.write` 是 request path 上第一个未包 try/except 的 stderr 输出；宿主已关闭 stderr pipe（EPIPE）时会让整个 tool call 以异常结束，且 `MCP_DESKTOP_MODE` 来不及清掉、下次调用重演。改用与 `debug_log` 同样静默失败的 `user_notice`，并把桌面启动失败的原因（exit code、stderr 尾段）一并打印给用户——Defender 隔离、glibc、Gatekeeper 三者处置完全不同，没有原因就无法反馈。
- **只有非零退出才算启动失败**：v2.8.0 把观察期内任何退出都当失败，用户在窗口出现后两秒内自己关掉（exit 0）也会被降级成 Web、与 v2.7.2 的关窗收尾语义冲突。现在 exit 0 沿用既有语义。
- **`sys.stderr` 为 None 时不再改写 stdout**：`print(file=sys.stderr)` 在 pythonw 或宿主关闭 stderr 时会退回 `sys.stdout`——那是 MCP 协议通道，一行提示就足以让客户端解析失败。`debug_log` 与 `user_notice` 改共用 `_write_stderr`，先抓住 stream、None 即返回。
- **stderr 尾段读取加上限**：native 可能把 stderr 写端留给 WebView 等后代进程，`read()` 会等到它们全部关闭；改用 `communicate(timeout=1)`，超时只报 exit code。

### 🔧 其他变更
- README 三语：「安装为应用」段落的「每次调用仍会打开系统浏览器标签页」不符实际（标签页保持连接时会重用），改为「关掉应用窗口后下次调用会打开在普通浏览器标签页」；「随即退出」改为「随即出错退出」。

### ✅ 测试
- `test_desktop_fallback.py` —— stderr 断言改在 `MCP_DEBUG=false` 下执行（conftest 默认开 debug，原测试在退回只打印 debug log 时仍会通过）；早退测试改用临时目录的假 binary，不再依赖入库的真 binary；新增：后代握着 stderr 不卡住、exit 0 不算失败、两份 launcher 字节一致（`build_desktop.py` 复制曾让两份漂移）。
- `test_user_notice.py` —— `sys.stderr` 为 None 时 stdout 必须为空（`debug_log` 与 `user_notice` 皆测）、`user_notice` 不受 `MCP_DEBUG` 影响、stderr 已关闭时不抛出。

---

## [v2.8.0] - 2026-09-07 - 桌面应用程序进入仅维护状态

### 🌟 版本亮点
- 桌面应用程序（Tauri 壳）自本版起 **maintenance-only**：不再新增功能，只修安全问题与完全无法启动的兼容性问题，预计 v3 移除；binary 仍随本版发布，想继续使用请在 IDE 的 MCP 配置固定版本（见 README「桌面应用程序维护状态」）。
- 桌面壳启动不了时（被杀毒隔离、glibc 太旧、Gatekeeper 拦下、启动后随即退出）不再空等到超时：本 process 自动改走浏览器，并把网址打印到 stderr。

### 🐛 问题修复
- **桌面模式的浏览器回退从未生效**：`launch_desktop_app` 失败时调用的 `open_browser` 会因为同一个 `MCP_DESKTOP_MODE` 环境变量而直接跳过，用户面前什么都没有，只能等到 timeout 收到「用户未回应」。现在改在唯一的分流点处理：桌面启动失败 → 清掉本 process 的 `MCP_DESKTOP_MODE` → 走既有 `smart_open_browser`（含活跃标签页检测与会话更新通知），之后每次调用都直接走 Web，不会再试桌面、再开新标签页；重启 MCP 服务器会重新读 IDE 配置再试桌面。
- **native 启动后随即退出现在算启动失败**：两份 Python launcher 原本只 `Popen` 再等两秒，不看退出码，被 Defender 隔离或缺 glibc 时仍报告「启动成功」。现在观察期内退出即失败（附 exit code 与 stderr 尾段），交给上述回退。
- **浏览器也打不开时不再静默**：`webbrowser.open` 返回 False（例如无桌面环境的 SSH 主机）或 WSL 三种打开方式全失败时，无条件把网址打印到 stderr，让用户能手动打开；不再只在 `MCP_DEBUG=true` 时可见。

### 🔧 其他变更
- `build-desktop.yml` 的触发路径排除 `src-tauri/python/**`：纯 Python launcher 变更不再触发四平台 native 重建与 binary 提交。
- 两份 launcher（`src/mcp_feedback_enhanced/desktop_app/` 与 `src-tauri/python/`）同步为同一份；`build_desktop.py` 复制时不会再把发布版退回旧写法。
- README 三语新增「桌面应用程序维护状态」与迁移说明；SECURITY.md 新增桌面组件维护范围，支持版本表区分「最新 2.x」与「固定的旧版不回补修正」。
- 本版**不**改 Rust、不改 native binary、不改 `/ws` 的桌面 WebView Origin 白名单、不改 renovate 配置。

### ✅ 测试
- `test_desktop_fallback.py` —— 桌面模块缺失时真的把网址交给浏览器并离开桌面模式、第二次调用重用既有标签页而非重试桌面、桌面健康时完全不碰浏览器、native 随即退出视为失败、浏览器打不开时网址打印到 stderr。测试只拦最底层的 `webbrowser.open`，保留真实的桌面模式判断，修正前四项确认失败。

---

## [v2.7.2] - 2026-09-07 - 无人回应时明确收尾

### 🌟 版本亮点
- 等待超时或用户关闭界面时，工具改为返回明确的「用户未回应，请结束任务」指令，工具描述的使用规则同步允许在此情况停止调用，客户端不再把它当一般错误无限重试（#125）。
- 用户关掉反馈标签页／窗口后，75 秒内未重新连接即结束等待，不再空等到 timeout（默认 10 分钟）才回应（#162）。

### 🐛 问题修复
- **超时返回改为结束指令**（[#125](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/125)）：旧版把 `TimeoutError` 交给 `ErrorHandler`，返回给模型的是「操作超时／增加超时时间设置／稍后重试」——客户端照做就是再调用一次本工具，用户不在时形成死循环。现在超时（或下述的用户关闭界面）返回「用户未回应（原因）。请视为用户已离开：直接结束本次任务并输出最终总结，不要再次调用 interactive_feedback」，附英文对照；工具描述的 USAGE RULES 也把「用户未回应」列为可停止调用的条件，避免描述与返回互相矛盾。只有等待本身的 `TimeoutError` 走这条路——取得反馈之后的存档／图片处理若抛出 `TimeoutError`（含 `OSError` 的 ETIMEDOUT），仍视为错误，不会把已到手的反馈说成没回应。
- **关闭界面即结束等待**（[#162](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/162)）：旧版前端关闭时只清理本地资源，后端不知情，`wait_for_feedback` 一直等到 timeout。现在会话登记的 WebSocket 断开后启动 75 秒宽限计时器，期间重新连上（F5、短暂断线、另一个标签页）即取消，逾期未重连才视为用户关闭界面。75 秒的依据：后端只登记最新一条连接，旧标签页要等下一次应用层心跳（60 秒）才会被判定失效并重连，宽限必须大于「一次心跳周期 + 首次重连」，否则「开两个标签页、关掉后开的那个」会把还在的用户判成离开。这只保证正常网络下的路径；首次重连就失败而走完整个退避序列（1+2+4+8+16 秒 + jitter，再 31-36 秒）会超过宽限，视同断线收尾。提交反馈与放弃等待在同一把 lock 下线性化：`Timer.cancel()` 拦不住已开始的回调，故回调以身份比对作废；提交是原子写入，等待端读到反馈就是完整反馈（不会文字有了、图片还没处理完），反馈送达一律为准。从未有前端连上的情况（例如没开浏览器）维持原本的 timeout 行为。
- 前端「会话超时」通知（`user_timeout`）现在会先写明原因，返回给 AI 的文字不再是默认的「等待用户反馈」。

### ⚠️ 行为变更
- 任何超过 75 秒的 WebSocket 中断——笔记本休眠、浏览器丢弃后台标签页、SSH 转发断线——现在都会以「用户已关闭反馈界面」结束等待，而不是等到 timeout。这是刻意的取舍：关掉窗口却让 AI 空等十分钟，比偶尔提早收尾更常见也更恼人。

### ✅ 测试
- `test_feedback_timeout.py` —— 超时返回必含结束指令且不再建议重试；取得反馈后的 `TimeoutError` 不得被当成没回应；工具描述允许在没回应时停止；断线宽限：在宽限内（而非 timeout）结束等待、期间重连不结束、已有反馈时不启动、回调写入 TIMEOUT 后才送达的反馈仍为准、回调在提交写到一半时到期不得返回半套反馈；`/ws` 端点的接线（登记连接断开启动宽限、重连取消）以 `TestClient.websocket_connect` 覆盖。
- 以真实 MCP stdio round-trip 加 Chromium 验证：打开界面 → F5 → 仍在等待 → 关闭标签页 → 宽限到期后收到结束指令；无前端连接时超时同样收到结束指令。

---

## [v2.7.1] - 2026-09-06 - MCP_LANGUAGE 优先级与 Linux 桌面兼容性

### 🌟 版本亮点
- `MCP_LANGUAGE` 真正成为强制指定——不再被界面中先前保存的语言覆盖（#189）。
- Linux 桌面 binary 可在 Ubuntu 22.04 / Debian 12 以上运行（glibc 需求由 2.39 降至 2.34，#165）。

### 🐛 问题修复
- **`MCP_LANGUAGE` 改为最高优先**（[#189](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/189)）：README 把它描述为「强制指定界面语言」，但检测顺序却让界面中保存的语言排在它前面，设了 `MCP_LANGUAGE=zh-CN` 仍会显示繁中。顺序对调；设置环境变量后，界面中的语言选择只在当次会话生效。
- **Linux 桌面 binary 改在 ubuntu-22.04 构建**（[#165](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/165)）：原本在 ubuntu-latest 构建的文件需要 `GLIBC_2.39`，只能在 Ubuntu 24.04+ 运行；重建后最高需求降为 `GLIBC_2.34`。
- **修正桌面 binary 提交流程在单平台构建时失效**：`download-artifact` 只有单一 artifact 时不会创建子目录，原本靠目录名识别平台的复制步骤会报告 0/4 并跳过提交。改为以最终文件名上传与搜索。

### 🔧 其他变更
- 修正 renovate 配置警告（`vulnerabilityAlerts.prPriority` 不合法，改以 `isVulnerabilityAlert` packageRule 表达）。
- 依赖下限一次提高到 OSV 记录的最后漏洞修补版本（aiohttp 3.14.3、starlette 1.3.1、jinja2 3.1.6、tauri 2.11.1、tokio 1.44.2 等），实际锁定版本不变；renovate 改用 `rangeStrategy=widen`，范围内的更新不再逐个 patch 提高下限。

---

## [v2.7.0] - 2026-09-06 - 升级至 fastmcp 4 / mcp 2

### 🌟 版本亮点
- 升级至 fastmcp 4.x 与 MCP Python SDK 2.x；服务端对旧协议客户端保持兼容，工具与返回格式不变。
- 修正 `ResourceManager` 临时文件清理的边界条件，消除一个随机失败的测试。

### 🔧 其他变更
- **升级 `fastmcp` 至 4.x、`mcp` 至 2.x**（取代 renovate [#239](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/239)、[#240](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/240)）：mcp 1.x 与 fastmcp 3.x 已进入仅收安全修补的维护模式。fastmcp 4 依赖 `mcp>=2,<3`，两者必须一起升级 —— 只合并其中一个会让依赖无法解析、包装不起来（与 #213/#217/#221/#228 同类问题）。服务端代码只需把 `ImageContent` 的构造参数改为 mcp 2 的正式字段名 `mime_type`；wire 格式仍为 `mimeType`。以 stdio 实测 `list_tools`／`get_system_info`，旧协议（2024-11-05）客户端的集成测试全部通过。
- **修正 `ResourceManager.cleanup_temp_files` 的年龄边界**：`file_age > max_age` 改为 `>=`。`cleanup_all` 以 `max_age=0` 表示「清理所有文件」，但刚创建的文件在 Windows 时间精度下年龄恰为 0，会被漏掉。

### ✅ 测试
- `test_image_content.py` —— 不再绑定 mcp 1 的内部模块名与 snake_case 之前的 `model_dump()` 字段；改以 `type(...) is ImageContent` 与 `model_dump(by_alias=True)` 验证 wire 契约。

---

## [v2.6.2] - 2026-08-25 - timeout 钳制与工具返回契约

### 🐛 问题修复
- **钳制 `interactive_feedback` 的 timeout**（[#212](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/212)）：客户端有时会传入不合理的小值 —— 报告中 Cursor 传过 `timeout=1`，用户还没看清界面就「操作超时」。现在服务端会钳制到 60–86400 秒。选择钳制而非 pydantic 的 `ge`/`le` 验证，是因为验证失败会让整个 tool call 中断；对 human-in-the-loop 工具来说，以安全值继续比中断更有用。
- **修正 `wait_for_feedback` 的提前结束逻辑**：旧版对 `timeout <= 30` 使用 `max(timeout - 1, 5)`，在 `timeout=1` 时反而把等待「延长」到 5 秒，与提前结束、避免与 MCP 层超时竞争的本意相反。

### 🔧 其他变更
- **精确声明工具返回类型**（由裸 `list` 改为 `list[TextContent | ImageContent]`），与 [#234](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/234) 相关。模糊的 `list` 让 FastMCP 无法判断内容类型，只能生成 wrap-result 的 `outputSchema`（`{"result": {"type": "array"}}` 加上 `x-fastmcp-wrap-result`），并把 content blocks 额外包成 `structuredContent`。声明精确类型后 FastMCP 正确识别为 content blocks，该 schema 消失。
  - 这**不等于** #234 报告的违规已重现。实测 FastMCP 3.4.7 下，修复前后 `interactive_feedback` 与 `get_system_info` 的 `CallToolResult` 都含 schema 要求的 `content` 字段。完整调查说明留在该 issue。

### ✅ 测试
- `test_feedback_timeout.py` —— 钳制边界、坏类型容错、margin 不得延长等待
- `test_tool_contract.py` —— 守住返回注解，避免退回裸 `list`

---

## [v2.6.1] - 2026-08-25 - 安全修复与维护恢复

### 🌟 版本亮点
移除已知的命令执行风险，并修复让新安装完全无法使用的兼容性问题。项目恢复维护，目前范围聚焦在「安全 + 装了就坏的兼容性」。

### 🔒 安全修复
- **移除命令执行功能**（[#219](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/219)）：旧版可通过**未认证**的 WebSocket `/ws` 端点发送 `run_command` 消息并执行任意程序。原本的防护是 shell metacharacter blocklist，但因为使用 `shell=False`，metacharacter 本来就不是风险点——`cat`、`curl`、`wget`、`python`、`powershell` 等可直接执行。且自动执行命令功能**默认为启用**。
  - 此功能已**完整移除**（后端处理器、session 方法、前端 UI、设置项、i18n 文案），而非加强 blocklist。blocklist 无法安全地允许任意可执行文件。
  - 新增 `tests/unit/test_no_command_execution.py` 防止重新引入。
  - 影响版本：**2.6.0 及之前所有版本**。请升级。
- **修复 Cross-Site WebSocket Hijacking（CSWSH）**：私下报告的 `GHSA-cmr5-gpm3-79vf`（critical）与 `GHSA-2wx7-r4rh-f663`（high）。浏览器开启 WebSocket **不受 same-origin policy 限制**，因此恶意网页可让用户的浏览器连上 `ws://127.0.0.1:<port>/ws` 并发送消息 —— 旧版 `/ws` 接受任何 Origin 就直接 `accept()`，配合上述 `run_command` 可升级为远程代码执行；绑定 loopback 并不能防止这点，因为浏览器本身就在本机。
  - 修复采两层独立防御：(1) 命令执行已完全移除，升级路径消失；(2) `/ws` 在 `accept()` **之前**验证 Origin，仅允许本服务端口上的 loopback 来源、绑定主机自身、以及桌面 WebView scheme；未带 Origin 的非浏览器客户端（如桌面应用）仍放行，因为跨站页面无法移除该 header。
  - 跨站连接在握手完成前即以 HTTP 403 拒绝。`tests/unit/test_websocket_origin.py` 使用报告者 PoC 中的实际来源作为测试用例。
  - 感谢两位报告者提供详尽分析与可运行的 PoC。

### 🐛 问题修复
- **修复 Web UI 直接返回 500**（[#213](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/213)、[#217](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/217)、[#221](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/221)、[#228](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/228)）：新版 Starlette 变更 `TemplateResponse` 签名，旧调用方式会抛出 `TypeError: unhashable type: 'dict'`，导致以 `uvx @latest` 安装的用户完全无法打开页面。感谢 [#220](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/220)（[#214](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/214)、[#215](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/215)、[#216](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/216) 亦报告同一问题）。
- **修复 `session_id` 未带入 template**：`feedback.html` 需要它初始化前端，但 context 从未提供。
- **修复图片序列化错误**（[#154](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/154)、[#168](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/168)、[#180](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/180) 等）：改用标准 `mcp.types.ImageContent`。旧实现返回 `fastmcp.utilities.types.Image`，在 FastMCP 3.x 会失败于 `Output validation error: outputSchema defined but no structured output returned`。已用真实 MCP round-trip 验证 PNG/JPEG/GIF/WebP。感谢 [#171](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/171)。

### 🔧 其他变更
- **依赖加上版本上限**：避免上游破坏性变更再次让安装失效。`starlette` 改为显式直接依赖。
- **文档修正**：移除「大幅节省平台成本」宣称（Cursor 已改为 token 计费，前提不成立）；`MCP_WEB_HOST=0.0.0.0` 不再作为推荐方案，改标示安全警告并建议 SSH 端口转发。
- 新增 [SECURITY.md](../SECURITY.md)：维护范围、已知风险、报告渠道。

### ⚠️ 已知未修问题
以下为既有限制，不在目前的维护范围内：
- Web UI 与 WebSocket **无认证机制**、无 Origin 验证
- 会话状态流转、i18n 环境检测、cleanup timer 相关的既有测试失败

---

## [v2.6.0] - 2025-06-28 - 智能会话管理与自动化功能强化

### 🌟 版本亮点
大幅强化会话管理功能，新增自动执行命令、导出功能和通知系统，提供更智能的开发体验。

### ✨ 新功能
- 🚀 **自动执行命令**: 新建会话和提交后可自动执行预设命令
- 📊 **会话导出功能**: 支持将会话记录导出为多种格式
- ⏸️ **自动提交控制**: 新增暂停和开始按钮，让用户更好控制自动提交时机
- 🔔 **系统通知**: 新增系统级通知功能，重要事件即时提醒

### 🚀 改进功能
- ⏱️ **会话超时机制优化**: 重新设计会话管理，提供更弹性的设置选项
- 🌏 **多语系强化**: 重构多语系架构，通知系统也完整支持多语言
- 🎨 **界面简化**: 大幅简化用户界面，提升使用体验

### 🐛 问题修复
- 修复命令执行功能的相关问题
- 修正 WebSocket 状态检测的导入错误
- 完善会话历史的多语言支持

---

## [v2.5.6] - 2025-06-21 - 设置保存机制优化与界面美化

### 🌟 版本亮点
重构设置保存机制，解决语系切换保存问题，并为设置界面增加可视化图标，提升用户体验。

### 🚀 改进功能
- 🔨 **设置保存机制重构**: 完全移除 localStorage 依赖，改用统一的 FastAPI 后端保存机制
  - 解决语系切换时设置无法正确保存的问题
  - 移除防抖机制，确保设置即时保存
  - 提升设置保存的可靠性和一致性
- ✨ **设置界面美化**: 为设置页签内的各功能区块新增对应图标
  - 提升界面视觉效果和用户体验
  - 更直观的功能识别

### 🛠️ 技术改进
- 📊 **统一存储架构**: 所有设置统一使用 JSON 文件存储，确保跨环境一致性
- 🔧 **代码简化**: 移除复杂的 localStorage 相关代码，降低维护成本

---

## [v2.5.5] - 2025-06-21 - SSH 远程开发支持与稳定性增强

### 🌟 版本亮点
新增 SSH 远程开发环境支持，解决远程开发时无法访问 Web UI 的问题。同时改进 macOS 编译支持和桌面应用稳定性，提升开发者体验。

### ✨ 新功能
- 🌐 **SSH 远程开发支持**: 新增 `MCP_WEB_HOST` 环境变量，支持设置 Web 服务器主机绑定
  - 默认为 `127.0.0.1` 确保安全性
  - 可设置为 `0.0.0.0` 允许远程访问
  - 解决 Cursor SSH Remote 等远程开发环境的访问问题
- 🍎 **macOS 编译支持增强**: 新增 `.cargo/config.toml` 配置文件
  - 支持 Intel (x86_64) 和 Apple Silicon (aarch64) 架构
  - 解决 macOS 上 PyO3 undefined dynamic_lookup 编译问题
  - 遵循 PyO3 官方推荐的最佳实践

### 🚀 改进功能
- 📝 **工具文档优化**: 将 LLM 指令移至工具 docstring，提升 token 效率
- 🎨 **用户配置简化**: 移除复杂的 Cursor 规则配置
- 📊 **AI 工作摘要 Markdown 增强**: 改进 Markdown 渲染效果和兼容性
- 🔄 **会话历史流程优化**: 改进会话保存和管理机制

### 🐛 问题修复
- 🖥️ **桌面应用 MCP 协议修复**: 修正桌面模式下 MCP 协议通信污染问题
- 📦 **打包流程修复**: 修正多平台桌面应用打包和发布问题
- 🔧 **发布流程优化**: 改进自动化发布工作流程的稳定性
- 🔥 **移除 ESC 快捷键**: 移除可能造成意外关闭的 ESC 快捷键功能

### 🛠️ 技术改进
- 🏗️ **构建系统增强**: 改进跨平台编译配置和依赖管理
- 📚 **文档自动化**: 改进工具自我文档化，遵循 FastMCP 最佳实践
- 🔍 **调试功能增强**: 新增更详细的调试信息和错误处理

### 📋 使用说明
- **SSH 远程开发**: 在 MCP 配置中设置 `"MCP_WEB_HOST": "0.0.0.0"` 允许远程访问
- **本地开发**: 保持默认 `"MCP_WEB_HOST": "127.0.0.1"` 确保安全性
- **macOS 开发**: 新的编译配置将自动生效，无需额外设置

---

## [v2.5.0] - 2025-06-15 - 桌面应用程序与性能优化

### 🌟 版本亮点
全新推出跨平台桌面应用程序，支持 Windows、macOS、Linux 三大平台。同时大幅提升系统性能与稳定性，引入防抖/节流机制优化用户体验。

### ✨ 新功能
- 🖥️ **桌面应用程序**: 基于 Tauri 框架的原生桌面应用，支持 Windows x64、macOS (Intel/Apple Silicon)、Linux x64
- 📊 **会话历史本地文件存储**: 会话记录从 localStorage 改为服务器端本地文件保存，支持跨环境数据一致性
- 🔧 **多平台构建支持**: 完整的 CI/CD 流程，支持自动化多平台桌面应用构建
- 📝 **桌面模式配置**: 新增 `MCP_DESKTOP_MODE` 环境变量，支持桌面/Web 模式切换
- 📋 **AI 工作摘要 Markdown 显示**: 支持 Markdown 语法渲染，包含标题、粗体、代码区块、列表、链接等格式

### 🚀 改进功能
- ⚡ **性能大幅提升**: 引入防抖/节流机制，减少不必要的渲染和网络请求
- 🌐 **网络连接稳定性**: 改进 WebSocket 重连机制，支持网络状态检测和智能重连
- 📊 **会话历史存储改进**: 从 localStorage 改为服务器端本地文件存储，提升跨环境一致性
- 🎨 **UI 渲染优化**: 优化会话管理、统计信息、状态指示器的渲染性能
- 📱 **响应式改进**: 调整心跳频率和超时阈值，减少系统负载
- 🔄 **模块化增强**: JavaScript 模块结构优化，支持更好的日志管理

### 🐛 问题修复
- 🌐 **网络重连改进**: 优化重连算法，采用指数退避策略和随机抖动
- 🖥️ **桌面模式适配**: 修复桌面模式下浏览器自动开启的问题
- 📊 **渲染性能修复**: 解决重复渲染和不必要的状态更新问题

### 🛠️ 技术改进
- 🏗️ **构建流程优化**: 新增 Makefile 桌面应用构建命令，支持 debug/release 模式
- 📦 **依赖管理**: 整合 Rust 工具链，支持跨平台编译和打包
- 🔍 **开发工具增强**: 新增环境检查、构建验证、清理工具
- 📚 **文档完善**: 新增桌面应用构建指南和工作流程说明
- 🔒 **安全性增强**: 引入 DOMPurify 进行 XSS 防护，确保内容安全

### 📋 使用说明
- **桌面模式**: 在 MCP 配置中设定 `"MCP_DESKTOP_MODE": "true"` (参考 `examples/mcp-config-desktop.json`)
- **Web 模式**: 在 MCP 配置中设定 `"MCP_DESKTOP_MODE": "false"` (默认，参考 `examples/mcp-config-web.json`)
- **测试桌面模式**: `uvx mcp-feedback-enhanced@latest test --desktop`
- **构建桌面应用**: `make build-desktop-release`

---

## [v2.4.3] - 2025-06-14 - 会话管理重构与音效通知

### 🌟 版本亮点
将会话管理从左侧边栏迁移到独立页签，解决浏览器兼容性问题。新增音效通知系统，支持自定义音效。

### ✨ 新功能
- 🔊 **音效通知系统**: 会话更新时播放音效提醒，支持内建音效和自定义音效上传
- 📚 **会话历史管理**: 本地保存会话记录，支持导出和清理功能
- 💾 **输入框高度记忆**: 自动保存和恢复文字输入框的高度设定
- 📋 **一键复制**: 项目路径和会话ID支持点击复制

### 🚀 改进功能
- 📋 **会话管理重构**: 从左侧边栏迁移到"会话管理"页签，解决小窗口下按钮无法点击的问题
- 🎨 **界面布局优化**: AI摘要区域自动扩展，提交按钮位置调整，移除多余描述文字
- 🌐 **多语言增强**: 新增tooltip和按钮的多语言支持

### 🐛 问题修复
- 修复当前会话详细信息按钮无反应问题
- 修复会话详情弹窗关闭延迟问题
- 修复音效通知语系初始化问题
- 修正自动提交处理逻辑

---

## [v2.4.2] - Web-Only 架构重构与智能功能增强

### 🌟 版本亮点
本版本进行了重大架构重构，**完全移除 PyQt6 GUI 依赖**，转为纯 Web UI 架构，大幅简化部署和维护。同时新增多项智能功能，包括提示词管理、自动提交、会话管理等，全面提升用户体验和工作效率。

### 🔄 重大架构变更
- 🏗️ **完全移除 PyQt6 GUI**: 彻底移除桌面应用程序依赖，简化安装和部署流程
- 🌐 **纯 Web UI 架构**: 统一使用 Web 界面，支持所有平台和环境
- 📦 **依赖大幅简化**: 移除 PyQt6、相关 GUI 库等重型依赖，安装包体积显著减小
- 🚀 **部署更简单**: 无需考虑 GUI 环境配置，适用于所有开发环境

### ✨ 全新功能
- 📝 **智能提示词管理系统**:
  - 常用提示词的 CRUD 操作（新增、编辑、删除、使用）
  - 使用频率统计和智能排序
  - 快速选择和一键应用功能
  - 支持自动提交标记和优先显示
- ⏰ **自动定时提交功能**:
  - 可设定 1-86400 秒的倒数计时器
  - 可视化倒数显示和状态指示
  - 与提示词管理系统深度整合
  - 支持暂停、恢复、取消操作
- 📊 **会话管理与追踪**:
  - 当前会话状态即时显示
  - 会话历史记录和统计分析
  - 今日会话数量和平均时长统计
  - 会话详情查看和管理功能
- 🔗 **连接监控系统**:
  - WebSocket 连接状态即时监控
  - 延迟测量和连接品质指示
  - 自动重连机制和错误处理
  - 详细的连接统计信息
- ⌨️ **快捷键增强**: 新增 Ctrl+I 快速聚焦输入框功能 (感谢 @penn201500)

### 🚀 功能改进
- 🎨 **UI/UX 全面优化**:
  - 新增左侧会话管理面板，支持收合/展开
  - 顶部连接状态栏，即时显示系统状态
  - 响应式设计，适配不同屏幕尺寸
  - 统一的设计语言和视觉风格
- 🌐 **多语言系统增强**:
  - 优化语言切换机制，支持即时切换
  - 新增大量翻译文本，提升本地化覆盖率
  - 改进语言选择器 UI，使用下拉菜单设计
  - 修复语言切换时的显示问题
- 🖼️ **图片设置整合**:
  - 将图片设置从工作区移至设置标签页
  - 统一的设置管理界面
  - 改进设置项目的组织和布局
- 📱 **界面布局优化**:
  - 调整版面配置，符合多语言显示需求
  - 优化按钮样式和间距
  - 改进表单元素的视觉设计
  - 增强可访问性和易用性

### 🐛 问题修复
- 🔧 **会话管理修复**:
  - 修复会话统计信息无法正确更新的问题
  - 修复会话数量计算错误
  - 改进会话状态追踪机制
- 🎯 **提示词功能修复**:
  - 修复常用提示词管理无法正确设置自动提交的问题
  - 改进提示词选择和应用逻辑
- 🌐 **语系切换修复**:
  - 修复语言切换时部分文字未更新的问题
  - 改进多语言文本的加载机制
- 🏗️ **架构稳定性修复**:
  - 修复会话管理初始化问题
  - 改进错误处理和资源清理
  - 优化模块加载顺序和依赖关系

### 🛠️ 技术改进
- 📦 **模块化架构**:
  - JavaScript 代码完全模块化重构
  - 采用 ES6+ 语法和现代化开发模式
  - 清晰的模块分离和职责划分
- 📊 **性能提升**:
  - 优化 WebSocket 通信效率
  - 改进前端资源加载速度
  - 减少内存使用和 CPU 负载

### 📚 文档更新
- 📖 **架构文档更新**: 更新系统架构说明，反映 Web-Only 设计
- 🔧 **安装指南简化**: 移除 GUI 相关安装步骤和依赖说明
- 🖼️ **截图更新**: 更新所有界面截图，展示新的 Web UI 设计
- 📋 **API 文档增强**: 新增提示词管理、自动提交等新功能的 API 说明

---

## [v2.3.0] - 系统稳定性与资源管理增强

### 🌟 亮点
本版本专注于提升系统稳定性和使用体验，特别解决了 Cursor SSH Remote 环境下无法启动浏览器的问题。

### ✨ 新功能
- 🌐 **SSH Remote 环境支持**: 解决 Cursor SSH Remote 无法启动浏览器的问题，提供清晰的使用指引
- 🛡️ **错误提示改善**: 当发生错误时，提供更友善的错误信息和解决建议
- 🧹 **自动清理功能**: 自动清理临时文件和过期会话，保持系统整洁
- 📊 **内存监控**: 监控内存使用情况，防止系统资源不足

### 🚀 改进功能
- 💾 **资源管理优化**: 更好地管理系统资源，提升运行效率
- 🔧 **错误处理增强**: 遇到问题时提供更清楚的说明和解决方案
- 🌐 **连接稳定性**: 改善 Web UI 的连接稳定性
- 🖼️ **图片上传优化**: 改善图片上传功能的稳定性
- 🎯 **自动聚焦输入框**: 反馈窗口开启时自动聚焦到输入框，提升用户体验 (感谢 @penn201500)

### 🐛 问题修复
- 🌐 **连接问题**: 修复 WebSocket 连接的相关问题
- 🔄 **会话管理**: 修复会话状态跟踪的问题
- 🖼️ **图片处理**: 修复图片上传时的事件处理问题

---

## [v2.2.5] - WSL 环境支持与跨平台增强

### ✨ 新功能
- 🐧 **WSL 环境检测**: 自动识别 WSL 环境，提供专门的支持逻辑
- 🌐 **智能浏览器启动**: WSL 环境下自动调用 Windows 浏览器，支持多种启动方式
- 🔧 **跨平台测试增强**: 测试功能整合 WSL 检测，提升测试覆盖率

### 🚀 改进功能
- 🎯 **环境检测优化**: 改进远程环境检测逻辑，WSL 不再被误判为远程环境
- 📊 **系统信息增强**: 系统信息工具新增 WSL 环境状态显示
- 🧪 **测试体验提升**: 测试模式下自动尝试启动浏览器，提供更好的测试体验

---

## [v2.2.4] - GUI 体验优化与问题修复

### 🐛 问题修复
- 🖼️ **图片重复粘贴修复**: 解决 GUI 界面中使用 Ctrl+V 复制粘贴图片时出现重复粘贴的问题
- 🌐 **语系切换修复**: 修复图片设定区域在语言切换时文字没有正确翻译的问题
- 📝 **字体可读性改善**: 调整图片设定区域的字体大小，提升文字可读性

---

## [v2.2.3] - 超时控制与图片设置增强

### ✨ 新功能
- ⏰ **用户超时控制**: 新增可自定义的超时设置功能，支持 30 秒至 2 小时的弹性设置
- ⏱️ **倒数计时器**: 界面顶部显示实时倒数计时器，提供可视化的时间提醒
- 🖼️ **图片大小限制**: 新增图片上传大小限制设置（无限制/1MB/3MB/5MB）
- 🔧 **Base64 兼容模式**: 新增 Base64 详细模式，提升部分 AI 模型的图片识别兼容性
- 🧹 **UV Cache 管理工具**: 新增 `cleanup_cache.py` 脚本，协助管理和清理 UV cache 空间

### 🚀 改进功能
- 📚 **文档结构优化**: 重新整理文档目录结构，将图片移至 `docs/{语言}/images/` 路径
- 📖 **Cache 管理指南**: 新增详细的 UV Cache 管理指南，包含自动化清理方案
- 🎯 **智能兼容性提示**: 当图片上传失败时自动显示 Base64 兼容模式建议

### 🐛 问题修复
- 🛡️ **超时处理优化**: 改进用户自定义超时与 MCP 系统超时的协调机制
- 🖥️ **界面自动关闭**: 修复超时后界面自动关闭和资源清理逻辑
- 📱 **响应式布局**: 优化超时控制组件在小屏幕设备上的显示效果

---

## [v2.2.2] - 超时自动清理修复

### 🐛 问题修复
- 🔄 **超时自动清理**: 修复 GUI/Web UI 在 MCP session timeout (默认 600 秒) 后没有自动关闭的问题
- 🛡️ **资源管理优化**: 改进超时处理机制，确保在超时时正确清理和关闭所有 UI 资源
- ⚡ **超时检测增强**: 加强超时检测逻辑，确保在各种情况下都能正确处理超时事件

---

## [v2.2.1] - 窗口优化与统一设置接口

### 🚀 改进功能
- 🖥️ **窗口大小限制解除**: 解除 GUI 主窗口最小大小限制，从 1000×800 降至 400×300
- 💾 **窗口状态实时保存**: 实现窗口大小与位置的即时保存机制，支持防抖延迟
- ⚙️ **统一设置接口优化**: 改进 GUI 设置版面的配置保存逻辑，避免设置冲突

### 🐛 问题修复
- 🔧 **窗口大小限制**: 解决 GUI 窗口无法调整至小尺寸的问题
- 🛡️ **设置冲突**: 修复设置保存时可能出现的配置冲突问题

---

## [v2.2.0] - 布局与设置界面优化

### ✨ 新功能
- 🎨 **水平布局模式**: GUI 与 Web UI 的合并模式新增摘要与反馈的左右布局选项

### 🚀 改进功能
- 🎨 **设置界面改进**: 优化了 GUI 与 Web UI 的设置页面，提升布局清晰度
- ⌨️ **快捷键完善**: 提交反馈快捷键现已完整支持数字键盘的 Enter 键

### 🐛 问题修复
- 🔧 **图片重复粘贴**: 解决了在 Web UI 文字输入区使用 Ctrl+V 粘贴图片时的重复问题

---

## [v2.1.1] - 窗口定位优化

### ✨ 新功能
- 🖥️ **智能窗口定位**: 新增「总是在主屏幕中心显示窗口」设置选项
- 🌐 **多屏幕支持**: 完美解决 T 字型屏幕排列等复杂多屏幕环境的窗口定位问题
- 💾 **位置记忆**: 自动保存和恢复窗口位置，智能检测窗口可见性

---

## [v2.1.0] - 全面重构版

### 🎨 重大重构
- 🏗️ **全面重构**: GUI 和 Web UI 采用模块化架构
- 📁 **集中管理**: 重新组织文件夹结构，提升维护性
- 🖥️ **界面优化**: 现代化设计和改进的用户体验

### ✨ 新功能
- 🍎 **macOS 界面优化**: 针对 macOS 用户体验进行专项改进
- ⚙️ **功能增强**: 新增设置选项和自动关闭页面功能
- ℹ️ **关于页面**: 新增关于页面，包含版本信息、项目链接和致谢内容

---

## [v2.0.14] - 快捷键与图片功能增强

### 🚀 改进功能
- ⌨️ **增强快捷键**: Ctrl+Enter 支持数字键盘
- 🖼️ **智能图片粘贴**: Ctrl+V 直接粘贴剪贴板图片

---

## [v2.0.9] - 多语言架构重构

### 🔄 重构
- 🌏 **多语言架构重构**: 支持动态载入
- 📁 **语言文件模块化**: 模块化组织语言文件

---

## [v2.0.3] - 编码问题修复

### 🐛 重要修复
- 🛡️ **完全修复中文字符编码问题**: 解决所有中文显示相关问题
- 🔧 **解决 JSON 解析错误**: 修复数据解析错误

---

## [v2.0.0] - Web UI 支持

### 🌟 重大功能
- ✅ **新增 Web UI 支持**: 支持远程环境使用
- ✅ **自动环境检测**: 自动选择合适的界面
- ✅ **WebSocket 即时通讯**: 实现即时双向通讯

---

## 图例说明

| 图标 | 意义 |
|------|------|
| 🌟 | 版本亮点 |
| ✨ | 新功能 |
| 🚀 | 改进功能 |
| 🐛 | 问题修复 |
| 🔄 | 重构变更 |
| 🎨 | 界面优化 |
| ⚙️ | 设置相关 |
| 🖥️ | 窗口相关 |
| 🌐 | 多语言/网络相关 |
| 📁 | 文件结构 |
| ⌨️ | 快捷键 |
| 🖼️ | 图片功能 |
| 📝 | 提示词管理 |
| ⏰ | 自动提交 |
| 📊 | 会话管理 |
| 🔗 | 连接监控 |
| 🏗️ | 架构变更 |
| 🛠️ | 技术改进 |
| 📚 | 文档更新 |

---

**完整项目信息：** [GitHub - mcp-feedback-enhanced](https://github.com/Minidoracat/mcp-feedback-enhanced)
