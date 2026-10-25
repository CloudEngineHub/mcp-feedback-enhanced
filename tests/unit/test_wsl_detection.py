#!/usr/bin/env python3
"""WSL 偵測只在 Linux 上成立：原生 Windows 設了 WSLENV 也不能被判成 WSL"""

import platform

from mcp_feedback_enhanced.web.utils.browser import is_wsl_environment


WSL_ENV_VARS = ("WSL_DISTRO_NAME", "WSL_INTEROP", "WSLENV")


def _clear_wsl_env(monkeypatch):
    for name in WSL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_native_windows_with_wslenv_is_not_wsl(monkeypatch):
    _clear_wsl_env(monkeypatch)
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setenv("WSLENV", "GIT_TERMINAL_PROMPT")

    assert is_wsl_environment() is False


def test_linux_with_wsl_distro_name_is_wsl(monkeypatch):
    _clear_wsl_env(monkeypatch)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")

    assert is_wsl_environment() is True
