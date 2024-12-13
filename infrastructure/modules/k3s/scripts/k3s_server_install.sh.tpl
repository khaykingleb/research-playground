#!/bin/bash
set -e

curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="${k3s_version}" sh -s - server \
    %{if is_main_node == true} \
    --cluster-init \
    %{else} \
    --token "${k3s_token}" \
    --server "https://${tailscale_k3s_main_server_ip}:6443" \
    %{endif} \
    --tls-san "${tailscale_k3s_main_server_ip}" \
    --tls-san "${k3s_server_main_ip}" \
    --vpn-auth "name=tailscale,joinKey=${tailscale_auth_key}" \
    --node-external-ip "${tailscale_k3s_server_ip}"