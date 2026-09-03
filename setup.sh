#!/usr/bin/env bash
set -euo pipefail

echo "=== Evoluent VM4 Horizontal Scroll Setup ==="

# Create udev rules
echo "Creating udev rules..."
sudo tee /etc/udev/rules.d/69-evoluent.rules > /dev/null <<'EOF'
SUBSYSTEM=="input", ATTRS{idVendor}=="1a7c", ATTRS{idProduct}=="0191", MODE="0660", GROUP="input", TAG+="uaccess"
KERNEL=="uinput", MODE="0660", GROUP="input", TAG+="uaccess"
EOF

# Add user to input group
echo "Adding $USER to input group..."
sudo usermod -aG input "$USER"

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules && sudo udevadm trigger

echo ""
echo "=== Done ==="
echo "Next steps:"
echo "  1. Log out and log back in (for group membership to take effect)"
echo "  2. Run: systemctl --user enable --now evoluent-hscroll.service"
