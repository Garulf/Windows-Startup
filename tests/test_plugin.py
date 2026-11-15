import asyncio
import json
from pathlib import Path

import shell
import startup
import windows_startup
from conftest import APPROVED_RUN
from registry import HKEY_CURRENT_USER

ROOT = Path(__file__).resolve().parents[1]
SPOTIFY = [str(HKEY_CURRENT_USER), APPROVED_RUN, "1"]


def call(method, *parameters):
    return asyncio.run(windows_startup.plugin._event_handler.trigger_event(method, *parameters))


def titles(response):
    return [result["Title"] for result in response["Result"]]


def test_query_lists_every_program_without_search(fake_registry):
    assert titles(call("query", "")) == ["Discord", "Spotify", "Notes", "SecurityHealth", "Backup"]


def test_query_filters_by_name_ignoring_case(fake_registry):
    assert titles(call("query", "SPOT")) == ["Spotify"]


def test_query_result_toggles_and_carries_context(fake_registry):
    discord, spotify = call("query", "")["Result"][:2]
    assert discord["SubTitle"] == "✔️Enabled - Press ENTER to toggle program startup behavior"
    assert spotify["SubTitle"] == "❌Disabled"
    assert spotify["IcoPath"] == r"C:\Users\alex\AppData\Roaming\Spotify\Spotify.exe"
    assert spotify["JsonRPCAction"] == {"Method": "toggle", "Parameters": SPOTIFY, "DontHideAfterAction": False}
    assert spotify["ContextData"] == SPOTIFY
    json.dumps(spotify)


def test_context_menu_offers_open_reveal_enable_disable(fake_registry):
    response = call("context_menu", SPOTIFY)
    assert titles(response) == ["Open Program", "Reveal in Explorer", "Enable Program", "Disable Program"]
    open_program, reveal, enable, disable = response["Result"]
    path = r"C:\Users\alex\AppData\Roaming\Spotify\Spotify.exe"
    assert open_program["JsonRPCAction"]["Method"] == "open_program"
    assert open_program["JsonRPCAction"]["Parameters"] == [path]
    assert reveal["JsonRPCAction"]["Method"] == "reveal_in_finder"
    assert reveal["IcoPath"] == r"C:\Windows\explorer.exe"
    assert enable["JsonRPCAction"]["Parameters"] == SPOTIFY
    assert disable["JsonRPCAction"]["Method"] == "disable"
    assert Path(enable["IcoPath"]).is_file() and Path(disable["IcoPath"]).is_file()


def test_toggle_shows_new_state(fake_registry):
    command = call("toggle", *SPOTIFY)
    assert command == {
        "Method": "Flow.Launcher.ShowMsg",
        "Parameters": ["Windows Startup: Enabled!", "Spotify start-up is Enabled", windows_startup.ICON],
    }
    assert startup.StartupProgram(HKEY_CURRENT_USER, APPROVED_RUN, 1).value() is True


def test_enable_when_already_enabled_reports_error(fake_registry):
    command = call("enable", str(HKEY_CURRENT_USER), APPROVED_RUN, "0")
    assert command["Parameters"][:2] == ["Windows Startup: ERROR!", "Unable to change Discord to Enabled!"]


def test_disable_writes_disabled_bytes(fake_registry):
    call("disable", str(HKEY_CURRENT_USER), APPROVED_RUN, "0")
    assert fake_registry.writes == [(HKEY_CURRENT_USER, APPROVED_RUN, "Discord", startup.DISABLED)]


def test_open_and_reveal_use_the_shell(monkeypatch):
    calls = []
    monkeypatch.setattr(shell, "open_file", lambda path: calls.append(("open", path)))
    monkeypatch.setattr(shell, "reveal_in_explorer", lambda path: calls.append(("reveal", path)))
    call("open_program", r"C:\Apps\app.exe")
    call("reveal_in_finder", r"C:\Apps\app.exe")
    assert calls == [("open", r"C:\Apps\app.exe"), ("reveal", r"C:\Apps\app.exe")]


def test_reveal_runs_explorer_select(monkeypatch):
    commands = []
    monkeypatch.setattr(shell.subprocess, "Popen", commands.append)
    shell.reveal_in_explorer(r"C:\Apps\app.exe")
    assert commands == [r"explorer /select,C:\Apps\app.exe"]


def test_manifest_keeps_id_keyword_and_runtime():
    manifest = json.loads((ROOT / "data" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["ID"] == "747F1A93B6D24CCFBC433BA2455B3BEA"
    assert manifest["ActionKeyword"] == "wst"
    assert manifest["Name"] == windows_startup.PLUGIN_NAME
    assert manifest["Language"] == "python_v2"
    assert (ROOT / "data" / manifest["IcoPath"]).is_file()
