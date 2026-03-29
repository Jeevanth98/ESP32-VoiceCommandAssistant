"""
Tests for command handler logic
==================================
Tests the pure-logic portions of command handlers that can be
unit-tested without side effects (no GUI, no file I/O, no subprocess).
"""

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# Timer — duration parsing & formatting
# ═══════════════════════════════════════════════════════════════════════════════

from commands.timer import _parse_duration, _format_duration


class TestTimerParsing:
    def test_minutes(self):
        assert _parse_duration("5 minutes") == 300

    def test_seconds(self):
        assert _parse_duration("30 seconds") == 30

    def test_hours(self):
        assert _parse_duration("1 hour") == 3600

    def test_combined(self):
        assert _parse_duration("1 hour 30 minutes") == 5400

    def test_abbreviated(self):
        assert _parse_duration("10 min") == 600

    def test_abbreviated_sec(self):
        assert _parse_duration("45 sec") == 45

    def test_bare_number_assumes_minutes(self):
        assert _parse_duration("10") == 600

    def test_no_duration_returns_none(self):
        assert _parse_duration("hello world") is None

    def test_zero_returns_none(self):
        assert _parse_duration("0 minutes") is None


class TestTimerFormatting:
    def test_seconds_only(self):
        assert _format_duration(30) == "30s"

    def test_minutes_only(self):
        assert _format_duration(300) == "5m"

    def test_hours_only(self):
        assert _format_duration(3600) == "1h"

    def test_combined(self):
        assert _format_duration(5430) == "1h 30m 30s"

    def test_zero(self):
        assert _format_duration(0) == "0s"


# ═══════════════════════════════════════════════════════════════════════════════
# Open App — app name extraction & resolution
# ═══════════════════════════════════════════════════════════════════════════════

from commands.open_app import extract_app_name, _resolve_app, _normalise


class TestOpenAppExtraction:
    def test_open_chrome(self):
        assert extract_app_name("open chrome").lower() == "chrome"

    def test_launch_firefox(self):
        assert extract_app_name("launch Firefox").lower() == "firefox"

    def test_fire_up_spotify(self):
        name = extract_app_name("fire up Spotify")
        assert "spotify" in name.lower()

    def test_fallback(self):
        assert extract_app_name("chrome") == "chrome"


class TestAppResolution:
    def test_exact_match(self):
        result = _resolve_app("chrome")
        assert result is not None
        assert result[1] == "Google Chrome"

    def test_case_insensitive(self):
        result = _resolve_app("Chrome")
        assert result is not None

    def test_unknown_app(self):
        result = _resolve_app("zzz_unknown_zzz")
        assert result is None

    def test_normalise_strips_articles(self):
        result = _normalise("the Chrome app")
        assert "chrome" in result
        assert "the" not in result
        assert "app" not in result


# ═══════════════════════════════════════════════════════════════════════════════
# Close App — app name extraction
# ═══════════════════════════════════════════════════════════════════════════════

from commands.close_app import extract_app_name as close_extract_app_name


class TestCloseAppExtraction:
    def test_close_chrome(self):
        assert close_extract_app_name("close chrome").lower() == "chrome"

    def test_quit_notepad(self):
        assert close_extract_app_name("quit notepad").lower() == "notepad"

    def test_terminate_discord(self):
        assert close_extract_app_name("terminate Discord").lower() == "discord"


# ═══════════════════════════════════════════════════════════════════════════════
# Web Search — query extraction
# ═══════════════════════════════════════════════════════════════════════════════

from commands.web_search import extract_query


class TestWebSearchExtraction:
    def test_search_query(self):
        result = extract_query("search what is a lion")
        assert "lion" in result.lower()

    def test_google_query(self):
        result = extract_query("google how to make pasta")
        assert "pasta" in result.lower()

    def test_what_is(self):
        result = extract_query("what is photosynthesis")
        assert "photosynthesis" in result.lower()

    def test_plain_fallback(self):
        result = extract_query("quantum physics")
        assert result == "quantum physics"


# ═══════════════════════════════════════════════════════════════════════════════
# GUI Control — action detection
# ═══════════════════════════════════════════════════════════════════════════════

from commands.gui_control import _detect_action


class TestGuiControlDetection:
    def test_scroll_down(self):
        assert _detect_action("scroll down") == "scroll_down"

    def test_scroll_up(self):
        assert _detect_action("scroll up") == "scroll_up"

    def test_play(self):
        assert _detect_action("play music") == "play"

    def test_pause(self):
        assert _detect_action("pause the video") == "pause"

    def test_volume_up(self):
        assert _detect_action("volume up") == "volume_up"

    def test_volume_down(self):
        assert _detect_action("volume down") == "volume_down"

    def test_mute(self):
        assert _detect_action("mute the audio") == "mute"

    def test_fullscreen(self):
        assert _detect_action("fullscreen") == "fullscreen"

    def test_unknown(self):
        assert _detect_action("banana") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Create File — command parsing
# ═══════════════════════════════════════════════════════════════════════════════

from commands.create_file import _parse_command, _resolve_extension, _resolve_folder


class TestCreateFileParsing:
    def test_full_pattern(self):
        result = _parse_command("create a python file called notes in Desktop")
        assert result is not None
        name, ext, folder = result
        assert name == "notes"
        assert ext == ".py"
        assert "Desktop" in folder

    def test_explicit_extension(self):
        result = _parse_command("create notes.py in Documents")
        assert result is not None
        name, ext, _ = result
        assert name == "notes"
        assert ext == ".py"

    def test_no_folder_defaults(self):
        result = _parse_command("create a python file called utils")
        assert result is not None
        name, ext, folder = result
        assert name == "utils"
        assert ext == ".py"

    def test_unparseable_returns_none(self):
        result = _parse_command("hello world")
        assert result is None


class TestResolveExtension:
    def test_python(self):
        assert _resolve_extension("python") == ".py"

    def test_text(self):
        assert _resolve_extension("text") == ".txt"

    def test_javascript(self):
        assert _resolve_extension("javascript") == ".js"

    def test_unknown(self):
        assert _resolve_extension("banana") is None


class TestResolveFolder:
    def test_desktop_alias(self):
        result = _resolve_folder("Desktop")
        assert "Desktop" in result

    def test_documents_alias(self):
        result = _resolve_folder("Documents")
        assert "Documents" in result

    def test_downloads_alias(self):
        result = _resolve_folder("Downloads")
        assert "Downloads" in result


# ═══════════════════════════════════════════════════════════════════════════════
# System Power — action detection
# ═══════════════════════════════════════════════════════════════════════════════

from commands.system_power import _detect_action as detect_power_action


class TestSystemPowerDetection:
    def test_lock(self):
        assert detect_power_action("lock the screen") == "lock"

    def test_shutdown(self):
        assert detect_power_action("shut down the computer") == "shutdown"

    def test_restart(self):
        assert detect_power_action("restart my pc") == "restart"

    def test_sleep(self):
        assert detect_power_action("go to sleep") == "sleep"

    def test_logoff(self):
        assert detect_power_action("log off") == "logoff"

    def test_unknown(self):
        assert detect_power_action("hello world") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Brightness — command parsing
# ═══════════════════════════════════════════════════════════════════════════════

from commands.brightness import _parse_command as parse_brightness


class TestBrightnessParsing:
    def test_set_absolute(self):
        action, value = parse_brightness("set brightness to 70")
        assert action == "set"
        assert value == 70

    def test_increase(self):
        action, value = parse_brightness("increase brightness")
        assert action == "up"

    def test_decrease(self):
        action, value = parse_brightness("decrease brightness")
        assert action == "down"

    def test_query(self):
        action, value = parse_brightness("what is my brightness")
        assert action == "get"


# ═══════════════════════════════════════════════════════════════════════════════
# Window Management — action detection
# ═══════════════════════════════════════════════════════════════════════════════

from commands.window_mgmt import _detect_action as detect_window_action


class TestWindowMgmtDetection:
    def test_minimize(self):
        assert detect_window_action("minimize this window") == "minimize"

    def test_maximize(self):
        assert detect_window_action("maximize the window") == "maximize"

    def test_snap_left(self):
        assert detect_window_action("snap to the left") == "snap_left"

    def test_snap_right(self):
        assert detect_window_action("snap right") == "snap_right"

    def test_show_desktop(self):
        assert detect_window_action("show desktop") == "minimize_all"

    def test_minimize_all(self):
        assert detect_window_action("minimize all") == "minimize_all"

    def test_task_view(self):
        assert detect_window_action("task view") == "task_view"

    def test_unknown(self):
        assert detect_window_action("banana") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Open URL — URL extraction
# ═══════════════════════════════════════════════════════════════════════════════

from commands.open_url import _extract_url


class TestOpenUrlExtraction:
    def test_domain(self):
        url = _extract_url("open youtube.com")
        assert url == "https://youtube.com"

    def test_full_url(self):
        url = _extract_url("go to https://github.com")
        assert url == "https://github.com"

    def test_shortcut(self):
        url = _extract_url("open youtube")
        assert url == "https://www.youtube.com"

    def test_no_url(self):
        url = _extract_url("hello world")
        assert url is None


# ═══════════════════════════════════════════════════════════════════════════════
# System Info — topic detection
# ═══════════════════════════════════════════════════════════════════════════════

from commands.system_info import _detect_topic


class TestSystemInfoDetection:
    def test_cpu(self):
        assert _detect_topic("what is my CPU usage") == "cpu"

    def test_ram(self):
        assert _detect_topic("how much RAM is being used") == "ram"

    def test_battery(self):
        assert _detect_topic("check battery percentage") == "battery"

    def test_disk(self):
        assert _detect_topic("show disk space") == "disk"

    def test_network(self):
        assert _detect_topic("what is my IP address") == "network"

    def test_default_all(self):
        assert _detect_topic("system information") == "all"
