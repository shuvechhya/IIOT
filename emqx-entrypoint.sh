#!/bin/sh
# Start EMQX in the background
emqx start

# Wait until EMQX node is ready
until emqx_ctl status >/dev/null 2>&1; do
    echo "Waiting for EMQX node to start..."
    sleep 2
done

# Add dashboard admin user (ignore if it already exists)
emqx_ctl admins add admin public123 || true

# Keep container running
tail -f /dev/null
