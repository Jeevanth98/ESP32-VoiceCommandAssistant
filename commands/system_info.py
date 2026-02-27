"""
Command: System Utilities — Hardware & Network Info
====================================================
Queries CPU usage, RAM, battery, disk, and network information
using psutil and socket.  Acts as a "System Administrator" module.
"""

from __future__ import annotations
import re
import socket
import platform


def _get_cpu_info() -> str:
    import psutil
    usage = psutil.cpu_percent(interval=1)
    freq = psutil.cpu_freq()
    cores = psutil.cpu_count(logical=True)
    info = f"CPU Usage: {usage}%  |  Cores: {cores}"
    if freq:
        info += f"  |  Frequency: {freq.current:.0f} MHz"
    return info


def _get_ram_info() -> str:
    import psutil
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)
    return f"RAM: {used_gb:.1f} GB / {total_gb:.1f} GB  ({mem.percent}% used)"


def _get_battery_info() -> str:
    import psutil
    battery = psutil.sensors_battery()
    if battery is None:
        return "Battery: Not available (desktop PC or sensor missing)"
    plugged = "Charging" if battery.power_plugged else "On battery"
    secs = battery.secsleft
    if secs == psutil.POWER_TIME_UNLIMITED:
        time_str = "∞ (plugged in)"
    elif secs == psutil.POWER_TIME_UNKNOWN:
        time_str = "unknown"
    else:
        hrs, rem = divmod(secs, 3600)
        mins = rem // 60
        time_str = f"{int(hrs)}h {int(mins)}m remaining"
    return f"Battery: {battery.percent:.0f}%  |  {plugged}  |  {time_str}"


def _get_disk_info() -> str:
    import psutil
    partitions = psutil.disk_partitions()
    lines = []
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            used_gb = usage.used / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)
            lines.append(f"  {p.device}  {used_gb:.1f} GB / {total_gb:.1f} GB  ({usage.percent}%)")
        except PermissionError:
            continue
    return "Disk:\n" + "\n".join(lines) if lines else "Disk: No accessible partitions"


def _get_network_info() -> str:
    # Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "unavailable"

    # Public IP
    try:
        import urllib.request
        public_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
    except Exception:
        public_ip = "unavailable (no internet?)"

    hostname = socket.gethostname()
    return f"Hostname: {hostname}  |  Local IP: {local_ip}  |  Public IP: {public_ip}"


def _get_all_info() -> str:
    """Return a full system dashboard."""
    sections = [
        _get_cpu_info(),
        _get_ram_info(),
        _get_battery_info(),
        _get_disk_info(),
        _get_network_info(),
        f"OS: {platform.system()} {platform.release()} ({platform.machine()})",
    ]
    return "\n".join(sections)


# ─── Keyword → handler routing ──────────────────────────────────────────────

def _detect_topic(raw_text: str) -> str:
    text = raw_text.lower()
    if re.search(r"cpu|processor|temperature", text):
        return "cpu"
    if re.search(r"ram|memory", text):
        return "ram"
    if re.search(r"batter", text):
        return "battery"
    if re.search(r"disk|storage|drive", text):
        return "disk"
    if re.search(r"ip|network|internet|hostname", text):
        return "network"
    return "all"


_TOPIC_MAP = {
    "cpu":     _get_cpu_info,
    "ram":     _get_ram_info,
    "battery": _get_battery_info,
    "disk":    _get_disk_info,
    "network": _get_network_info,
    "all":     _get_all_info,
}


def execute(raw_text: str) -> str:
    """Return system information based on what the user asked about."""
    topic = _detect_topic(raw_text)
    print(f"  [SYSTEM] Querying: {topic}")
    handler = _TOPIC_MAP[topic]
    return handler()
