#!/usr/bin/env python3
"""
MCP_LANGUAGE 帶進頁面的回歸測試（#189）

合法的 MCP_LANGUAGE 由伺服器寫進 <html lang> 與 data-forced-language，
前端第一次套用翻譯就用它；不合法或沒設時維持 lang="zh-TW"、不輸出屬性。
等待頁（沒有會話）與回饋頁（有會話）行為一致。
"""

import pytest
from fastapi.testclient import TestClient


def _get_index(web_ui_manager, test_project_dir, with_session: bool) -> str:
    if with_session:
        web_ui_manager.create_session(str(test_project_dir), "摘要")
    try:
        response = TestClient(web_ui_manager.app).get("/")
        assert response.status_code == 200
        return str(response.text)
    finally:
        session = web_ui_manager.get_current_session()
        if session:
            session._cleanup_sync()


@pytest.mark.parametrize("with_session", [False, True])
@pytest.mark.parametrize("language", ["zh-TW", "zh-CN", "en"])
def test_valid_forced_language_in_page(
    web_ui_manager, test_project_dir, monkeypatch, language, with_session
):
    monkeypatch.setenv("MCP_LANGUAGE", language)
    html = _get_index(web_ui_manager, test_project_dir, with_session)
    assert f'<html lang="{language}" data-forced-language="{language}"' in html
    marker = 'id="statsPanel"' if with_session else 'id="waitingContainer"'
    assert marker in html


@pytest.mark.parametrize("with_session", [False, True])
@pytest.mark.parametrize("value", [None, "ja", "EN", "zh_TW", ""])
def test_invalid_or_unset_forced_language_not_in_page(
    web_ui_manager, test_project_dir, monkeypatch, value, with_session
):
    if value is None:
        monkeypatch.delenv("MCP_LANGUAGE", raising=False)
    else:
        monkeypatch.setenv("MCP_LANGUAGE", value)
    html = _get_index(web_ui_manager, test_project_dir, with_session)
    assert '<html lang="zh-TW" id="html-root">' in html
    assert "data-forced-language" not in html
