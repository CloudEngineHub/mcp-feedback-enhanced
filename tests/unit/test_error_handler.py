"""
錯誤處理框架測試模組

測試 ErrorHandler 類的各項功能，包括：
- 錯誤類型自動分類
- 用戶友好錯誤信息生成
- 國際化支持
- 錯誤上下文記錄
"""

from unittest.mock import patch

import pytest

# 移除手動路徑操作，讓 mypy 和 pytest 使用正確的模組解析
from mcp_feedback_enhanced.utils.error_handler import (
    ErrorHandler,
    ErrorSeverity,
    ErrorType,
)


class TestErrorHandler:
    """錯誤處理器測試類"""

    def test_classify_error_network(self):
        """測試網絡錯誤分類"""
        # 測試 ConnectionError
        error = ConnectionError("Connection failed")
        assert ErrorHandler.classify_error(error) == ErrorType.NETWORK

        # 測試包含網絡關鍵字的錯誤（不包含 timeout）
        # 修復 assignment 錯誤 - 使用正確的異常類型
        network_error = Exception("socket connection failed")
        assert ErrorHandler.classify_error(network_error) == ErrorType.NETWORK

    def test_classify_error_file_io(self):
        """測試文件 I/O 錯誤分類"""
        # 測試 FileNotFoundError
        error = FileNotFoundError("No such file or directory")
        assert ErrorHandler.classify_error(error) == ErrorType.FILE_IO

        # 測試包含文件關鍵字的錯誤（不包含權限關鍵字）
        # 修復 assignment 錯誤 - 使用正確的異常類型
        file_error = Exception("file not found")
        assert ErrorHandler.classify_error(file_error) == ErrorType.FILE_IO

    def test_classify_error_timeout(self):
        """測試超時錯誤分類"""
        error = TimeoutError("Operation timed out")
        assert ErrorHandler.classify_error(error) == ErrorType.TIMEOUT

        timeout_error = Exception("timeout occurred")
        assert ErrorHandler.classify_error(timeout_error) == ErrorType.TIMEOUT

    def test_classify_error_permission(self):
        """測試權限錯誤分類"""
        error = PermissionError("Access denied")
        assert ErrorHandler.classify_error(error) == ErrorType.PERMISSION

        permission_error = Exception("access denied")
        assert ErrorHandler.classify_error(permission_error) == ErrorType.PERMISSION

    def test_classify_error_validation(self):
        """測試驗證錯誤分類"""
        error = ValueError("Invalid value")
        assert ErrorHandler.classify_error(error) == ErrorType.VALIDATION

        type_error = TypeError("Wrong type")
        assert ErrorHandler.classify_error(type_error) == ErrorType.VALIDATION

    def test_classify_error_default_system(self):
        """測試默認系統錯誤分類"""
        error = Exception("Some completely unknown issue")
        assert ErrorHandler.classify_error(error) == ErrorType.SYSTEM

    def test_format_user_error_basic(self):
        """測試基本用戶友好錯誤信息生成"""
        error = ConnectionError("Connection failed")
        result = ErrorHandler.format_user_error(error)

        assert "❌" in result
        assert (
            "網路連線出現問題" in result
            or "网络连接出现问题" in result
            or "Network connection issue" in result
        )

    def test_format_user_error_with_context(self):
        """測試帶上下文的錯誤信息生成"""
        error = FileNotFoundError("File not found")
        context = {"operation": "文件讀取", "file_path": "/path/to/file.txt"}

        result = ErrorHandler.format_user_error(error, context=context)

        assert "❌" in result
        assert "文件讀取" in result or "文件读取" in result or "文件讀取" in result
        assert "/path/to/file.txt" in result

    def test_format_user_error_with_technical_details(self):
        """測試包含技術細節的錯誤信息"""
        error = ValueError("Invalid input")
        result = ErrorHandler.format_user_error(error, include_technical=True)

        assert "❌" in result
        assert "ValueError" in result
        assert "Invalid input" in result

    def test_log_error_with_context(self):
        """測試帶上下文的錯誤記錄"""
        error = Exception("Test error")
        context = {"operation": "測試操作", "user": "test_user"}

        error_id = ErrorHandler.log_error_with_context(error, context=context)

        assert isinstance(error_id, str)
        assert error_id.startswith("ERR_")
        assert len(error_id.split("_")) == 3  # ERR_timestamp_id

    @pytest.mark.parametrize(
        ("language", "expected"),
        [
            ("zh-TW", "網路連線出現問題"),
            ("zh-CN", "网络连接出现问题"),
            ("en", "Network connection issue"),
        ],
    )
    def test_language_support(self, language, expected):
        """錯誤訊息依介面語言從內建訊息表取得"""
        with patch.object(ErrorHandler, "get_current_language", return_value=language):
            assert ErrorHandler.get_error_message(ErrorType.NETWORK) == expected
            result = ErrorHandler.format_user_error(ConnectionError("Network error"))
        assert result.startswith(f"❌ {expected}")

    @pytest.mark.parametrize(
        ("language", "expected_lines"),
        [
            ("zh-TW", ["操作：load", "檔案：/a.txt", "技術細節：ValueError: boom"]),
            ("zh-CN", ["操作：load", "文件：/a.txt", "技术细节：ValueError: boom"]),
            (
                "en",
                [
                    "Operation: load",
                    "File: /a.txt",
                    "Technical details: ValueError: boom",
                ],
            ),
        ],
    )
    def test_context_labels_follow_language(self, language, expected_lines):
        """上下文前綴依介面語言分開：簡中不能出現繁中的「檔案：」「技術細節：」"""
        with patch.object(ErrorHandler, "get_current_language", return_value=language):
            result = ErrorHandler.format_user_error(
                ValueError("boom"),
                error_type=ErrorType.FILE_IO,
                context={"operation": "load", "file_path": "/a.txt"},
                include_technical=True,
            )
        assert result.splitlines()[1:] == expected_lines

    def test_error_severity_logging(self):
        """測試錯誤嚴重程度記錄"""
        error = Exception("Critical system error")

        # 測試高嚴重程度錯誤
        error_id = ErrorHandler.log_error_with_context(
            error, severity=ErrorSeverity.CRITICAL
        )

        assert isinstance(error_id, str)
        assert error_id.startswith("ERR_")

    def test_get_current_language_fallback(self):
        """測試語言獲取回退機制"""
        # 由於 i18n 系統可能會覆蓋環境變數，我們主要測試函數不會拋出異常
        language = ErrorHandler.get_current_language()
        assert isinstance(language, str)
        assert len(language) > 0

        # 測試語言代碼格式
        assert language in ["zh-TW", "zh-CN", "en"] or "-" in language

    def test_error_context_preservation(self):
        """測試錯誤上下文保存"""
        error = Exception("Test error")
        context = {
            "operation": "測試操作",
            "file_path": "/test/path",
            "user_id": "test_user",
            "timestamp": "2025-01-05",
        }

        error_id = ErrorHandler.log_error_with_context(error, context=context)

        # 驗證錯誤 ID 格式
        assert isinstance(error_id, str)
        assert error_id.startswith("ERR_")

        # 上下文應該被記錄到調試日誌中（通過 debug_log）
        # 這裡我們主要驗證函數不會拋出異常

    def test_json_rpc_safety(self):
        """測試不影響 JSON RPC 通信"""
        # 錯誤處理應該只記錄到 stderr（通過 debug_log）
        # 不應該影響 stdout 或 JSON RPC 響應

        error = Exception("Test error for JSON RPC safety")
        context = {"operation": "JSON RPC 測試"}

        # 這些操作不應該影響 stdout
        error_id = ErrorHandler.log_error_with_context(error, context=context)
        user_message = ErrorHandler.format_user_error(error)

        # 驗證返回值類型正確
        assert isinstance(error_id, str)
        assert isinstance(user_message, str)

        # 驗證不會拋出異常
        assert error_id.startswith("ERR_")
        assert "❌" in user_message


if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v"])
