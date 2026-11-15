from typing import List, Tuple

HKEY_CURRENT_USER = 0x80000001
HKEY_LOCAL_MACHINE = 0x80000002


def _winreg():
    import winreg

    return winreg


class WindowsRegistry:
    """The only code that touches winreg, so the rest runs off Windows."""

    def values(self, hive: int, path: str) -> List[Tuple[str, object]]:
        winreg = _winreg()
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            count = winreg.QueryInfoKey(key)[1]
            return [tuple(winreg.EnumValue(key, index)[:2]) for index in range(count)]

    def set_binary(self, hive: int, path: str, name: str, data: bytes) -> None:
        winreg = _winreg()
        with winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, data)
