from mpu6050 import mpu6050
import time

mpu = mpu6050(0x68)

axes = ['x', 'y', 'z']

print("Test manuale assi MPU6050")
print("Premi CTRL+C per passare al prossimo asse\n")

for axis in axes:
    input(f"Premi INVIO per leggere l'asse {axis.upper()}")
    print(f"Muovi solo questo asse... Ctrl+C per fermare")
    try:
        while True:
            val = mpu.get_accel_data()[axis]
            print(f"{axis.upper()} = {val:.3f}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\nFine lettura asse {axis.upper()}\n")
