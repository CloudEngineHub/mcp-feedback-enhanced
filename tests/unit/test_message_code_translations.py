#!/usr/bin/env python3
"""後端以 messageCode 回給前端顯示的訊息代碼，三個語系都要有翻譯

前端收到 messageCode 後用 i18nManager.t(messageCode) 顯示；缺翻譯時使用者會
看到 key 本身。
"""

import json
import re
from pathlib import Path

import pytest

from mcp_feedback_enhanced.web.constants import get_message_code


WEB_DIR = Path(__file__).resolve().parents[2] / "src/mcp_feedback_enhanced/web"
LOCALES = ("zh-TW", "zh-CN", "en")


def _sent_message_codes() -> list[str]:
    source = (WEB_DIR / "routes/main_routes.py").read_text(encoding="utf-8")
    keys = set(re.findall(r'"messageCode":\s*get_msg_code\("([^"]+)"\)', source))
    return sorted({get_message_code(key) for key in keys})


def _lookup(data: dict, dotted_key: str) -> object:
    current: object = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def test_message_codes_are_found():
    codes = _sent_message_codes()
    assert codes, "main_routes.py 裡找不到任何 messageCode，正規表示式可能過時"
    assert not [code for code in codes if code.startswith("unknown.")]


@pytest.mark.parametrize("locale", LOCALES)
def test_sent_message_codes_are_translated(locale):
    translation_file = WEB_DIR / "locales" / locale / "translation.json"
    data = json.loads(translation_file.read_text(encoding="utf-8"))

    missing = [
        code
        for code in _sent_message_codes()
        if not isinstance(_lookup(data, code), str)
    ]
    assert missing == []
