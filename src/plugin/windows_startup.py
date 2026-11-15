from pathlib import Path, PureWindowsPath
from typing import Callable, List

from pyflowlauncher import FlowLauncherV2, Plugin, Result

import shell
import startup

PLUGIN_NAME = "Windows Startup"
PLUGIN_DIR = Path(__file__).resolve().parent
ICON = str(PLUGIN_DIR.parent / "icon.png")
ENABLED_ICON = str(PLUGIN_DIR / "icons" / "check-circle.png")
DISABLED_ICON = str(PLUGIN_DIR / "icons" / "checkbox-blank-circle.png")

plugin = Plugin(launcher=FlowLauncherV2())


def program_from(parameters: List[str]) -> startup.StartupProgram:
    base_key, reg_path, key_index = parameters
    return startup.StartupProgram(int(base_key), reg_path, int(key_index))


def subtitle(program: startup.StartupProgram) -> str:
    if program.value():
        return f"✔️{program.status} - Press ENTER to toggle program startup behavior"
    return f"❌{program.status}"


@plugin.on_method
def query(query: str):
    for program in startup.get_startup_programs():
        if query.lower() in program.name.lower():
            yield Result(
                title=program.name.replace(".lnk", ""),
                subtitle=subtitle(program),
                icon=program.path,
                context_data=program.rpc_parameters,
            ).add_action(toggle, parameters=program.rpc_parameters)


@plugin.on_method
def context_menu(data: List[str]):
    program = program_from(data)
    return [
        Result(
            title="Open Program",
            subtitle=program.path,
            icon=program.path,
        ).add_action(open_program, parameters=[program.path]),
        Result(
            title="Reveal in Explorer",
            subtitle="Reveals and selects program in file explorer.",
            icon=str(PureWindowsPath(startup.windir(), "explorer.exe")),
        ).add_action(reveal_in_finder, parameters=[program.path]),
        Result(
            title="Enable Program",
            subtitle="Allow program to start with Windows.",
            icon=ENABLED_ICON,
        ).add_action(enable, parameters=program.rpc_parameters),
        Result(
            title="Disable Program",
            subtitle="Prevent program from starting with Windows.",
            icon=DISABLED_ICON,
        ).add_action(disable, parameters=program.rpc_parameters),
    ]


def change_program(program: startup.StartupProgram, change: Callable[[], None]):
    before = program.value()
    change()
    if program.value() != before:
        title = f"{PLUGIN_NAME}: {program.status}!"
        message = f"{program.name.title()} start-up is {program.status}"
    else:
        title = f"{PLUGIN_NAME}: ERROR!"
        message = f"Unable to change {program.name} to {program.status}!"
    return plugin.launcher.api.show_msg(title, message, ICON)


@plugin.on_method
def enable(base_key: str, reg_path: str, key_index: str):
    program = program_from([base_key, reg_path, key_index])
    return change_program(program, program.enable)


@plugin.on_method
def disable(base_key: str, reg_path: str, key_index: str):
    program = program_from([base_key, reg_path, key_index])
    return change_program(program, program.disable)


@plugin.on_method
def toggle(base_key: str, reg_path: str, key_index: str):
    program = program_from([base_key, reg_path, key_index])
    return change_program(program, program.toggle)


@plugin.on_method
def open_program(path: str):
    shell.open_file(path)


@plugin.on_method
def reveal_in_finder(path: str):
    shell.reveal_in_explorer(path)
