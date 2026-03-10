from mpu6050 import mpu6050

class MPUReader:
    def __init__(self, address=0x68):
        self.sensor = mpu6050(address)
        # Valori per filtro complementare semplice
        self.prev_x = 0
        self.prev_y = 0
        self.alpha = 0.5  # coefficiente filtro (0-1)

    def read_filtered(self):
        accel = self.sensor.get_accel_data()
        # filtro semplice (media pesata tra valore precedente e nuovo)
        filtered_x = self.alpha * accel['x'] + (1 - self.alpha) * self.prev_x
        filtered_y = self.alpha * accel['y'] + (1 - self.alpha) * self.prev_y

        self.prev_x = filtered_x
        self.prev_y = filtered_y

        return {
            "ax": filtered_x,
            "ay": filtered_y,
            "az": accel['z']
        }
