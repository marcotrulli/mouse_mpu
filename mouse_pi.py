import smbus
import socket
import struct
import time
import math
from collections import deque

# --- MPU6050 setup ---
MPU_ADDR = 0x68
bus = smbus.SMBus(1)

# wake up MPU6050
bus.write_byte_data(MPU_ADDR, 0x6B, 0)

# --- TCP setup ---
PC_IP = '192.168.1.179'  # IP del PC
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))

# --- Filter / smoothing setup ---
alpha = 0.98
dt = 0.01  # intervallo di lettura stimato 10ms
dx_buffer = deque(maxlen=5)
dy_buffer = deque(maxlen=5)
N = 5  # lunghezza media mobile

# --- Calibrazione offset ---
print("Calibrazione MPU a riposo...")
gx_off = gy_off = gz_off = 0
ax_off = ay_off = az_off = 0
samples = 100
for _ in range(samples):
    accel_data = bus.read_i2c_block_data(MPU_ADDR, 0x3B, 6)
    gyro_data = bus.read_i2c_block_data(MPU_ADDR, 0x43, 6)

    ax = (accel_data[0] << 8 | accel_data[1])
    ay = (accel_data[2] << 8 | accel_data[3])
    az = (accel_data[4] << 8 | accel_data[5])
    gx = (gyro_data[0] << 8 | gyro_data[1])
    gy = (gyro_data[2] << 8 | gyro_data[3])
    gz = (gyro_data[4] << 8 | gyro_data[5])

    if ax > 32767: ax -= 65536
    if ay > 32767: ay -= 65536
    if az > 32767: az -= 65536
    if gx > 32767: gx -= 65536
    if gy > 32767: gy -= 65536
    if gz > 32767: gz -= 65536

    gx_off += gx
    gy_off += gy
    gz_off += gz
    ax_off += ax
    ay_off += ay
    az_off += az

gx_off /= samples
gy_off /= samples
gz_off /= samples
ax_off /= samples
ay_off /= samples
az_off /= samples
print("Offset calcolati: gx={:.2f}, gy={:.2f}, gz={:.2f}".format(gx_off, gy_off, gz_off))

# --- Main loop ---
angle_x = 0
angle_y = 0

while True:
    try:
        # leggi sensore
        accel_data = bus.read_i2c_block_data(MPU_ADDR, 0x3B, 6)
        gyro_data = bus.read_i2c_block_data(MPU_ADDR, 0x43, 6)

        ax = (accel_data[0] << 8 | accel_data[1])
        ay = (accel_data[2] << 8 | accel_data[3])
        az = (accel_data[4] << 8 | accel_data[5])
        gx = (gyro_data[0] << 8 | gyro_data[1])
        gy = (gyro_data[2] << 8 | gyro_data[3])
        gz = (gyro_data[4] << 8 | gyro_data[5])

        if ax > 32767: ax -= 65536
        if ay > 32767: ay -= 65536
        if az > 32767: az -= 65536
        if gx > 32767: gx -= 65536
        if gy > 32767: gy -= 65536
        if gz > 32767: gz -= 65536

        # sottrai offset
        gx -= gx_off
        gy -= gy_off
        gz -= gz_off
        ax -= ax_off
        ay -= ay_off
        az -= az_off

        # calcola pitch/roll
        pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))
        roll  = math.atan2(ay, az)

        # filtro complementare
        angle_x = alpha * (angle_x + gx*dt) + (1-alpha) * math.degrees(pitch)
        angle_y = alpha * (angle_y + gy*dt) + (1-alpha) * math.degrees(roll)

        # proiezione su 2D
        dx = angle_y * math.cos(pitch)
        dy = angle_x * math.cos(roll)

        # media mobile e soglia minima
        dx_buffer.append(dx)
        dy_buffer.append(dy)
        dx_smooth = sum(dx_buffer)/len(dx_buffer)
        dy_smooth = sum(dy_buffer)/len(dy_buffer)
        if abs(dx_smooth) < 0.2: dx_smooth = 0
        if abs(dy_smooth) < 0.2: dy_smooth = 0

        # invio dati al PC
        message = f"{dx_smooth:.2f},{dy_smooth:.2f},{gx:.2f},{gy:.2f},{gz:.2f},{ax:.2f},{ay:.2f},{az:.2f}"
        sock.sendall(message.encode())

        time.sleep(dt)

    except Exception as e:
        print("Errore:", e)
        time.sleep(0.05)
