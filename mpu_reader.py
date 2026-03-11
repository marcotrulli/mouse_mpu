# mpu_reader.py
import time
import math
from smbus2 import SMBus

MPU_ADDR = 0x68
REG_PWR_MGMT_1 = 0x6B
REG_ACCEL_XOUT_H = 0x3B
REG_GYRO_XOUT_H = 0x43

def _to_signed(val):
    return val - 65536 if val > 32767 else val

class MPUReader:
    def __init__(self, address=MPU_ADDR, bus=1, alpha=0.96, dt=0.01,
                 filter_strength=0.1, calib_samples=200, deadzone=0.0, max_delta=100.0):
        self.address = address
        self.bus_num = bus
        self.bus = SMBus(self.bus_num)
        # wake up sensor
        self.bus.write_byte_data(self.address, REG_PWR_MGMT_1, 0x00)
        time.sleep(0.05)
        self.alpha = alpha
        self.dt = dt
        self.filter_strength = filter_strength
        self.deadzone = deadzone
        self.max_delta = max_delta

        self.angle_x = 0.0
        self.angle_y = 0.0

        self.gyro_offset_x = 0.0
        self.gyro_offset_y = 0.0
        self.calibrate_gyro(calib_samples)

    def read_raw_block(self):
        # legge accelerometro (6), temp (2), giroscopio (6) = 14 byte
        data = self.bus.read_i2c_block_data(self.address, REG_ACCEL_XOUT_H, 14)
        ax = _to_signed((data[0] << 8) | data[1]) / 16384.0
        ay = _to_signed((data[2] << 8) | data[3]) / 16384.0
        az = _to_signed((data[4] << 8) | data[5]) / 16384.0
        gx = _to_signed((data[8] << 8) | data[9]) / 131.0
        gy = _to_signed((data[10] << 8) | data[11]) / 131.0
        return {'ax': ax, 'ay': ay, 'az': az, 'gx': gx, 'gy': gy}

    def calibrate_gyro(self, samples=200):
        sum_x = 0.0
        sum_y = 0.0
        print("Calibrating gyro... keep MPU still")
        for _ in range(samples):
            d = self.read_raw_block()
            sum_x += d['gx']
            sum_y += d['gy']
            time.sleep(0.005)
        self.gyro_offset_x = sum_x / samples
        self.gyro_offset_y = sum_y / samples
        print(f"Gyro offsets: x={self.gyro_offset_x:.3f}, y={self.gyro_offset_y:.3f}")

    def read_angles(self):
        d = self.read_raw_block()
        accel = {'x': d['ax'], 'y': d['ay'], 'z': d['az']}
        gyro = {'x': d['gx'] - self.gyro_offset_x, 'y': d['gy'] - self.gyro_offset_y}

        # calcolo pitch/roll da accelerometro
        roll = math.atan2(accel['y'], accel['z']) * 180.0 / math.pi
        pitch = math.atan2(-accel['x'], math.sqrt(accel['y']**2 + accel['z']**2)) * 180.0 / math.pi

        # filtro complementare (integrazione giroscopio + accelerometro)
        self.angle_x = self.alpha * (self.angle_x + gyro['x'] * self.dt) + (1 - self.alpha) * pitch
        self.angle_y = self.alpha * (self.angle_y + gyro['y'] * self.dt) + (1 - self.alpha) * roll

        # leggero passabasso
        self.angle_x = self.angle_x * (1 - self.filter_strength) + pitch * self.filter_strength
        self.angle_y = self.angle_y * (1 - self.filter_strength) + roll * self.filter_strength

        # deadzone e clamp
        if abs(self.angle_x) < self.deadzone:
            self.angle_x = 0.0
        if abs(self.angle_y) < self.deadzone:
            self.angle_y = 0.0

        self.angle_x = max(min(self.angle_x, self.max_delta), -self.max_delta)
        self.angle_y = max(min(self.angle_y, self.max_delta), -self.max_delta)

        return self.angle_x, self.angle_y

    def read_filtered(self, dt=None, samples=1):
        total_x = 0.0
        total_y = 0.0
        for _ in range(samples):
            x, y = self.read_angles()
            total_x += x
            total_y += y
            if dt:
                time.sleep(dt)
        return {'dx': total_x / samples, 'dy': total_y / samples}
