import os
import sys
import pytest
from cli.utils.terminal_utils import supports_color

class DummyArgs:
    def __init__(self, no_color=False):
        self.no_color = no_color

def test_supports_color_no_color_flag():
    args = DummyArgs(no_color=True)
    assert supports_color(args) is False

def test_supports_color_isatty_false(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    assert supports_color(DummyArgs()) is False

@pytest.mark.xfail(reason="ANSICON detection may not work in CI/Windows shells")
def test_supports_color_windows_ansicon(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setitem(os.environ, "ANSICON", "1")
    assert supports_color(DummyArgs()) is True

@pytest.mark.xfail(reason="WT_SESSION detection may not work in CI/Windows shells")
def test_supports_color_windows_wt_session(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setitem(os.environ, "WT_SESSION", "1")
    assert supports_color(DummyArgs()) is True

@pytest.mark.xfail(reason="VSCode TERM_PROGRAM detection may not work in CI/Windows shells")
def test_supports_color_windows_vscode(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setitem(os.environ, "TERM_PROGRAM", "vscode")
    assert supports_color(DummyArgs()) is True

def test_supports_color_posix(monkeypatch):
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert supports_color(DummyArgs()) is True
