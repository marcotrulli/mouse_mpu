import smbus
import socket
import struct
import time

MPU_ADDR = 0x68
PC_IP = "192.168.1.179"
PORT = 5005

bus = smbus.SMBus(1)

# sensibilità: più grande → mouse più lento
SENS = 500  

# soglia minima per eliminare micro-movimenti involontari
THRESH = 0.05  

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# wake up MPU6050
bus.write_byte_data(MPU_ADDR, 0x6B, 0)

print("Calibrazione MPU a riposo...")

offset_x = 0
offset_y = 0
samples = 200

for _ in range(samples):
    data = bus.read_i2c_block_data(MPU_ADDR, 0x43, 4)

    gx = (data[0] << 8) | data[1]
    gy = (data[2] << 8) | data[3]

    if gx > 32767: gx -= 65536
    if gy > 32767: gy -= 65536

    offset_x += gx
    offset_y += gy

    time.sleep(0.002)

offset_x /= samples
offset_y /= samples

print("Offset calcolati:", offset_x, offset_y)
print("Connessione al PC...")

# accumulatori per gestire piccoli delta
acc_dx = 0.0
acc_dy = 0.0

# buffer media mobile per stabilizzare piccoli movimenti
WINDOW = 5
dx_buffer = [0.0] * WINDOW
dy_buffer = [0.0] * WINDOW

# filtro complementare semplice
alpha = 0.98
angle_x = 0.0
angle_y = 0.0
prev_time = time.time()

while True:
    current_time = time.time()
    dt = current_time - prev_time
    prev_time = current_time

    data = bus.read_i2c_block_data(MPU_ADDR, 0x43, 4)

    gx = (data[0] << 8) | data[1]
    gy = (data[2] << 8) | data[3]

    if gx > 32767: gx -= 65536
    if gy > 32767: gy -= 65536

    gx -= offset_x
    gy -= offset_y

    # filtro complementare (solo gyro, accel opzionale se vuoi)
    angle_x = alpha * (angle_x + gx * dt)
    angle_y = alpha * (angle_y + gy * dt)

    dx_f = -angle_y / SENS
    dy_f = -angle_x / SENS

    # aggiorna buffer media mobile
    dx_buffer.append(dx_f)
    dy_buffer.append(dy_f)
    dx_buffer.pop(0)
    dy_buffer.pop(0)

    avg_dx = sum(dx_buffer) / WINDOW
    avg_dy = sum(dy_buffer) / WINDOW

    # applica soglia minima
    if abs(avg_dx) < THRESH:
        avg_dx = 0
    if abs(avg_dy) < THRESH:
        avg_dy = 0

    # accumulo per pixel
    acc_dx += avg_dx
    acc_dy += avg_dy

    move_x = int(acc_dx)
    move_y = int(acc_dy)

    if move_x != 0 or move_y != 0:
        packet = struct.pack("bb", move_x, move_y)
        sock.sendto(packet, (PC_IP, PORT))

        acc_dx -= move_x
        acc_dy -= move_y
