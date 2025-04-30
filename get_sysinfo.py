#!/usr/bin/env python3

import socket
import os
import platform

def get_ip_address():
    """Get the LAN IP address (non-loopback)."""
    try:
        # Connect to an external host, doesn't send packets but gets correct interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'  # fallback if disconnected

def main():
    hostname = platform.node()
    ip_address = get_ip_address()
    cwd = os.getcwd()

    # Infer agent.py and config path based on current directory
    agent_path = os.path.join(cwd, "src", "agent.py")
    config_path = os.path.join(cwd, "catdog_test.yaml")

    print(f"  {hostname}:")
    print(f"    ip: {ip_address}")
    print(f"    agent_path: {agent_path}")
    print(f"    config_path: {config_path}")

if __name__ == "__main__":
    main()
