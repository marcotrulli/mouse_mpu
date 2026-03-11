from mpu6050 import mpu6050
import time

# Inizializza il sensore
mpu = mpu6050(0x68)

# Mapping invertito: cursore X usa asse Y dell'MPU, cursore Y usa asse X dell'MPU
cursor_to_mpu = {'X': 'y', 'Y': 'x', 'Z': 'z'}

def read_axis(axis):
    accel = mpu.get_accel_data()
    return accel[axis]

def manual_calibrate():
    signs = {}

    print("Manual Calibration of MPU6050 with X/Y inverted\n")
    print("Ruota il sensore come desideri e premi INVIO per catturare i valori.")

    for cursor_axis, mpu_axis in cursor_to_mpu.items():
        input(f"\nPremi INVIO per iniziare a leggere l'asse {cursor_axis} (MPU {mpu_axis.upper()})...")
        print(f"Muovi solo questo asse e osserva i valori.")
        
        values = []
        try:
            while True:
                val = read_axis(mpu_axis)
                print(f"{mpu_axis.upper()} = {val:.3f}", end='\r')
                values.append(val)
                time.sleep(0.1)
        except KeyboardInterrupt:
            mean_val = sum(values) / len(values)
            print(f"\nValore medio registrato per {cursor_axis} (MPU {mpu_axis.upper()}): {mean_val:.3f}")
            sign_input = input("Vuoi invertire il segno? (s/n): ").strip().lower()
            signs[cursor_axis] = -1 if sign_input == 's' else 1

    print("\nCalibrazione completata!")
    print("Segni finali:", signs)

if __name__ == "__main__":
    manual_calibrate()
