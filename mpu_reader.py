from mpu6050 import mpu6050
import math
import time

class MPUReader:
    def __init__(self, address=0x68, alpha=0.96, dt=0.01, filter_strength=0.1,
                 calib_samples=100, deadzone=0.0, max_delta=100.0):
        self.sensor = mpu6050(address)
        self.alpha = alpha
        self.dt = dt
        self.filter_strength = filter_strength
        self.deadzone = deadzone
        self.max_delta = max_delta

        self.angle_x = 0.0
        self.angle_y = 0.0

        # Offset giroscopio per compensare drift
        self.gyro_offset_x = 0.0
        self.gyro_offset_y = 0.0
        self.calibrate_gyro(calib_samples)

    def calibrate_gyro(self, samples=100):
        sum_x = 0.0
        sum_y = 0.0
        print("Calibrating gyro... keep MPU still")
        for _ in range(samples):
            gyro = self.sensor.get_gyro_data()
            sum_x += gyro['x']
            sum_y += gyro['y']
            time.sleep(0.01)
        self.gyro_offset_x = sum_x / samples
        self.gyro_offset_y = sum_y / samples
        print(f"Gyro offsets: x={self.gyro_offset_x:.3f}, y={self.gyro_offset_y:.3f}")

    def read_angles(self):
        accel = self.sensor.get_accel_data()
        gyro = self.sensor.get_gyro_data()

        # Calcolo pitch e roll dall'accelerometro
        roll = math.atan2(accel['y'], accel['z']) * 180 / math.pi
        pitch = math.atan2(-accel['x'], math.sqrt(accel['y']**2 + accel['z']**2)) * 180 / math.pi

        # Correzione giroscopio con offset
        gx = gyro['x'] - self.gyro_offset_x
        gy = gyro['y'] - self.gyro_offset_y

        # Filtro complementare
        self.angle_x = self.alpha * (self.angle_x + gx * self.dt) + (1 - self.alpha) * pitch
        self.angle_y = self.alpha * (self.angle_y + gy * self.dt) + (1 - self.alpha) * roll

        # Passa-basso leggero
        self.angle_x = self.angle_x * (1 - self.filter_strength) + pitch * self.filter_strength
        self.angle_y = self.angle_y * (1 - self.filter_strength) + roll * self.filter_strength

        # Applicazione deadzone
        if abs(self.angle_x) < self.deadzone:
            self.angle_x = 0.0
        if abs(self.angle_y) < self.deadzone:
            self.angle_y = 0.0

        # Limitazione delta massima
        self.angle_x = max(min(self.angle_x, self.max_delta), -self.max_delta)
        self.angle_y = max(min(self.angle_y, self.max_delta), -self.max_delta)

        return self.angle_x, self.angle_y

    def read_filtered(self, dt=None, samples=1):
        """
        Funzione compatibile con mouse_pi.py.
        Se samples>1, fa una media su più letture.
        """
        total_x = 0.0
        total_y = 0.0
        for _ in range(samples):
            x, y = self.read_angles()
            total_x += x
            total_y += y
            if dt:
                time.sleep(dt)
        return total_x / samples, total_y / samples
