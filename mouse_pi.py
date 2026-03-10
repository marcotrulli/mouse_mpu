import time
import socket
from mpu_reader import MPUReader

PC_IP = "192.168.1.179"  # cambia con IP PC
PORT = 5005
SCALE_X = 500
SCALE_Y = 500
UPDATE_RATE = 0.01  # 100Hz

sensor = MPUReader()
prev_time = time.time()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))
print("Connesso al PC!")

try:
    while True:
        cur_time = time.time()
        dt = cur_time - prev_time
        prev_time = cur_time

        data = sensor.read_filtered(dt)

        dx = data["dx"] * SCALE_X
        dy = data["dy"] * SCALE_Y
        if abs(dx) < 0.5: dx = 0
        if abs(dy) < 0.5: dy = 0

        # Invia con \n come separatore di pacchetto
        payload = "{dx},{dy},{gx},{gy},{gz},{ax},{ay},{az}\n".format(**data)
        sock.send(payload.encode())

        time.sleep(UPDATE_RATE)

except KeyboardInterrupt:
    print("\nChiusura programma...")
    sock.close()
