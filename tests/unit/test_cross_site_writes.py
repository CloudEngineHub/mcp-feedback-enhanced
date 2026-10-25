#!/usr/bin/env python3
"""
跨站寫入 /api/* 的回歸測試（GHSA-x999-258q-h9mh）

瀏覽器對 Content-Type 為 text/plain 的 POST 不做 preflight，跨站網頁因此能直接
打本機的 /api/save-settings 等端點：讀不到回應，但寫入會生效。攻擊者可藉此覆寫
ui_settings.json（開啟自動提交）或在 session_history.json 埋入 stored XSS。

這些測試守住伺服器端的檢查：跨站來源回 403、非 JSON 回 415，且檔案不被改動。
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


SETTINGS = {"language": "zh-TW", "autoSubmitEnabled": False}
HISTORY = {"version": "1.0", "sessions": [], "lastCleanup": 0, "savedAt": 0}

# (端點, 請求 body)
WRITE_ENDPOINTS = [
    ("/api/save-settings", {"autoSubmitEnabled": True}),
    ("/api/save-session-history", {"sessions": [{"session_id": "<img src=x>"}]}),
    ("/api/add-user-message", {"content": "injected"}),
    ("/api/clear-settings", {}),
    ("/api/log-level", {"logLevel": "DEBUG"}),
]


@pytest.fixture
def env(web_ui_manager, test_project_dir, tmp_path, monkeypatch):
    """把 home 導到 tmp_path，預先放好設定檔，並建立一個活躍會話"""
    # Windows 的 Path.home() 讀 USERPROFILE，其他平台讀 HOME
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    assert Path.home() == tmp_path, "測試絕不能寫到真正的 ~/.config"

    config_dir = tmp_path / ".config" / "mcp-feedback-enhanced"
    config_dir.mkdir(parents=True)
    settings_file = config_dir / "ui_settings.json"
    history_file = config_dir / "session_history.json"
    settings_file.write_text(json.dumps(SETTINGS), encoding="utf-8")
    history_file.write_text(json.dumps(HISTORY), encoding="utf-8")

    web_ui_manager.create_session(str(test_project_dir), "摘要")
    session = web_ui_manager.get_current_session()
    client = TestClient(web_ui_manager.app)
    same_origin = f"http://127.0.0.1:{web_ui_manager.port}"
    yield web_ui_manager, session, client, same_origin, settings_file, history_file
    session._cleanup_sync()


def _snapshot(session, settings_file, history_file):
    return (
        settings_file.read_bytes(),
        history_file.read_bytes(),
        len(session.user_messages),
    )


class TestRejectsCrossSiteWrites:
    """advisory 的 PoC：跨站 text/plain POST 不得生效"""

    @pytest.mark.parametrize(("path", "body"), WRITE_ENDPOINTS)
    def test_cross_site_text_plain_rejected(self, env, path, body):
        _, session, client, _, settings_file, history_file = env
        before = _snapshot(session, settings_file, history_file)

        response = client.post(
            path,
            content=json.dumps(body),
            headers={"Origin": "https://evil.example", "Content-Type": "text/plain"},
        )

        assert response.status_code == 403
        assert _snapshot(session, settings_file, history_file) == before

    @pytest.mark.parametrize(("path", "body"), WRITE_ENDPOINTS)
    def test_cross_site_json_rejected(self, env, path, body):
        """即使帶了 application/json（瀏覽器會先 preflight），Origin 不符仍拒絕"""
        _, session, client, _, settings_file, history_file = env
        before = _snapshot(session, settings_file, history_file)

        response = client.post(
            path, json=body, headers={"Origin": "http://evil.example:8765"}
        )

        assert response.status_code == 403
        assert _snapshot(session, settings_file, history_file) == before

    @pytest.mark.parametrize(("path", "body"), WRITE_ENDPOINTS)
    def test_non_json_content_type_rejected(self, env, path, body):
        """Origin 可信但不是 JSON：回 415，逼跨站請求必須先 preflight"""
        _, session, client, same_origin, settings_file, history_file = env
        before = _snapshot(session, settings_file, history_file)

        response = client.post(
            path,
            content=json.dumps(body),
            headers={"Origin": same_origin, "Content-Type": "text/plain"},
        )

        assert response.status_code == 415
        assert _snapshot(session, settings_file, history_file) == before


class TestAllowsSameOriginJson:
    """正常前端（同源 + application/json）必須照常運作"""

    def test_save_settings(self, env):
        _, _, client, origin, settings_file, _ = env
        new = {"language": "en", "autoSubmitEnabled": False}

        response = client.post(
            "/api/save-settings", json=new, headers={"Origin": origin}
        )

        assert response.status_code == 200
        assert json.loads(settings_file.read_text(encoding="utf-8")) == new

    def test_save_session_history(self, env):
        _, _, client, origin, _, history_file = env
        sessions = [{"session_id": "abc", "status": "completed"}]

        response = client.post(
            "/api/save-session-history",
            json={"sessions": sessions},
            headers={"Origin": origin, "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert json.loads(history_file.read_text(encoding="utf-8"))["sessions"] == (
            sessions
        )

    def test_add_user_message(self, env):
        _, session, client, origin, _, _ = env

        response = client.post(
            "/api/add-user-message",
            json={"content": "hello"},
            headers={"Origin": origin},
        )

        assert response.status_code == 200
        assert session.user_messages[-1]["content"] == "hello"

    def test_log_level(self, env):
        _, _, client, origin, settings_file, _ = env

        response = client.post(
            "/api/log-level", json={"logLevel": "WARN"}, headers={"Origin": origin}
        )

        assert response.status_code == 200
        assert json.loads(settings_file.read_text(encoding="utf-8"))["logLevel"] == (
            "WARN"
        )

    def test_clear_settings(self, env):
        _, _, client, origin, settings_file, _ = env

        response = client.post(
            "/api/clear-settings", json={}, headers={"Origin": origin}
        )

        assert response.status_code == 200
        assert not settings_file.exists()

    def test_desktop_webview_origin_allowed(self, env):
        _, _, client, _, settings_file, _ = env

        response = client.post(
            "/api/log-level",
            json={"logLevel": "ERROR"},
            headers={"Origin": "tauri://localhost"},
        )

        assert response.status_code == 200
        assert json.loads(settings_file.read_text(encoding="utf-8"))["logLevel"] == (
            "ERROR"
        )

    def test_missing_origin_allowed(self, env):
        """非瀏覽器客戶端不會帶 Origin，與 /ws 規則一致"""
        _, _, client, _, settings_file, _ = env

        response = client.post("/api/log-level", json={"logLevel": "DEBUG"})

        assert response.status_code == 200
        assert json.loads(settings_file.read_text(encoding="utf-8"))["logLevel"] == (
            "DEBUG"
        )

    def test_json_with_charset_allowed(self, env):
        _, _, client, origin, settings_file, _ = env

        response = client.post(
            "/api/save-settings",
            content=json.dumps({"language": "en"}),
            headers={
                "Origin": origin,
                "Content-Type": "application/json; charset=utf-8",
            },
        )

        assert response.status_code == 200
        assert json.loads(settings_file.read_text(encoding="utf-8")) == {
            "language": "en"
        }

    def test_get_endpoints_unaffected(self, env):
        """讀取端點不受寫入檢查影響"""
        _, _, client, _, _, _ = env

        response = client.get(
            "/api/load-settings", headers={"Origin": "https://evil.example"}
        )

        assert response.status_code == 200


class TestWildcardBind:
    """綁 0.0.0.0 時，Origin 的 host:port 必須等於請求的 Host header"""

    def test_origin_matching_host_header_allowed(self, env):
        manager, _, client, _, settings_file, _ = env
        manager.host = "0.0.0.0"  # noqa: S104
        lan = f"192.168.1.50:{manager.port}"

        response = client.post(
            "/api/log-level",
            json={"logLevel": "WARN"},
            headers={"Origin": f"http://{lan}", "Host": lan},
        )

        assert response.status_code == 200
        assert json.loads(settings_file.read_text(encoding="utf-8"))["logLevel"] == (
            "WARN"
        )

    def test_foreign_host_same_port_rejected(self, env):
        manager, session, client, _, settings_file, history_file = env
        manager.host = "0.0.0.0"  # noqa: S104
        before = _snapshot(session, settings_file, history_file)

        response = client.post(
            "/api/save-settings",
            json={"autoSubmitEnabled": True},
            headers={
                "Origin": f"http://evil.example:{manager.port}",
                "Host": f"192.168.1.50:{manager.port}",
            },
        )

        assert response.status_code == 403
        assert _snapshot(session, settings_file, history_file) == before

    def test_websocket_compares_host_header(self, env):
        """/ws 與 HTTP 走同一個檢查，也要把 Host header 傳進去"""
        manager, _, client, _, _, _ = env
        manager.host = "0.0.0.0"  # noqa: S104
        lan = f"192.168.1.50:{manager.port}"

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(
                "/ws",
                headers={"Origin": f"http://evil.example:{manager.port}", "Host": lan},
            ):
                pass
        assert exc_info.value.code == 4003

        with client.websocket_connect(
            "/ws", headers={"Origin": f"http://{lan}", "Host": lan}
        ) as ws:
            assert ws.receive_json()["type"] == "connection_established"
