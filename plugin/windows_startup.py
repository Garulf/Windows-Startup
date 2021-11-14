import os
from subprocess import Popen
from pathlib import Path
from typing import Callable

from flox import Flox, ICON_APP_ERROR

import startup

ICONS_DIR = Path.joinpath(Path(__file__).absolute().parent.parent, "icons")
ENABLED_ICON = str(Path(ICONS_DIR).joinpath("check-circle.png"))
DISABLED_ICON = str(Path(ICONS_DIR).joinpath("checkbox-blank-circle.png"))
class WindowsStartup(Flox):

    def query(self, query):
        programs = startup.get_startup_programs()
        for program in programs:
            if query.lower() in program.name.lower():
                subtitle = f"❌{program.status}"
                if program.value():
                    subtitle = f"✔️{program.status} - Toggle program startup behavior"
                self.add_item(
                    title=program.name.replace(".lnk", ""),
                    subtitle=subtitle,
                    icon=program.path,
                    method=self.change_state,
                    parameters=["toggle", str(program._base_key), str(program._reg_path), str(program._key_index)],
                    context=[str(program._base_key), str(program._reg_path), str(program._key_index)]
                )

    def context_menu(self, data):
        prog = startup.StartupProgram(int(data[0]), data[1], int(data[2]))
        if prog.path == "None":
            self.add_item(
                title="Open Program",
                subtitle=prog.path,
                icon=prog.path,
                method=self.open_program,
                parameters=[prog.path]
            )
            self.add_item(
                title="Reveal in Explorer",
                subtitle=prog.path,
                icon=str(Path(os.getenv('WINDIR'), 'explorer.exe')),
                method=self.reveal_in_finder,
                parameters=[prog.path]
            )
        self.add_item(
                title="Enable Program",
                subtitle="Allow program to start with Windows.",
                icon=ENABLED_ICON,
                method=self.change_state,
                parameters=["enable", str(prog._base_key), str(prog._reg_path), str(prog._key_index)]
        )
        self.add_item(
            title="Disable Program",
            subtitle="Prevent program from starting with Windows.",
            icon=DISABLED_ICON,
            method=self.change_state,
            parameters=["disable", str(prog._base_key), str(prog._reg_path), str(prog._key_index)]
        )

    def change_program(self, program: startup.StartupProgram, method: Callable, msg: str, fail_msg: str):
        _begin_state = program.value()
        method()
        _format = {"name": program.name, "status": program.status.lower()}
        if program.value() != _begin_state:
            msg = msg.format(**_format)
            self.show_msg(f"{program.name} {program.status}", msg, ico_path=program.path)
        else:
            fail_msg = fail_msg.format(**_format)
            self.show_msg(f"Error", fail_msg.format(program), ico_path=ICON_APP_ERROR)

    def change_state(self, state, base_key, path, key_index):
        prog = startup.StartupProgram(int(base_key), path, int(key_index))
        self.change_program(prog, getattr(prog, state), "Program start-up is {status}", "Unable to change {name} to {status}!")

    def open_program(self, path):
        os.startfile(path)

    def reveal_in_finder(self, path):
        Popen(f"explorer /select,{path}")


if __name__ == "__main__":
    WindowsStartup()
