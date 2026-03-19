#!/usr/bin/python3
"""Uninstaller for Evoluent VM4 horizontal scroll daemon."""

import subprocess
import sys
from pathlib import Path

HOME = Path.home()

FILES_TO_REMOVE = [
    HOME / ".local" / "bin" / "evoluent-hscroll",
    HOME / ".local" / "bin" / "evoluent-config",
    HOME / ".config" / "systemd" / "user" / "evoluent-hscroll.service",
]

SUDO_FILES = [
    Path("/etc/udev/rules.d/99-evoluent.rules"),
]


def run(cmd, check=True):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def main():
    print("=== Evoluent VM4 Horizontal Scroll - Uninstaller ===\n")

    # Stop and disable service
    print("Stopping and disabling service")
    run(["systemctl", "--user", "stop", "evoluent-hscroll.service"], check=False)
    run(["systemctl", "--user", "disable", "evoluent-hscroll.service"], check=False)

    # Remove user files
    for f in FILES_TO_REMOVE:
        if f.exists():
            f.unlink()
            print(f"Removed {f}")

    # Remove udev rules
    for f in SUDO_FILES:
        if f.exists():
            print(f"Removing {f} (requires sudo)")
            run(["sudo", "rm", str(f)])

    # Reload
    run(["systemctl", "--user", "daemon-reload"])
    run(["sudo", "udevadm", "control", "--reload-rules"], check=False)
    run(["sudo", "udevadm", "trigger"], check=False)

    print("\n=== Uninstall complete ===")
    print("Config left at ~/.config/evoluent/ (delete manually if desired)")


if __name__ == "__main__":
    main()
