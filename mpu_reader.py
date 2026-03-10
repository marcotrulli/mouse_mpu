# mpu_reader.py
from mpu6050 import mpu6050
import math

class MPUReader:
    def __init__(self, address=0x68, alpha=0.98):
        self.sensor = mpu6050(address)
        self.alphafrom mpu6050 import mpu6050
import math

class MPUReader:
    def __init__(self, address=0x68, alpha=0.95, deadzone=0.2, max_delta=15):
        self.sensor = mpu6050(address)
        self.alpha = alpha
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.deadzone = deadzone
        self.max_delta = max_delta

    def read_filtered(self, dt):
        accel = self.sensor.get_accel_data()
        gyro  = self.sensor.get_gyro_data()

        ax, ay, az = accel['x'], accel['y'], accel['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']

        pitch = math.atan2(ax, math.sqrt(ay*ay + az*az))
        roll  = math.atan2(ay, math.sqrt(ax*ax + az*az))

        self.angle_x = self.alpha * (self.angle_x + gx*dt) + (1 - self.alpha) * pitch
        self.angle_y = self.alpha * (self.angle_y + gy*dt) + (1 - self.alpha) * roll

        dx = self.angle_x * math.cos(pitch)
        dy = self.angle_y * math.cos(roll)

        # Limita delta
        dx = max(min(dx, self.max_delta), -self.max_delta)
        dy = max(min(dy, self.max_delta), -self.max_delta)

        # Deadzone
        if abs(dx) < self.deadzone: dx = 0
        if abs(dy) < self.deadzone: dy = 0

        return {
            "dx": dx,
            "dy": dy,
            "pitch": pitch,
            "roll": roll,
            "gx": gx,
            "gy": gy,
            "gz": gz,
            "ax": ax,
            "ay": ay,
            "az": az
        } = alpha
        self.angle_x = 0.0
        self.angle_y = 0.0

    def read_filtered(self, dt):
        # Legge accelerometro e gyro
        accel = self.sensor.get_accel_data()
        gyro  = self.sensor.get_gyro_data()

        ax, ay, az = accel['x'], accel['y'], accel['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']

        # Calcola pitch e roll dall'accelerometro
        pitch = math.atan2(ax, math.sqrt(ay*ay + az*az))
        roll  = math.atan2(ay, math.sqrt(ax*ax + az*az))

        # Filtro complementare
        self.angle_x = self.alpha * (self.angle_x + gx*dt) + (1 - self.alpha) * pitch
        self.angle_y = self.alpha * (self.angle_y + gy*dt) + (1 - self.alpha) * roll

        # Proiezione su piano 2D
        dx = self.angle_x * math.cos(pitch)
        dy = self.angle_y * math.cos(roll)

        return {
            "dx": dx,
            "dy": dy,
            "pitch": pitch,
            "roll": roll,
            "gx": gx,
            "gy": gy,
            "gz": gz,
            "ax": ax,
            "ay": ay,
            "az": az
        }
