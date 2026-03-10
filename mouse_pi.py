import smbus
import math
import socket
import time

# MPU6050 Registers
MPU_ADDR = 0x68
bus = smbus.SMBus(1)

# Inizializza MPU6050
bus.write_byte_data(MPU_ADDR, 0x6B, 0)

# TCP PC
PC_IP = '192.168.1.179'  # indirizzo IP del PC
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))

# Parametri filtro
ALPHA = 0.98
SENS = 131.0
dt = 0.01
angle_x = 0
angle_y = 0

def read_mpu():
    # Accelerometro
    accel = bus.read_i2c_block_data(MPU_ADDR, 0x3B, 6)
    ax = (accel[0] << 8 | accel[1])
    ay = (accel[2] << 8 | accel[3])
    az = (accel[4] << 8 | accel[5])
    for v in [ax, ay, az]:
        if v > 32767: v -= 65536

    # Gyro
    gyro = bus.read_i2c_block_data(MPU_ADDR, 0x43, 6)
    gx = (gyro[0] << 8 | gyro[1])
    gy = (gyro[2] << 8 | gyro[3])
    gz = (gyro[4] << 8 | gyro[5])
    for v in [gx, gy, gz]:
        if v > 32767: v -= 65536

    return ax, ay, az, gx, gy, gz

def calc_mouse(ax, ay, az, gx, gy, gz):
    global angle_x, angle_y
    # Angoli accelerometro
    pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))
    roll  = math.atan2(ay, az)

    # Filtro complementare gyro+accel
    angle_x = ALPHA*(angle_x + gx/SENS*dt) + (1-ALPHA)*math.degrees(pitch)
    angle_y = ALPHA*(angle_y + gy/SENS*dt) + (1-ALPHA)*math.degrees(roll)

    # Delta mouse proiettato su piano 2D
    dx = angle_y * math.cos(pitch)
    dy = angle_x * math.cos(roll)

    # Limite sensibilità
    dx = max(min(dx, 20), -20)
    dy = max(min(dy, 20), -20)

    return dx, dy

while True:
    ax, ay, az, gx, gy, gz = read_mpu()
    dx, dy = calc_mouse(ax, ay, az, gx, gy, gz)
    # Invia dati al PC
    msg = f"{dx:.2f},{dy:.2f},{gx:.2f},{gy:.2f},{gz:.2f},{ax:.2f},{ay:.2f},{az:.2f}"
    try:
        sock.sendall(msg.encode())
    except:
        pass
    time.sleep(dt)
