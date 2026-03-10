import smbus
import socket
import math
import time
from collections import deque

# --- Config MPU6050 ---
MPU_ADDR = 0x68
bus = smbus.SMBus(1)
bus.write_byte_data(MPU_ADDR, 0x6B, 0)  # sveglia MPU

SENS = 131.0  # scala gyro
ALPHA = 0.96  # filtro complementare
DT = 0.01     # loop time ~10ms

# --- TCP ---
PC_IP = '192.168.1.179'  # METTI QUI IL TUO IP DEL PC
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))

# --- Accumulatori e smoothing ---
dx_queue = deque(maxlen=5)
dy_queue = deque(maxlen=5)
angle_x = 0
angle_y = 0

def read_mpu():
    # accel
    a = bus.read_i2c_block_data(MPU_ADDR, 0x3B, 6)
    ax = (a[0] << 8) | a[1]
    ay = (a[2] << 8) | a[3]
    az = (a[4] << 8) | a[5]
    if ax > 32767: ax -= 65536
    if ay > 32767: ay -= 65536
    if az > 32767: az -= 65536
    # gyro
    g = bus.read_i2c_block_data(MPU_ADDR, 0x43, 6)
    gx = (g[0] << 8) | g[1]
    gy = (g[2] << 8) | g[3]
    gz = (g[4] << 8) | g[5]
    if gx > 32767: gx -= 65536
    if gy > 32767: gy -= 65536
    if gz > 32767: gz -= 65536
    return gx, gy, gz, ax, ay, az

while True:
    gx, gy, gz, ax, ay, az = read_mpu()
    # calcolo angoli accel
    pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))
    roll  = math.atan2(ay, az)
    # filtro complementare
    angle_x = ALPHA * (angle_x + gx/ SENS * DT) + (1-ALPHA) * math.degrees(pitch)
    angle_y = ALPHA * (angle_y + gy/ SENS * DT) + (1-ALPHA) * math.degrees(roll)
    # proiezione 2D
    dx = angle_y * math.cos(pitch)
    dy = angle_x * math.cos(roll)
    # smoothing
    dx_queue.append(dx)
    dy_queue.append(dy)
    dx_f = sum(dx_queue)/len(dx_queue)
    dy_f = sum(dy_queue)/len(dy_queue)
    # invio dati separati da virgola
    data_str = f"{dx_f},{dy_f},{gx},{gy},{gz},{ax},{ay},{az}"
    sock.sendall(data_str.encode())
    time.sleep(DT)
