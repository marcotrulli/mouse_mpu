from mpu6050 import mpu6050
import time

# Inizializza il sensore
mpu = mpu6050(0x68)

def read_axis(axis):
    """Legge il valore accelerometro dell'asse scelto."""
    accel = mpu.get_accel_data()
    return accel[axis]

def manual_calibrate():
    axes = ['x', 'y', 'z']
    mapping = {}
    signs = {}

    print("Manual Calibration of MPU6050\n")
    print("Ruota il sensore come desideri e premi INVIO per catturare i valori.")

    for axis in axes:
        input(f"\nPremi INVIO per iniziare a leggere l'asse {axis.upper()}...")
        print(f"Muovi solo questo asse e osserva i valori.")
        
        values = []
        try:
            while True:
                val = read_axis(axis)
                print(f"{axis.upper()} = {val:.3f}", end='\r')
                values.append(val)
                time.sleep(0.1)
        except KeyboardInterrupt:
            # Interruzione con Ctrl+C per fermare lettura
            mean_val = sum(values) / len(values)
            print(f"\nValore medio registrato per {axis.upper()}: {mean_val:.3f}")
            # Chiedi all'utente il segno corretto
            sign_input = input("Vuoi invertire il segno? (s/n): ").strip().lower()
            signs[axis] = -1 if sign_input == 's' else 1
            mapping[axis] = mean_val * signs[axis]

    print("\nCalibrazione completata!")
    print("Mapping finale:", mapping)
    print("Segni:", signs)

if __name__ == "__main__":
    manual_calibrate()
