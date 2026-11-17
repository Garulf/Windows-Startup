import pytest

import startup
from registry import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE

APPROVED_RUN, APPROVED_RUN32, APPROVED_FOLDER = startup.APPROVED_PATHS


class FakeRegistry:
    def __init__(self, keys):
        self.keys = {location: list(values) for location, values in keys.items()}
        self.writes = []

    def values(self, hive, path):
        if (hive, path) not in self.keys:
            raise FileNotFoundError(path)
        return list(self.keys[(hive, path)])

    def set_binary(self, hive, path, name, data):
        self.writes.append((hive, path, name, data))
        values = self.keys[(hive, path)]
        for index, (value_name, _) in enumerate(values):
            if value_name == name:
                values[index] = (name, data)
                return
        values.append((name, data))


def sample_keys():
    return {
        (HKEY_CURRENT_USER, startup.RUN_PATH): [
            ("Discord", r'"C:\Users\alex\AppData\Local\Discord\Update.exe" --processStart Discord.exe'),
            ("Spotify", r"C:\Users\alex\AppData\Roaming\Spotify\Spotify.exe /minimized"),
        ],
        (HKEY_CURRENT_USER, APPROVED_RUN): [
            ("Discord", startup.ENABLED),
            ("Spotify", startup.DISABLED),
        ],
        (HKEY_CURRENT_USER, APPROVED_FOLDER): [
            ("Notes.lnk", startup.ENABLED),
        ],
        (HKEY_LOCAL_MACHINE, startup.RUN_PATH): [
            ("SecurityHealth", r"%windir%\system32\SecurityHealthSystray.exe"),
        ],
        (HKEY_LOCAL_MACHINE, APPROVED_RUN): [
            ("SecurityHealth", startup.ENABLED),
        ],
        (HKEY_LOCAL_MACHINE, APPROVED_FOLDER): [
            ("Backup.lnk", startup.DISABLED),
        ],
    }


@pytest.fixture
def fake_registry(monkeypatch):
    fake = FakeRegistry(sample_keys())
    monkeypatch.setattr(startup, "registry", fake)
    monkeypatch.setenv("APPDATA", r"C:\Users\alex\AppData\Roaming")
    monkeypatch.setenv("WINDIR", r"C:\Windows")
    monkeypatch.setenv("PROGRAMDATA", r"C:\ProgramData")
    return fake
