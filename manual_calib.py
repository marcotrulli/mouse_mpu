# test_roll_pitch.py
import time
from mpu6050 import mpu6050

# Inizializza MPU6050
sensor = mpu6050(0x68)

# Offset del giroscopio (se vuoi calibrare a mano)
gyro_offset_x = 0
gyro_offset_y = 0

# Fattore di scala per velocità cursore (modificabile)
scale_x = 1.0  # pitch → su/giù
scale_y = 1.0  # roll → destra/sinistra

print("Muovi la mano per testare il movimento (CTRL+C per uscire)...")
time.sleep(2)

try:
    while True:
        accel_data = sensor.get_accel_data()
        gyro_data = sensor.get_gyro_data()

        # Calcola angoli base da accelerometro (approssimazione)
        pitch = accel_data['x']  # Pitch → asse X → su/giù
        roll  = accel_data['y']  # Roll  → asse Y → destra/sinistra

        # Applica offset e scala
        dx = (roll - gyro_offset_y) * scale_y
        dy = (pitch - gyro_offset_x) * scale_x

        print(f"dx (destra/sinistra) = {dx:.2f}, dy (su/giù) = {dy:.2f}", end='\r')
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nTest terminato.")
