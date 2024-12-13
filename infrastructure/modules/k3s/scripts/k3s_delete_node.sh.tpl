#!/bin/bash
set -e

# Uninstall k3s agent
/usr/local/bin/k3s-agent-uninstall.sh

# Delete node from k3s cluster
echo "${kube_client_certificate}" > /tmp/client.crt \
    && echo "${kube_client_key}" > /tmp/client.key \
    && echo "${kube_cluster_ca_certificate}" > /tmp/ca.crt

curl -X DELETE \
    --cert /tmp/client.crt \
    --key /tmp/client.key \
    --cacert /tmp/ca.crt \
    "${kube_api_server}/api/v1/nodes/${k3s_agent_node_name}"

rm -f /tmp/client.crt /tmp/client.key /tmp/ca.crt
