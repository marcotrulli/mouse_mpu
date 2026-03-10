# mpu_reader.py
from mpu6050 import mpu6050
import math

class MPUReader:
    def __init__(self, address=0x68, alpha=0.9, deadzone=0.3, max_delta=15, samples=3):
        self.sensor = mpu6050(address)
        self.alpha = alpha            # peso gyro nel filtro complementare
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.deadzone = deadzone      # soglia minima per dx/dy
        self.max_delta = max_delta    # delta massimo per stabilità
        self.samples = samples        # media mobile su N campioni

    def read_filtered(self, dt):
        dx_sum, dy_sum = 0, 0
        last_pitch, last_roll = 0, 0

        for _ in range(self.samples):
            accel = self.sensor.get_accel_data()
            gyro  = self.sensor.get_gyro_data()

            ax, ay, az = accel['x'], accel['y'], accel['z']
            gx, gy, gz = gyro['x'], gyro['y'], gyro['z']

            # calcolo pitch e roll
            pitch = math.atan2(ax, math.sqrt(ay*ay + az*az))
            roll  = math.atan2(ay, math.sqrt(ax*ax + az*az))

            # filtro complementare con gyro e accelerometro
            self.angle_x = self.alpha * (self.angle_x + gx*dt) + (1 - self.alpha) * pitch
            self.angle_y = self.alpha * (self.angle_y + gy*dt) + (1 - self.alpha) * roll

            dx = self.angle_x * math.cos(pitch)
            dy = self.angle_y * math.cos(roll)

            dx_sum += dx
            dy_sum += dy

            last_pitch, last_roll = pitch, roll

        # media mobile
        dx = dx_sum / self.samples
        dy = dy_sum / self.samples

        # deadzone
        if abs(dx) < self.deadzone: dx = 0
        if abs(dy) < self.deadzone: dy = 0

        # limiti massimo delta
        dx = max(min(dx, self.max_delta), -self.max_delta)
        dy = max(min(dy, self.max_delta), -self.max_delta)

        return {
            "dx": dx,
            "dy": dy,
            "pitch": last_pitch,
            "roll": last_roll,
            "gx": gx,
            "gy": gy,
            "gz": gz,
            "ax": ax,
            "ay": ay,
            "az": az
        }
