import smbus
import socket
import struct
import time

MPU_ADDR = 0x68
PC_IP = "192.168.1.179"
PORT = 5005

bus = smbus.SMBus(1)

# sensibilità: più grande ? mouse più lento
SENS = 4000  

# soglia minima per eliminare micro-movimenti involontari
THRESH = 0.1  

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

while True:
    data = bus.read_i2c_block_data(MPU_ADDR, 0x43, 4)

    gx = (data[0] << 8) | data[1]
    gy = (data[2] << 8) | data[3]

    if gx > 32767: gx -= 65536
    if gy > 32767: gy -= 65536

    gx -= offset_x
    gy -= offset_y

    # calcolo movimento con sensibilità e correzione asse
    dx_f = -gy / SENS  # segno invertito per direzione corretta
    dy_f = -gx / SENS

    # applica soglia minima
    if abs(dx_f) < THRESH:
        dx_f = 0
    if abs(dy_f) < THRESH:
        dy_f = 0

    # accumulo dei delta
    acc_dx += dx_f
    acc_dy += dy_f

    # invio solo quando accumulo almeno 1 pixel
    move_x = int(acc_dx)
    move_y = int(acc_dy)

    if move_x != 0 or move_y != 0:
        packet = struct.pack("bb", move_x, move_y)
        sock.sendto(packet, (PC_IP, PORT))

        acc_dx -= move_x
        acc_dy -= move_y
