from module import Module
from messaging.module_link_server import ModuleLinkServer
from enums import HeartbeatStatus
from gpiozero import DistanceSensor
import asyncio

class UltrasonicSensor(Module):
    def __init__(self, trigger_pin=27, echo_pin=22, **kwargs):
        super().__init__(name="ultrasonic_sensor")
        self.sensor = DistanceSensor(trigger=trigger_pin, echo=echo_pin, max_distance=3)
        self._server = ModuleLinkServer(host="0.0.0.0", port=9100)
        self.running = False

    async def boot(self):
        self.set_last_function("boot")
        print("[UltrasonicSensor] Boot complete")

    async def start(self):
        self.set_last_function("start")
        await self._server.start()
        self.set_status(HeartbeatStatus.OPERATIONAL)
        self.running = True
        print("[UltrasonicSensor] Started successfully.")

    async def loop(self):
        self.set_last_function("loop")
        while self.running:
            distance = self.sensor.distance * 100
            print(f"[UltrasonicSensor] Distance: {distance:.1f} cm")
            await self._server.broadcast({
                "sensor_channel": "ultrasonic_data",
                "value": distance
            })
            await asyncio.sleep(0.5)

    async def stop(self):
        self.running = False
        await self._server.stop()
