import asyncio
import json
from bleak import BleakScanner, BleakClient
from utils.mpu_reader import MPUReader

SCALE_X = 20
SCALE_Y = 20
SEND_INTERVAL = 0.05
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"
TARGET_NAME = "PiMouseServer"

async def find_pc():
    print("Scansione dispositivi BLE...")
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == TARGET_NAME:
            print(f"Trovato PC: {d.name}, MAC: {d.address}")
            return d.address
    return None

async def main():
    sensor = MPUReader()
    pc_mac = await find_pc()
    if not pc_mac:
        print("PC non trovato! Assicurati che il server BLE sia avviato.")
        return

    async with BleakClient(pc_mac) as client:
        print("Connesso al PC. Inizio invio dati...")
        try:
            while True:
                data = sensor.read_filtered()
                payload = {"dx": data["ax"] * SCALE_X, "dy": data["ay"] * SCALE_Y}
                await client.write_gatt_char(CHAR_UUID, json.dumps(payload).encode("utf-8"))
                await asyncio.sleep(SEND_INTERVAL)
        except KeyboardInterrupt:
            print("Chiusura...")

if __name__ == "__main__":
    asyncio.run(main())
