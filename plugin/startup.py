import subprocess as sp
import winreg as reg
import os
from pathlib import Path
import logging
import logging.handlers


COMMAND = "wmic startup list /format:csv"
RUN_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
ENABLED = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
DISABLED = b'\x03\x00\x00\x00\x11\xd0\xb6I\xc3\xaa\xd7\x01'
BASE_KEYS = {
    reg.HKEY_CURRENT_USER: str(reg.HKEY_CURRENT_USER),
    reg.HKEY_LOCAL_MACHINE: str(reg.HKEY_LOCAL_MACHINE)
}
USER_STARTUP = Path(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
SYSTEM_STARTUP = Path(os.getenv("WINDIR"), "Microsoft", "Windows", "Start Menu", "StartUp")

class StartupProgram():

    def __init__(self, base_key: int, reg_path: str, key_index: int):
        self._base_key = base_key
        self._reg_path = reg_path
        self._key_index = key_index
        self._name = None
        self._command = None
        self._path = None

    def __str__(self):
        return f"{self.name} ({self.path})"

    @property
    def name(self):
        if self._name is None:
            self._name = self._get_registry_value(self._base_key, self._reg_path, self._key_index)[0]
        return self._name

    @property
    def _value(self):
        return self._get_registry_value(self._base_key, self._reg_path, self._key_index)[1]

    def value(self):
        if self._value == ENABLED:
            return True
        elif self._value == DISABLED:
            return False
        else:
            return None


    def _get_registry_value(self, base_key, path, index):
        with reg.OpenKey(base_key, path, 0, reg.KEY_READ) as key_root:
            return reg.EnumValue(key_root, index)

    def _set_registry_value(self, base_key, path, value_name, value):
        with reg.OpenKey(base_key, path, 0, reg.KEY_ALL_ACCESS) as key_root:
            reg.SetValueEx(key_root, value_name, 0, reg.REG_BINARY, value)

    def _find_command(self, name, base_key):
        with reg.OpenKey(base_key, RUN_PATH, 0, reg.KEY_READ) as key_root:
            for i in range(0, reg.QueryInfoKey(key_root)[1]):
                _ = self._get_registry_value(base_key, RUN_PATH, i)
                if name.lower() == _[0].lower():
                    return _[1]

    @property
    def command(self):
        if self._command is None:
            self._command = self._find_command(self.name, self._base_key)
            if self._command:
                self._command.replace("%windir%", os.getenv("WINDIR"))
        return self._command

    @property
    def path(self):
        if self._path is None:
            if self.name.endswith(".lnk"):
                for path in [USER_STARTUP, SYSTEM_STARTUP]:
                    if Path(path, self.name).exists():
                        self._path = Path(path, self.name)
                        break
            elif self.command:
                self._path = self.command.split(" -")[0].split(" /")[0].replace("\"", "").replace("%windir%", os.getenv("WINDIR"))
        return str(self._path)

    @property
    def status(self):
        if self.value():
            return "Enabled"
        else:
            return "Disabled"

    def enable(self):
        self._set_registry_value(self._base_key, self._reg_path, self.name, ENABLED)

    def disable(self):
        self._set_registry_value(self._base_key, self._reg_path, self.name, DISABLED)

    def toggle(self):
        if self.value():
            self.disable()
        else:
            self.enable()





def get_startup_programs():
    program_list = []

    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder"
    ]
    for base_key in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
        for path in reg_paths:
            try:
                with reg.OpenKey(base_key, path, 0, reg.KEY_READ) as key_root:
                    for i in range(0, reg.QueryInfoKey(key_root)[1]):
                        program_list.append(
                            StartupProgram(base_key, path, i)
                        )
            except FileNotFoundError:
                continue
    return program_list

        



if __name__ == "__main__":
    programs = get_startup_programs()
    for prog in programs:
        if prog.name == "Steam":
            print(prog)
            print(prog.status)
            # prog.toggle()
            print(prog.status)
            print(type(prog._base_key))
