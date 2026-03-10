import socket
import json
import time
from mpu_reader import MPUReader

PC_IP = "192.168.1.179"  # metti qui l’IP del PC
PC_PORT = 5005

SCALE_X = 20
SCALE_Y = 20
SEND_INTERVAL = 0.05  # 20 Hz

sensor = MPUReader()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"Connessione al PC {PC_IP}:{PC_PORT} ...")
    s.connect((PC_IP, PC_PORT))
    print("Connesso! Invio dati MPU...")
    try:
        while True:
            data = sensor.read_filtered()
            payload = {"dx": data["ax"] * SCALE_X, "dy": data["ay"] * SCALE_Y}
            s.sendall((json.dumps(payload) + "\n").encode())
            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        print("Chiusura...")
