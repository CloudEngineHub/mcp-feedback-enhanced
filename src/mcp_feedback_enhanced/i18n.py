#!/usr/bin/env python3
"""
國際化支援模組
===============

提供統一的多語系支援功能，支援繁體中文、簡體中文與英文。
後端語言只由環境變數與系統語言決定，不讀寫任何設定檔。

新架構：
- 使用分離的 JSON 翻譯檔案
- 支援巢狀翻譯鍵值
- 元資料支援
- 易於擴充新語言

作者: Minidoracat
"""

import json
import locale
import os
from pathlib import Path
from typing import Any

from .debug import i18n_debug_log as debug_log


SUPPORTED_LANGUAGES = ("zh-CN", "zh-TW", "en")


def get_forced_language() -> str | None:
    """MCP_LANGUAGE 指定的語言；去掉前後空白後不是支援的語言代碼就當作沒設"""
    value = os.getenv("MCP_LANGUAGE", "").strip()
    return value if value in SUPPORTED_LANGUAGES else None


class I18nManager:
    """國際化管理器 - 新架構版本"""

    def __init__(self):
        self._current_language = None
        self._translations = {}
        self._supported_languages = list(SUPPORTED_LANGUAGES)
        self._fallback_language = "zh-TW"
        self._locales_dir = Path(__file__).parent / "web" / "locales"

        # 載入翻譯
        self._load_all_translations()

        # 設定語言
        self._current_language = self._detect_language()

    def _load_all_translations(self) -> None:
        """載入所有語言的翻譯檔案"""
        self._translations = {}

        for lang_code in self._supported_languages:
            lang_dir = self._locales_dir / lang_code
            translation_file = lang_dir / "translation.json"

            if translation_file.exists():
                try:
                    with open(translation_file, encoding="utf-8") as f:
                        data = json.load(f)
                        self._translations[lang_code] = data
                        debug_log(
                            f"成功載入語言 {lang_code}: {data.get('meta', {}).get('displayName', lang_code)}"
                        )
                except Exception as e:
                    debug_log(f"載入語言檔案失敗 {lang_code}: {e}")
                    # 如果載入失敗，使用空的翻譯
                    self._translations[lang_code] = {}
            else:
                debug_log(f"找不到語言檔案: {translation_file}")
                self._translations[lang_code] = {}

    def _detect_language(self) -> str:
        """自動偵測語言"""
        # 1. MCP_LANGUAGE 是「強制指定」（見 #189）
        forced = get_forced_language()
        if forced:
            return forced

        # 2. 檢查其他環境變數（LANG, LC_ALL 等）
        for env_var in ["LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE"]:
            env_value = os.getenv(env_var, "").strip()
            if env_value:
                if env_value.startswith("zh_TW") or env_value.startswith("zh_Hant"):
                    return "zh-TW"
                if env_value.startswith("zh_CN") or env_value.startswith("zh_Hans"):
                    return "zh-CN"
                if env_value.startswith("en"):
                    return "en"

        # 3. 自動偵測系統語言（僅在非測試模式下）
        if not os.getenv("MCP_TEST_MODE"):
            try:
                # 獲取系統語言
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    if system_locale.startswith("zh_TW") or system_locale.startswith(
                        "zh_Hant"
                    ):
                        return "zh-TW"
                    if system_locale.startswith("zh_CN") or system_locale.startswith(
                        "zh_Hans"
                    ):
                        return "zh-CN"
                    if system_locale.startswith("en"):
                        return "en"
            except Exception:
                pass

        # 4. 回退到默認語言
        return self._fallback_language

    def get_current_language(self) -> str:
        """獲取當前語言"""
        return self._current_language or "zh-TW"

    def get_supported_languages(self) -> list[str]:
        """獲取支援的語言列表"""
        return self._supported_languages.copy()

    def _get_nested_value(self, data: dict[str, Any], key_path: str) -> str | None:
        """從巢狀字典中獲取值，支援點分隔的鍵路徑"""
        keys = key_path.split(".")
        current: Any = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return str(current) if isinstance(current, str) else None

    def t(self, key: str, **kwargs) -> str:
        """
        翻譯函數：'buttons.submit' -> data['buttons']['submit']

        找不到時改查回退語言，再找不到就回傳 key 本身。
        """
        # 獲取當前語言的翻譯
        current_translations = self._translations.get(self._current_language, {})
        text = self._get_nested_value(current_translations, key)

        # 如果沒有找到，嘗試使用回退語言
        if text is None:
            fallback_translations = self._translations.get(self._fallback_language, {})
            text = self._get_nested_value(fallback_translations, key)

        # 最後回退到鍵本身
        if text is None:
            text = key

        # 處理格式化參數
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass

        return text


# 全域的國際化管理器實例
_i18n_manager = None


def get_i18n_manager() -> I18nManager:
    """獲取全域的國際化管理器實例"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def t(key: str, **kwargs) -> str:
    """便捷的翻譯函數"""
    return get_i18n_manager().t(key, **kwargs)


def get_current_language() -> str:
    """獲取當前語言"""
    return get_i18n_manager().get_current_language()
