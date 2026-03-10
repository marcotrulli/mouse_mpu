import bluetooth
import json
import time
from config import PC_MAC, PORT, SCALE_X, SCALE_Y, SEND_INTERVAL
from utils.mpu_reader import MPUReader

def main():
    sensor = MPUReader()
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    
    print(f"Connessione a {PC_MAC} sulla porta {PORT}...")
    sock.connect((PC_MAC, PORT))
    print("Connesso! Inizio invio dati...")

    try:
        while True:
            data = sensor.read_filtered()
            # scala i valori prima di inviare
            payload = {
                "dx": data["ax"] * SCALE_X,
                "dy": data["ay"] * SCALE_Y
            }
            sock.send(json.dumps(payload))
            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        print("Chiusura...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
