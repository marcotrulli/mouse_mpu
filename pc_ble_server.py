import asyncio
import json
from pynput.mouse import Controller
from bleak import BleakGATTCharacteristic, BleakGATTService, BleakServer

mouse = Controller()

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"

def on_write(characteristic: BleakGATTCharacteristic, value: bytearray):
    try:
        payload = json.loads(value.decode("utf-8"))
        dx = payload.get("dx", 0)
        dy = payload.get("dy", 0)
        mouse.move(dx, dy)
    except Exception as e:
        print("Errore lettura dati:", e)

async def run_server():
    server = BleakServer()
    service = BleakGATTService(SERVICE_UUID)
    char = BleakGATTCharacteristic(CHAR_UUID, ["write"])
    char.set_write_callback(on_write)
    service.add_characteristic(char)
    server.add_service(service)
    print("Server BLE 'PiMouseServer' avviato. In attesa dati dal Pi...")
    await server.start()
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_server())
