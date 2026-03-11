import time
from mpu6050 import mpu6050
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Inizializza sensore
sensor = mpu6050(0x68)

# Setup grafico 3D
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(-180, 180)
ax.set_ylim(-180, 180)
ax.set_zlim(-180, 180)
ax.set_xlabel('X (Pitch)')
ax.set_ylabel('Y (Roll)')
ax.set_zlabel('Z (Yaw)')

point, = ax.plot([0], [0], [0], 'ro', markersize=8)

print("Muovi solo l'asse che vuoi osservare e premi CTRL+C per fermare")

try:
    while True:
        accel = sensor.get_accel_data()
        gyro = sensor.get_gyro_data()

        # Angoli in gradi (roll/pitch/yaw)
        pitch = gyro['x']  # asse X = Pitch
        roll  = gyro['y']  # asse Y = Roll
        yaw   = gyro['z']  # asse Z = Yaw

        # Aggiorna punto sul grafico
        point.set_data([pitch], [roll])
        point.set_3d_properties([yaw])
        plt.draw()
        plt.pause(0.01)

except KeyboardInterrupt:
    print("Calibrazione visualizzazione terminata.")
