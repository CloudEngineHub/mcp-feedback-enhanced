#!/usr/bin/env python3
"""
測試配置和共用 fixtures
"""

import asyncio
import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest


# 產品程式會在匯入或建構時就算好家目錄底下的路徑（feedback_session.TEMP_DIR、
# I18nManager._config_file），所以這裡不在模組層匯入 mcp_feedback_enhanced，
# 讓家目錄在任何測試模組匯入產品程式之前就導走。
if TYPE_CHECKING:
    from mcp_feedback_enhanced.web.main import WebUIManager

_REAL_HOME = Path.home()
_home_patch = pytest.MonkeyPatch()


@pytest.hookimpl(trylast=True)  # 等 tmpdir 外掛先建好 _tmp_path_factory
def pytest_configure(config: pytest.Config) -> None:
    """整個測試階段把 USERPROFILE／HOME 指到 pytest 暫存目錄，子行程一併繼承"""
    home = config._tmp_path_factory.mktemp("home", numbered=False)  # type: ignore[attr-defined]
    _home_patch.setenv("USERPROFILE", str(home))
    _home_patch.setenv("HOME", str(home))


def pytest_unconfigure(config: pytest.Config) -> None:
    _home_patch.undo()


def _assert_home_isolated() -> None:
    from mcp_feedback_enhanced.i18n import get_i18n_manager
    from mcp_feedback_enhanced.web.models import feedback_session

    assert Path.home() != _REAL_HOME, f"Path.home() 仍指向真的家目錄 {_REAL_HOME}"
    for path in (get_i18n_manager()._config_file, feedback_session.TEMP_DIR):
        for real_dir in (_REAL_HOME / ".config", _REAL_HOME / ".cache"):
            assert not path.is_relative_to(real_dir), f"{path} 仍在真的家目錄底下"


@pytest.fixture(scope="session", autouse=True)
def guard_real_home() -> Generator[None, None, None]:
    """測試前後都確認沒有任何路徑指向真的家目錄"""
    _assert_home_isolated()
    yield
    _assert_home_isolated()


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環 fixture"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """創建臨時目錄 fixture"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_project_dir(temp_dir: Path) -> Path:
    """創建測試專案目錄"""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()

    # 創建一些測試文件
    (project_dir / "README.md").write_text("# Test Project")
    (project_dir / "main.py").write_text("print('Hello World')")

    return project_dir


@pytest.fixture
def web_ui_manager() -> Generator["WebUIManager", None, None]:
    """創建 WebUIManager fixture"""
    from mcp_feedback_enhanced.web.main import WebUIManager

    # 設置測試模式環境變數
    original_test_mode = os.environ.get("MCP_TEST_MODE")
    original_web_host = os.environ.get("MCP_WEB_HOST")
    original_web_port = os.environ.get("MCP_WEB_PORT")

    os.environ["MCP_TEST_MODE"] = "true"
    os.environ["MCP_WEB_HOST"] = "127.0.0.1"  # 確保測試使用本地主機
    # 使用動態端口範圍避免衝突
    os.environ["MCP_WEB_PORT"] = "0"  # 讓系統自動分配端口

    try:
        manager = WebUIManager()  # 使用環境變數控制主機和端口
        yield manager
    finally:
        # 恢復原始環境變數
        if original_test_mode is not None:
            os.environ["MCP_TEST_MODE"] = original_test_mode
        else:
            os.environ.pop("MCP_TEST_MODE", None)

        if original_web_host is not None:
            os.environ["MCP_WEB_HOST"] = original_web_host
        else:
            os.environ.pop("MCP_WEB_HOST", None)

        if original_web_port is not None:
            os.environ["MCP_WEB_PORT"] = original_web_port
        else:
            os.environ.pop("MCP_WEB_PORT", None)

        # 清理
        if manager.server_thread and manager.server_thread.is_alive():
            # 這裡可以添加服務器停止邏輯
            pass


@pytest.fixture
def i18n_manager():
    """創建 I18N 管理器 fixture"""
    from mcp_feedback_enhanced.i18n import get_i18n_manager

    return get_i18n_manager()


@pytest.fixture
def test_config() -> dict[str, Any]:
    """測試配置 fixture"""
    return {
        "timeout": 30,
        "debug": True,
        "web_port": 8765,
        "test_summary": "測試摘要 - 這是一個自動化測試",
        "test_feedback": "這是測試回饋內容",
    }


@pytest.fixture(autouse=True)
def setup_test_env():
    """自動設置測試環境"""
    # 設置測試環境變數
    original_debug = os.environ.get("MCP_DEBUG")
    os.environ["MCP_DEBUG"] = "true"

    yield

    # 恢復原始環境
    if original_debug is not None:
        os.environ["MCP_DEBUG"] = original_debug
    else:
        os.environ.pop("MCP_DEBUG", None)
