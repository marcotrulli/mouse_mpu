import smbus
import math
import socket
import time

# --- MPU6050 Setup ---
MPU_ADDR = 0x68
bus = smbus.SMBus(1)
bus.write_byte_data(MPU_ADDR, 0x6B, 0)  # wake up

# --- TCP PC ---
PC_IP = '192.168.1.179'  # sostituisci con IP del tuo PC
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))

# --- Parametri filtro e sensibilità ---
ALPHA = 0.98
SENS = 131.0
dt = 0.01
angle_x = 0
angle_y = 0

# --- Lettura sensore ---
def read_mpu():
    accel = bus.read_i2c_block_data(MPU_ADDR, 0x3B, 6)
    ax = (accel[0] << 8 | accel[1])
    ay = (accel[2] << 8 | accel[3])
    az = (accel[4] << 8 | accel[5])
    if ax > 32767: ax -= 65536
    if ay > 32767: ay -= 65536
    if az > 32767: az -= 65536

    gyro = bus.read_i2c_block_data(MPU_ADDR, 0x43, 6)
    gx = (gyro[0] << 8 | gyro[1])
    gy = (gyro[2] << 8 | gyro[3])
    gz = (gyro[4] << 8 | gyro[5])
    if gx > 32767: gx -= 65536
    if gy > 32767: gy -= 65536
    if gz > 32767: gz -= 65536

    return ax, ay, az, gx, gy, gz

# --- Calcolo movimento mouse ---
def calc_mouse(ax, ay, az, gx, gy, gz):
    global angle_x, angle_y
    pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))
    roll  = math.atan2(ay, az)

    # Filtro complementare
    angle_x = ALPHA*(angle_x + gx/SENS*dt) + (1-ALPHA)*math.degrees(pitch)
    angle_y = ALPHA*(angle_y + gy/SENS*dt) + (1-ALPHA)*math.degrees(roll)

    # Movimento mouse proporzionale e limitato
    dx = max(min(angle_y*0.5, 20), -20)
    dy = max(min(angle_x*0.5, 20), -20)
    return dx, dy

# --- Loop principale ---
while True:
    ax, ay, az, gx, gy, gz = read_mpu()
    dx, dy = calc_mouse(ax, ay, az, gx, gy, gz)
    msg = f"{dx:.2f},{dy:.2f}\n"
    try:
        sock.sendall(msg.encode())
    except:
        pass
    time.sleep(dt)
