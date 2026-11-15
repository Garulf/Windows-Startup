import subprocess
import sys
import types
from pathlib import Path

import pytest

from registry import HKEY_CURRENT_USER, WindowsRegistry

PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"


class FakeKey:
    def __init__(self, log, values):
        self.log = log
        self.values = values

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.log.append(("close",))


@pytest.fixture
def winreg(monkeypatch):
    log = []
    values = [("Discord", b"\x02", 3), ("Spotify", b"\x03", 3)]
    module = types.ModuleType("winreg")
    module.KEY_READ = 0x20019
    module.KEY_ALL_ACCESS = 0xF003F
    module.REG_BINARY = 3

    def open_key(hive, path, reserved, access):
        log.append(("OpenKey", hive, path, reserved, access))
        return FakeKey(log, values)

    module.OpenKey = open_key
    module.QueryInfoKey = lambda key: (0, len(key.values), 0)
    module.EnumValue = lambda key, index: key.values[index]
    module.SetValueEx = lambda key, *args: log.append(("SetValueEx", *args))
    monkeypatch.setitem(sys.modules, "winreg", module)
    module.log = log
    return module


def test_values_opens_key_read_only(winreg):
    assert WindowsRegistry().values(HKEY_CURRENT_USER, PATH) == [("Discord", b"\x02"), ("Spotify", b"\x03")]
    assert winreg.log == [("OpenKey", HKEY_CURRENT_USER, PATH, 0, winreg.KEY_READ), ("close",)]


def test_set_binary_writes_reg_binary(winreg):
    WindowsRegistry().set_binary(HKEY_CURRENT_USER, PATH, "Spotify", b"\x02\x00")
    assert winreg.log == [
        ("OpenKey", HKEY_CURRENT_USER, PATH, 0, winreg.KEY_ALL_ACCESS),
        ("SetValueEx", "Spotify", 0, winreg.REG_BINARY, b"\x02\x00"),
        ("close",),
    ]


def test_importing_the_plugin_does_not_need_winreg(tmp_path):
    plugin_dir = Path(__file__).resolve().parents[1] / "src" / "plugin"
    code = f"import sys; sys.modules['winreg'] = None; sys.path.insert(0, {str(plugin_dir)!r}); import windows_startup"
    subprocess.run([sys.executable, "-c", code], cwd=tmp_path, check=True)
