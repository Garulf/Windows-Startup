import startup
from conftest import APPROVED_FOLDER, APPROVED_RUN
from registry import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE


def names(programs):
    return [program.name for program in programs]


def test_lists_approved_entries_from_both_hives(fake_registry):
    programs = startup.get_startup_programs()
    assert names(programs) == ["Discord", "Spotify", "Notes.lnk", "SecurityHealth", "Backup.lnk"]
    assert [(p.base_key, p.reg_path, p.key_index) for p in programs[:2]] == [
        (HKEY_CURRENT_USER, APPROVED_RUN, 0),
        (HKEY_CURRENT_USER, APPROVED_RUN, 1),
    ]


def test_missing_keys_are_skipped(fake_registry):
    fake_registry.keys = {(HKEY_LOCAL_MACHINE, APPROVED_RUN): [("Only", startup.ENABLED)]}
    assert names(startup.get_startup_programs()) == ["Only"]


def test_value_reads_enabled_disabled_and_unknown(fake_registry):
    fake_registry.keys[(HKEY_CURRENT_USER, APPROVED_RUN)].append(("Other", b"\x06" + b"\x00" * 11))
    discord, spotify, other = (startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, i) for i in range(3))
    assert (discord.value(), discord.status) == (True, "Enabled")
    assert (spotify.value(), spotify.status) == (False, "Disabled")
    assert (other.value(), other.status) == (None, "Disabled")


def test_path_comes_from_run_command(fake_registry):
    discord, spotify = (startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, i) for i in range(2))
    assert discord.path == r"C:\Users\alex\AppData\Local\Discord\Update.exe"
    assert spotify.path == r"C:\Users\alex\AppData\Roaming\Spotify\Spotify.exe"


def test_path_expands_windir(fake_registry):
    health = startup.StartupProgram(HKEY_LOCAL_MACHINE, APPROVED_RUN, 0)
    assert health.path == r"C:\Windows\system32\SecurityHealthSystray.exe"


def test_command_match_ignores_case(fake_registry):
    fake_registry.keys[(HKEY_CURRENT_USER, APPROVED_RUN)][0] = ("discord", startup.ENABLED)
    program = startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, 0)
    assert program.command.endswith("--processStart Discord.exe")


def test_user_startup_folder_path(fake_registry):
    notes = startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_FOLDER, 0)
    assert notes.path == r"C:\Users\alex\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Notes.lnk"


def test_unknown_command_gives_none_path(fake_registry):
    fake_registry.keys[(HKEY_CURRENT_USER, startup.RUN_PATH)] = []
    program = startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, 0)
    assert program.command is None
    assert program.path == "None"


def test_enable_disable_toggle_write_the_same_bytes(fake_registry):
    spotify = startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, 1)
    spotify.toggle()
    assert spotify.value() is True
    spotify.toggle()
    assert spotify.value() is False
    spotify.enable()
    spotify.disable()
    assert fake_registry.writes == [
        (HKEY_CURRENT_USER, APPROVED_RUN, "Spotify", startup.ENABLED),
        (HKEY_CURRENT_USER, APPROVED_RUN, "Spotify", startup.DISABLED),
        (HKEY_CURRENT_USER, APPROVED_RUN, "Spotify", startup.ENABLED),
        (HKEY_CURRENT_USER, APPROVED_RUN, "Spotify", startup.DISABLED),
    ]


def test_registry_locations_and_bytes_are_unchanged():
    assert (HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE) == (0x80000001, 0x80000002)
    assert startup.RUN_PATH == "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
    assert startup.APPROVED_PATHS == (
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run",
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run32",
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\StartupFolder",
    )
    assert startup.ENABLED.hex() == "020000000000000000000000"
    assert startup.DISABLED.hex() == "0300000011d0b649c3aad701"


def test_all_users_startup_folder_path(fake_registry):
    backup = startup.StartupProgram(HKEY_LOCAL_MACHINE, APPROVED_FOLDER, 0)
    assert backup.path == r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\Backup.lnk"


def test_missing_run_key_leaves_command_unknown(fake_registry):
    del fake_registry.keys[(HKEY_CURRENT_USER, startup.RUN_PATH)]
    discord = startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, 0)
    assert discord.command is None
    assert discord.path == "None"
