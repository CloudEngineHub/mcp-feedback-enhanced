# Security Policy

## Maintenance status

The project is actively maintained. The current scope is deliberately narrow so it stays
sustainable — the previous 14-month gap happened because the goal was "maintain every feature
for every client", which did not hold.

**In scope right now:**
- ✅ Security vulnerabilities
- ✅ Compatibility breaks that make the server unusable on install (dependency updates,
  upstream breaking changes)
- ✅ Regression tests guarding the above

**Component scope — desktop application (Tauri shell), since v2.8.0:**
- 🟡 Maintenance-only: security fixes and "cannot launch at all" compatibility fixes only;
  no new features (always-on-top, staying resident, keeping the window after submit).
  Scheduled for removal in v3; the release notes will name the last version that ships
  the desktop binaries. Details and migration options are in the README.

**Decided from community feedback** (see the pinned discussion):
- Which pre-existing defects to fix (timeouts, session history, per-client compatibility)
- Whether to move toward native MCP Elicitation / Apps to shrink the implementation

**Out of scope permanently:**
- ❌ Arbitrary command execution (removed in v2.6.1, will not return)
- ❌ Prompt patterns designed to force a callback on every step (they existed to save
  request quota, which no longer applies)

## Supported versions

| Version | Supported |
|---------|-----------|
| Latest 2.x release | ✅ Receives all fixes (security, compatibility, and the fixes in the "in scope" list) |
| Older 2.6.1+ releases | ⚠️ Free of the command-execution issue below, but fixes are **not** back-ported — pinning an old version (e.g. to keep desktop mode) means staying on its known issues |
| 2.6.0 and earlier | ❌ **Not supported — contains a known command execution issue (see below)** |

If you are on 2.6.0 or earlier, upgrade:

```bash
uvx mcp-feedback-enhanced@latest
```

## Issues fixed in v2.8.2

### Cross-site writes to HTTP `/api/*` endpoints and stored XSS in session details

Reported privately as `GHSA-x999-258q-h9mh`. Thanks to the reporter for the
detailed write-up.

**Affected:** all versions up to and including 2.8.1
**Fixed in:** 2.8.2
**Impact:** a malicious web page could overwrite the UI settings (including the
auto-submit prompt and timeout, so feedback is submitted automatically over the
legitimate WebSocket) and plant HTML that runs as script in the Web UI

The v2.6.1 Origin check only covered `/ws`. The state-changing HTTP endpoints
(`/api/save-settings`, `/api/save-session-history`, `/api/add-user-message`,
`/api/clear-settings`, `/api/log-level`) checked neither `Origin` nor
`Content-Type`, and `request.json()` parses the body whatever the declared type.
A cross-origin `POST` with `Content-Type: text/plain` is a CORS *simple request*:
the browser sends it without a preflight, so the page cannot read the response
but the write still happens. Two further problems made this worse:

1. The session details dialog interpolated `session_id`, `status`,
   `project_directory` and other history fields into HTML without escaping,
   so a tampered `session_history.json` became stored DOM XSS. The shared
   `escapeHtml` helper also left quotes unescaped, so values placed in
   attributes could break out.
2. When bound to `0.0.0.0` or `::`, `Origin` validation only compared the port,
   so any site served on the same port number passed — for `/ws` as well.

**Resolution:**

1. Every non-GET/HEAD/OPTIONS request to `/api/*` now goes through one middleware,
   so endpoints added later are covered too. An `Origin` that fails the same
   check as `/ws` gets **403**; a `Content-Type` other than `application/json`
   gets **415**. Requiring JSON forces a cross-origin request into a preflight,
   which the server never approves. Requests without an `Origin` header
   (non-browser clients) and desktop WebView origins are still allowed, as for `/ws`.
2. On a wildcard bind, the `Origin` host and port must now equal the request's
   `Host` header instead of matching on port alone. Loopback origins on the
   server's port are still allowed.
3. All session-history fields in the details dialog are escaped, and the shared
   `escapeHtml` now escapes `"` and `'`. Stored prompt and custom-sound IDs,
   which also come from the settings file, are escaped in the same way.

`tests/unit/test_cross_site_writes.py` replays the reported requests against every
write endpoint and checks the files are left untouched;
`tests/unit/test_websocket_origin.py` covers the wildcard-bind rule.

## Issues fixed in v2.6.1

### Unauthenticated command execution (issue [#219](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/219))

**Affected:** all versions up to and including 2.6.0
**Fixed in:** 2.6.1
**Impact:** arbitrary program execution in the project directory

Versions up to 2.6.0 accepted a `run_command` message over the WebSocket
endpoint `/ws` and passed it to `subprocess.Popen`. Three factors combined
to make this exploitable:

1. `/ws` had **no authentication** — it only checked whether an active session existed,
   and a new connection would take over the existing session's socket.
2. The safety check was a **blocklist of shell metacharacters** (`;`, `&&`, `||`, `|`,
   `>`, `<`, backtick, `$(`, `rm -rf`, …). Because execution used `shell=False`,
   metacharacters were never the risk — plain binaries such as `cat`, `curl`,
   `wget`, `python`, and `powershell` passed straight through.
3. The auto-command feature was **enabled by default** (`autoCommandEnabled: true`),
   so a configured command would fire automatically on new sessions and on
   feedback submission.

Default binding is `127.0.0.1`, which limits exposure to local processes.
However, older documentation recommended setting `MCP_WEB_HOST=0.0.0.0` for
SSH remote development, which turned this into a network-reachable issue.

**Resolution:** command execution was **removed entirely** rather than hardened.
A blocklist cannot safely permit arbitrary executables. The WebSocket handler,
session methods, frontend UI, and related settings are all gone, and
`tests/unit/test_no_command_execution.py` guards against reintroduction.

### Cross-Site WebSocket Hijacking (CSWSH)

Reported privately as `GHSA-cmr5-gpm3-79vf` (critical) and
`GHSA-2wx7-r4rh-f663` (high). Thanks to both reporters for the detailed
write-ups and working proofs of concept.

**Affected:** all versions up to and including 2.6.0
**Fixed in:** 2.6.1
**Impact:** in ≤2.6.0, arbitrary command execution triggered from a web page

Browsers are **not** restricted by the same-origin policy when opening a
WebSocket. A malicious page could therefore make the victim's browser connect
to `ws://127.0.0.1:<port>/ws` and send messages, because `/ws` accepted any
`Origin` and called `accept()` without validation. Combined with the
`run_command` handler above, this escalated to remote code execution — the
loopback binding did not help, since the browser itself is local.

**Resolution — two independent layers:**

1. Command execution was removed entirely (see above), so the escalation path is gone.
2. `/ws` now validates `Origin` **before** `accept()`. Only loopback origins on
   the server's own port, the bound host itself, and desktop WebView schemes are
   allowed. Requests without an `Origin` header (non-browser clients such as the
   desktop app) are still permitted, since a cross-origin page cannot suppress
   the header.

Cross-origin connection attempts are rejected with HTTP 403 before the handshake
completes. `tests/unit/test_websocket_origin.py` guards this, using the exact
origins from the reported proofs of concept.

## Remaining security considerations

These are **known and unfixed** properties of the current architecture. Treat this
tool as local, single-user development tooling:

- **No authentication on the Web UI or WebSocket.** Any *local process* that can
  reach the port can read session content (project path, AI summary, feedback
  history) and submit feedback on your behalf. Origin validation stops malicious
  *web pages*, but it cannot stop a local process — an `Origin` header is only
  enforced by browsers.
- **HTTP `/api/*` endpoints are unauthenticated.** Since v2.8.2, cross-origin pages
  can no longer *write* through them (state-changing requests need a trusted
  `Origin` and `Content-Type: application/json`), and they cannot read the
  responses (the same-origin policy applies to `fetch`). A local process can do both.
- **`MCP_WEB_HOST=0.0.0.0` is unsafe.** It exposes the above to anyone who can
  reach the port. Use SSH port forwarding instead.

Keep the default `127.0.0.1` binding and use SSH port forwarding for remote work.

## Reporting a vulnerability

Report privately via
[GitHub Security Advisories](https://github.com/Minidoracat/mcp-feedback-enhanced/security/advisories/new).

Please do not open a public issue for a vulnerability that is not already public.

Include where possible:

- affected version
- reproduction steps or a proof of concept
- impact assessment

Security reports are prioritised. For anything that cannot be fixed within the current
architecture, it will be documented here rather than silently left open — the
"no authentication on the Web UI" item above is an example of that.
