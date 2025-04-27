import asyncio
import socket
import json
import time

class VibeSender:
    def __init__(self, device_name, get_health_callback, port=30303, interval=5):
        self.device_name = device_name
        self.get_health_callback = get_health_callback
        self.port = port
        self.interval = interval
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    async def start(self):
        while True:
            vibe = {
                "device_name": self.device_name,
                "timestamp": time.time(),
                "health": self.get_health_callback(),
                "uptime": time.time() - self.get_health_callback().get('start_time', time.time())
            }
            message = json.dumps(vibe).encode('utf-8')
            self.sock.sendto(message, ('<broadcast>', self.port))
            await asyncio.sleep(self.interval)


class VibeListener:
    def __init__(self, port=30303):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.vibe_map = {}  # { device_name: last_vibe_dict }

    async def start(self):
        while True:
            data, addr = self.sock.recvfrom(4096)
            try:
                vibe = json.loads(data.decode('utf-8'))
                device_name = vibe.get("device_name", "unknown")
                self.vibe_map[device_name] = vibe
                self.print_vibe_map()
            except Exception as e:
                print(f"[VibeListener] Failed to decode vibe: {e}")

    def print_vibe_map(self):
        print("\n[VibeListener] Current Vibe Map:")
        for device, vibe in self.vibe_map.items():
            print(f"- {device}: {vibe['health']} (uptime: {vibe['uptime']:.1f}s)")
