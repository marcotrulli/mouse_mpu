import smbus
import socket
import struct
import time

MPU_ADDR = 0x68
PC_IP = "192.168.1.179"
PORT = 5005

bus = smbus.SMBus(1)

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

    if gx > 32767:
        gx -= 65536
    if gy > 32767:
        gy -= 65536

    offset_x += gx
    offset_y += gy

    time.sleep(0.002)

offset_x /= samples
offset_y /= samples

print("Offset calcolati:", offset_x, offset_y)

print("Connessione al PC...")

while True:

    data = bus.read_i2c_block_data(MPU_ADDR, 0x43, 4)

    gx = (data[0] << 8) | data[1]
    gy = (data[2] << 8) | data[3]

    if gx > 32767:
        gx -= 65536
    if gy > 32767:
        gy -= 65536

    gx -= offset_x
    gy -= offset_y

    dx = int(gy / 1000)    #  /a con più a è grande più la sensibilità del mouse è bassa 
    dy = int(gx / 1000)

    packet = struct.pack("bb", dx, dy)

    sock.sendto(packet, (PC_IP, PORT))
