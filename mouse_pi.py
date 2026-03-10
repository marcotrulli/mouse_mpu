import time
import socket
from mpu_reader import MPUReader

# --- TCP PC ---
PC_IP = '192.168.1.179'
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))

# --- Parametri ---
FPS = 120
FRAME_TIME = 1 / FPS
SEND_THRESHOLD = 0.3  # invia dati solo se dx/dy > threshold
SAMPLES_AVG = 3       # media su N campioni per ridurre jitter

# --- MPU setup ---
mpu = MPUReader(alpha=0.95, deadzone=0.2, max_delta=15)

# --- Loop principale ---
last_time = time.perf_counter()

while True:
    now = time.perf_counter()
    if now - last_time >= FRAME_TIME:
        last_time = now

        dx_sum = 0
        dy_sum = 0
        # media su più campioni
        for _ in range(SAMPLES_AVG):
            data = mpu.read_filtered(FRAME_TIME / SAMPLES_AVG)
            dx_sum += data['dx']
            dy_sum += data['dy']
        
        dx = dx_sum / SAMPLES_AVG
        dy = dy_sum / SAMPLES_AVG

        # invia solo se movimento significativo
        if abs(dx) > SEND_THRESHOLD or abs(dy) > SEND_THRESHOLD:
            msg = f"{dx:.2f},{dy:.2f}\n"
            try:
                sock.sendall(msg.encode())
            except:
                pass
