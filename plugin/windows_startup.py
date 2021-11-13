from subprocess import Popen
from pathlib import Path

from flox import Flox

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
                    subtitle = f"✔️{program.status}"
                    self.add_item(
                        title=program.name.replace(".lnk", ""),
                        subtitle=subtitle,
                        icon=program.path,
                        method='toggle',
                        parameters=[str(program._base_key), str(program._reg_path), str(program._key_index)],
                        context=[str(program._base_key), str(program._reg_path), str(program._key_index)]
                    )

    def context_menu(self, data):
        prog = startup.StartupProgram(int(data[0]), data[1], int(data[2]))
        self.add_item(
            title="Open Program",
            subtitle=prog.path,
            icon=prog.path,
            method='open_program',
            parameters=[prog.path]
        )
        self.add_item(
                title="Enable Program",
                subtitle="Allow program to start with Windows.",
                icon=ENABLED_ICON,
                method='enable',
                parameters=[str(prog._base_key), str(prog._reg_path), str(prog._key_index)]
        )
        self.add_item(
            title="Disable Program",
            subtitle="Prevent program from starting with Windows.",
            icon=DISABLED_ICON,
            method='disable',
            parameters=[str(prog._base_key), str(prog._reg_path), str(prog._key_index)]
        )


    def toggle(self, base_key, path, key_index):
        prog = startup.StartupProgram(int(base_key), path, int(key_index))
        prog.toggle()

    def enable(self, base_key, path, key_index):
        prog = startup.StartupProgram(int(base_key), path, int(key_index))
        prog.enable()

    def disable(self, base_key, path, key_index):
        prog = startup.StartupProgram(int(base_key), path, int(key_index))
        prog.disable()

    def open_program(self, path):
        proc = Popen(path)


if __name__ == "__main__":
    WindowsStartup()
