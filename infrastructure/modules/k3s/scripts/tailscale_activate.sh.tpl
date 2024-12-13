#!/bin/bash
set -e

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Use a normal ASCII dash in the following lines
sudo tailscale up \
  --auth-key="${tailscale_auth_key}" \
  --accept-routes \
  --reset

# Save the Tailscale IP to a temporary file
sudo tailscale ip -4 | sudo tee /usr/local/share/tailscale_ip.txt
