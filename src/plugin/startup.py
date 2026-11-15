import os
from pathlib import PureWindowsPath
from typing import List, Optional

from registry import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, WindowsRegistry

RUN_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
APPROVED_PATHS = (
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder",
)
HIVES = (HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE)
ENABLED = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
DISABLED = b'\x03\x00\x00\x00\x11\xd0\xb6I\xc3\xaa\xd7\x01'

registry = WindowsRegistry()


def windir() -> str:
    return os.environ.get("WINDIR", r"C:\Windows")


def user_startup_folder() -> PureWindowsPath:
    return PureWindowsPath(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")


def system_startup_folder() -> PureWindowsPath:
    program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    return PureWindowsPath(program_data, "Microsoft", "Windows", "Start Menu", "Programs", "StartUp")


class StartupProgram:

    def __init__(self, base_key: int, reg_path: str, key_index: int):
        self.base_key = base_key
        self.reg_path = reg_path
        self.key_index = key_index

    def __str__(self) -> str:
        return f"{self.name} ({self.path})"

    @property
    def rpc_parameters(self) -> List[str]:
        return [str(self.base_key), self.reg_path, str(self.key_index)]

    def _entry(self):
        return registry.values(self.base_key, self.reg_path)[self.key_index]

    @property
    def name(self) -> str:
        return self._entry()[0]

    def value(self) -> Optional[bool]:
        data = self._entry()[1]
        if data == ENABLED:
            return True
        if data == DISABLED:
            return False
        return None

    @property
    def status(self) -> str:
        return "Enabled" if self.value() else "Disabled"

    @property
    def command(self) -> Optional[str]:
        name = self.name.lower()
        try:
            run_values = registry.values(self.base_key, RUN_PATH)
        except FileNotFoundError:
            return None
        for value_name, data in run_values:
            if value_name.lower() == name:
                return data
        return None

    @property
    def path(self) -> str:
        if PureWindowsPath(self.reg_path).name == "StartupFolder":
            folder = user_startup_folder() if self.base_key == HKEY_CURRENT_USER else system_startup_folder()
            return str(folder / self.name)
        command = self.command
        if not command:
            return str(None)
        return command.split(" -")[0].split(" /")[0].replace("\"", "").replace("%windir%", windir())

    def enable(self) -> None:
        registry.set_binary(self.base_key, self.reg_path, self.name, ENABLED)

    def disable(self) -> None:
        registry.set_binary(self.base_key, self.reg_path, self.name, DISABLED)

    def toggle(self) -> None:
        if self.value():
            self.disable()
        else:
            self.enable()


def get_startup_programs() -> List[StartupProgram]:
    programs = []
    for base_key in HIVES:
        for path in APPROVED_PATHS:
            try:
                count = len(registry.values(base_key, path))
            except FileNotFoundError:
                continue
            programs.extend(StartupProgram(base_key, path, index) for index in range(count))
    return programs
