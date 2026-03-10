# mouse_pi.py
import time
import socket
from mpu_reader import MPUReader

# Configurazioni
PC_IP = "192.168.1.179"  # IP del PC
PORT  = 5005
SCALE_X = 500  # moltiplicatore per mouse dx
SCALE_Y = 500  # moltiplicatore per mouse dy
UPDATE_RATE = 0.01  # 100 Hz

# Inizializza sensore
sensor = MPUReader()
prev_time = time.time()

# Connessione UDP al PC
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Connesso! Invio dati MPU...")
try:
    while True:
        cur_time = time.time()
        dt = cur_time - prev_time
        prev_time = cur_time

        # Lettura MPU completa
        data = sensor.read_filtered(dt)

        # Calcolo movimento mouse 2D
        dx = data["dx"] * SCALE_X
        dy = data["dy"] * SCALE_Y

        # Threshold minimo per evitare micro-movimenti
        if abs(dx) < 0.5: dx = 0
        if abs(dy) < 0.5: dy = 0

        # Invia dati al PC
        payload = f"{dx},{dy}"
        sock.sendto(payload.encode(), (PC_IP, PORT))

        # Frequenza di aggiornamento
        time.sleep(UPDATE_RATE)

except KeyboardInterrupt:
    print("\nChiusura programma...")
    sock.close()
