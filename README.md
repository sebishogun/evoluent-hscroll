# Evoluent VM4 Horizontal Scroll Daemon

Adds horizontal scrolling and browser tab switching to the Evoluent VerticalMouse 4 on Linux (Wayland/Hyprland).

## Behavior

- **Quick tap** BTN_FORWARD (thumb button) → normal forward click (browser back/forward, etc.)
- **Hold BTN_FORWARD + move left/right** → horizontal scroll
- **Hold BTN_FORWARD + move left/right on browser tab bar** → switch tabs

The daemon detects whether the cursor is in the top area of a browser window and switches between horizontal scroll and tab switching automatically.

## Requirements

- Linux with `uinput` support (any modern kernel)
- Hyprland (for browser tab bar detection via `hyprctl`)
- Python 3 (system Python)
- `python-evdev` package
- Evoluent VerticalMouse 4 (vendor `0x1a7c`, product `0x0191`)

### Install python-evdev

```bash
# Arch Linux
sudo pacman -S python-evdev

# Debian/Ubuntu
sudo apt install python3-evdev

# Fedora
sudo dnf install python3-evdev

# pip (any distro)
pip install evdev
```

## Install

```bash
git clone <this-repo>
cd Evoluent
python3 install.py
```

The installer will:
- Copy the daemon and config CLI to `~/.local/bin/`
- Create a default config at `~/.config/evoluent/config.json`
- Install a systemd user service
- Install udev rules for device permissions (requires sudo)
- Add your user to the `input` group (requires sudo)

After install, **log out and back in** for group membership to take effect. The daemon starts automatically on every login.

## Uninstall

```bash
python3 uninstall.py
```

## Configuration

Config lives at `~/.config/evoluent/config.json`. Use the CLI or edit the file directly.

### Using the CLI

```bash
# View current config
evoluent-config get

# Set scroll speed multiplier (1-20, default 5)
evoluent-config set sensitivity 8

# Set accumulator threshold (1-50, default 15)
evoluent-config set threshold 10
```

Changes apply immediately — the CLI sends SIGHUP to the running daemon to hot-reload.

### Config options

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| `sensitivity` | `5` | 1-20 | Multiplier for each horizontal scroll tick. Higher = faster scrolling. |
| `accumulator_threshold` | `15` | 1-50 | Raw mouse X units to accumulate before emitting one scroll tick. Lower = more sensitive, triggers scroll with less mouse movement. |
| `tab_bar_height` | `50` | any int | Pixel height from the top of a browser window considered the "tab bar zone". Increase if tab switching doesn't trigger, decrease if it triggers too easily. |
| `acceleration` | `false` | bool | Reserved for future use. |

### Example: making scroll more sensitive

```bash
evoluent-config set sensitivity 10
evoluent-config set threshold 8
```

### Example: making scroll less sensitive

```bash
evoluent-config set sensitivity 3
evoluent-config set threshold 25
```

### Editing config directly

```bash
# Edit the file
nano ~/.config/evoluent/config.json

# Then reload the daemon (pick one):
evoluent-config get                                    # CLI auto-sends SIGHUP
systemctl --user restart evoluent-hscroll.service      # full restart
kill -SIGHUP $(pgrep -f evoluent-hscroll)              # manual SIGHUP
```

### Restarting the daemon

```bash
# Restart (e.g. after editing config manually or updating the script)
systemctl --user restart evoluent-hscroll.service

# Stop
systemctl --user stop evoluent-hscroll.service

# Start
systemctl --user start evoluent-hscroll.service

# Disable (won't start on login)
systemctl --user disable evoluent-hscroll.service

# Re-enable (starts on login)
systemctl --user enable evoluent-hscroll.service
```

## How it works

The daemon grabs the Evoluent mouse exclusively via `evdev`, creates a virtual device via `uinput` that clones all its capabilities, and forwards all events through unchanged.

When BTN_FORWARD is held and the mouse moves horizontally:
1. On the first movement, the daemon checks `hyprctl` to see if the cursor is over a browser tab bar
2. If on a tab bar: emits Ctrl+PageDown/PageUp key events to switch tabs
3. If anywhere else: converts REL_X movement into REL_HWHEEL horizontal scroll events
4. REL_Y is suppressed while held to prevent vertical jitter

If BTN_FORWARD is tapped without triggering any scroll, a normal BTN_FORWARD click is emitted on release.

### Supported browsers

Firefox, Chromium, Chrome, Brave, Zen, LibreWolf, Vivaldi, Edge, Waterfox, Thorium, Floorp.

## File locations

| File | Purpose |
|------|---------|
| `~/.local/bin/evoluent-hscroll` | Main daemon |
| `~/.local/bin/evoluent-config` | Config CLI |
| `~/.config/evoluent/config.json` | Sensitivity/threshold config |
| `~/.config/systemd/user/evoluent-hscroll.service` | Systemd user service |
| `/etc/udev/rules.d/69-evoluent.rules` | Device permission rules |

## Troubleshooting

```bash
# Check if the daemon is running
systemctl --user status evoluent-hscroll.service

# View daemon logs
journalctl --user -u evoluent-hscroll.service

# Restart the daemon
systemctl --user restart evoluent-hscroll.service

# Check if you're in the input group
groups
```

If the mouse stops responding, the daemon likely crashed while holding the grab. Unplug and replug the mouse, or switch to a TTY (`Ctrl+Alt+F2`) and run:
```bash
systemctl --user stop evoluent-hscroll.service
```
