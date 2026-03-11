# visual_3d_mpu.py
import smbus2
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# MPU6050 registers
MPU_ADDR = 0x68
REG_PWR_MGMT_1 = 0x6B
REG_ACCEL_XOUT_H = 0x3B

# Inizializza bus I2C
bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, REG_PWR_MGMT_1, 0)  # sveglia il sensore

def read_accel():
    data = bus.read_i2c_block_data(MPU_ADDR, REG_ACCEL_XOUT_H, 6)
    x = (data[0] << 8) | data[1]
    y = (data[2] << 8) | data[3]
    z = (data[4] << 8) | data[5]
    x = x - 65536 if x > 32767 else x
    y = y - 65536 if y > 32767 else y
    z = z - 65536 if z > 32767 else z
    return x, y, z

# Setup grafico 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-17000, 17000])
ax.set_ylim([-17000, 17000])
ax.set_zlim([-17000, 17000])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
quiver = ax.quiver(0, 0, 0, 0, 0, 0, length=1)

plt.ion()
plt.show()

try:
    while True:
        x, y, z = read_accel()
        ax.cla()
        ax.set_xlim([-17000, 17000])
        ax.set_ylim([-17000, 17000])
        ax.set_zlim([-17000, 17000])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.quiver(0, 0, 0, x, y, z, length=1, color='r')
        plt.draw()
        plt.pause(0.05)
except KeyboardInterrupt:
    print("Chiusura...")
    plt.close()
