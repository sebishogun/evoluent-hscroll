#!/usr/bin/python3
"""Installer for Evoluent VM4 horizontal scroll daemon.

Run: python3 install.py
  - Installs daemon and config CLI to ~/.local/bin/
  - Creates default config at ~/.config/evoluent/config.json
  - Installs systemd user service
  - Installs udev rules (requires sudo)
  - Adds current user to the input group (requires sudo)
  - Reloads udev rules and enables the service

After install, log out and back in for group membership to take effect,
then the daemon starts automatically on every login.
"""

import grp
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
SRC_DIR = REPO_DIR / "src"

HOME = Path.home()
BIN_DIR = HOME / ".local" / "bin"
CONFIG_DIR = HOME / ".config" / "evoluent"
SYSTEMD_DIR = HOME / ".config" / "systemd" / "user"
UDEV_DIR = Path("/etc/udev/rules.d")

FILES = {
    "daemon": {
        "src": SRC_DIR / "evoluent-hscroll",
        "dst": BIN_DIR / "evoluent-hscroll",
        "executable": True,
    },
    "config_cli": {
        "src": SRC_DIR / "evoluent-config",
        "dst": BIN_DIR / "evoluent-config",
        "executable": True,
    },
    "service": {
        "src": SRC_DIR / "evoluent-hscroll.service",
        "dst": SYSTEMD_DIR / "evoluent-hscroll.service",
        "executable": False,
    },
    "udev": {
        "src": SRC_DIR / "99-evoluent.rules",
        "dst": UDEV_DIR / "99-evoluent.rules",
        "executable": False,
        "sudo": True,
    },
}

DEFAULT_CONFIG = '{\n  "sensitivity": 5,\n  "accumulator_threshold": 15,\n  "acceleration": false\n}\n'


def run(cmd, check=True):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def check_dependency():
    try:
        import evdev  # noqa: F401
    except ImportError:
        print("ERROR: python-evdev is not installed.")
        print("Install it with: sudo pacman -S python-evdev  (Arch)")
        print("            or:  pip install evdev")
        sys.exit(1)


def install_files():
    for name, info in FILES.items():
        src = info["src"]
        dst = info["dst"]
        needs_sudo = info.get("sudo", False)

        dst.parent.mkdir(parents=True, exist_ok=True)

        if needs_sudo:
            print(f"Installing {dst} (requires sudo)")
            run(["sudo", "cp", str(src), str(dst)])
            run(["sudo", "chmod", "644", str(dst)])
        else:
            print(f"Installing {dst}")
            shutil.copy2(str(src), str(dst))

        if info["executable"] and not needs_sudo:
            dst.chmod(0o755)


def create_default_config():
    config_file = CONFIG_DIR / "config.json"
    if config_file.exists():
        print(f"Config already exists at {config_file}, skipping")
        return
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_file.write_text(DEFAULT_CONFIG)
    print(f"Created default config at {config_file}")


def ensure_input_group():
    user = os.environ.get("USER", os.getlogin())
    try:
        members = grp.getgrnam("input").gr_mem
        if user in members:
            print(f"User '{user}' is already in the 'input' group")
            return
    except KeyError:
        pass
    print(f"Adding '{user}' to 'input' group (requires sudo)")
    run(["sudo", "usermod", "-aG", "input", user])


def reload_udev():
    print("Reloading udev rules")
    run(["sudo", "udevadm", "control", "--reload-rules"])
    run(["sudo", "udevadm", "trigger"])


def enable_service():
    print("Reloading systemd user daemon")
    run(["systemctl", "--user", "daemon-reload"])
    print("Enabling evoluent-hscroll service")
    run(["systemctl", "--user", "enable", "evoluent-hscroll.service"])


def main():
    print("=== Evoluent VM4 Horizontal Scroll - Installer ===\n")

    check_dependency()
    install_files()
    create_default_config()
    ensure_input_group()
    reload_udev()
    enable_service()

    print("\n=== Installation complete ===")
    print()
    print("Next steps:")
    print("  1. Log out and log back in (for 'input' group membership)")
    print("  2. The daemon will start automatically on login")
    print()
    print("To start immediately (if group is already active):")
    print("  systemctl --user start evoluent-hscroll.service")
    print()
    print("To adjust scroll speed:")
    print("  evoluent-config set sensitivity <1-20>")
    print("  evoluent-config set threshold <1-50>")


if __name__ == "__main__":
    main()
