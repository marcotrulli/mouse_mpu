from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)

for _ in range(100):
    data = sensor.get_accel_data()
    print(data)
    time.sleep(0.05)
