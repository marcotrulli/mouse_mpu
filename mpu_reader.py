from mpu6050 import mpu6050
import time

class MPUReader:
    def __init__(self, address=0x68, alpha=0.5, deadzone=0.02):
        self.sensor = mpu6050(address)
        self.alpha = alpha          # filtro passa basso
        self.deadzone = deadzone    # soglia minima per ignorare il movimento
        self.prev_x = 0
        self.prev_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.calibrate()

    def calibrate(self, samples=100, delay=0.01):
        """Calibrazione a riposo: legge il sensore fermo e calcola offset"""
        print("Calibrazione MPU a riposo...")
        sum_x, sum_y = 0, 0
        for _ in range(samples):
            data = self.sensor.get_accel_data()
            sum_x += data['x']
            sum_y += data['y']
            time.sleep(delay)
        self.offset_x = sum_x / samples
        self.offset_y = sum_y / samples
        print(f"Offset calcolati: x={self.offset_x:.4f}, y={self.offset_y:.4f}")

    def scale(self, val):
        """Scala il valore con sensibilità non lineare"""
        sign = 1 if val >= 0 else -1
        # esponente <2 per non amplificare troppo i movimenti piccoli
        return sign * (abs(val) ** 1.5) * 20

    def read_filtered(self):
        accel = self.sensor.get_accel_data()
        # sottrae offset
        x = accel['x'] - self.offset_x
        y = accel['y'] - self.offset_y

        # applica filtro passa basso
        filtered_x = self.alpha * x + (1 - self.alpha) * self.prev_x
        filtered_y = self.alpha * y + (1 - self.alpha) * self.prev_y

        self.prev_x = filtered_x
        self.prev_y = filtered_y

        # applica deadzone
        if abs(filtered_x) < self.deadzone:
            filtered_x = 0
        if abs(filtered_y) < self.deadzone:
            filtered_y = 0

        # scala valori per il mouse
        dx = self.scale(filtered_x)
        dy = self.scale(filtered_y)

        return {"dx": dx, "dy": dy, "az": accel['z']}
