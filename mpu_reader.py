# mpu_reader.py
from mpu6050 import mpu6050
import math
import time

class MPUReader:
    def __init__(self, address=0x68, alpha=0.98):
        self.sensor = mpu6050(address)
        self.alpha = alpha
        self.angle_x = 0.0
        self.angle_y = 0.0

    def read_filtered(self, dt):
        # Legge accelerometro e gyro
        accel = self.sensor.get_accel_data()
        gyro  = self.sensor.get_gyro_data()

        ax, ay, az = accel['x'], accel['y'], accel['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']

        # Calcola pitch e roll dall'accelerometro (rad)
        pitch = math.atan2(ax, math.sqrt(ay*ay + az*az))
        roll  = math.atan2(ay, math.sqrt(ax*ax + az*az))

        # Filtro complementare
        self.angle_x = self.alpha * (self.angle_x + gx*dt) + (1 - self.alpha) * pitch
        self.angle_y = self.alpha * (self.angle_y + gy*dt) + (1 - self.alpha) * roll

        # Proiezione su piano XY
        dx = self.angle_x * math.cos(pitch)
        dy = self.angle_y * math.cos(roll)

        return {"dx": dx, "dy": dy, "pitch": pitch, "roll": roll, "gz": gz}
