import time
import json
from mpu_reader import MPUReader
import statistics

CALIB_FILE = "calib.json"
SAMPLES = 300
DELAY = 0.01

mpu = MPUReader(alpha=0.95, deadzone=0.2, max_delta=15)

def sample_sensor():
    xs, ys, zs = [], [], []
    for _ in range(SAMPLES):
        try:
            data = mpu.read_filtered(dt=None, samples=1)
            xs.append(data.get('dx', 0))
            ys.append(data.get('dy', 0))
            zs.append(data.get('dz', 0))
            time.sleep(DELAY)
        except Exception as e:
            print("Errore lettura:", e)
            time.sleep(0.05)
    return {
        'x_mean': statistics.mean(xs),
        'y_mean': statistics.mean(ys),
        'z_mean': statistics.mean(zs)
    }

print("=== Calibrazione MPU6050 ===")
input("Tieni il sensore fermo e piatto, poi premi INVIO...")
rest = sample_sensor()
print(f"Valori a riposo: {rest}")

input("Muovi solo l'asse che vuoi mappare come X (destra/sinistra), poi premi INVIO...")
x_move = sample_sensor()
print(f"Valori movimento X: {x_move}")

input("Muovi solo l'asse che vuoi mappare come Y (su/giù), poi premi INVIO...")
y_move = sample_sensor()
print(f"Valori movimento Y: {y_move}")

# Calcola delta assoluto
delta_x = {k: abs(x_move[f"{k}_mean"] - rest[f"{k}_mean"]) for k in ['x', 'y', 'z']}
delta_y = {k: abs(y_move[f"{k}_mean"] - rest[f"{k}_mean"]) for k in ['x', 'y', 'z']}

# Trova asse dominante
sensor_axis_for_X = max(delta_x, key=delta_x.get)
sensor_axis_for_Y = max(delta_y, key=delta_y.get)

if sensor_axis_for_X == sensor_axis_for_Y:
    sorted_y = sorted(delta_y.items(), key=lambda kv: kv[1], reverse=True)
    sensor_axis_for_Y = sorted_y[1][0]

# Determina segno
sign_X = 1 if (x_move[f"{sensor_axis_for_X}_mean"] - rest[f"{sensor_axis_for_X}_mean"]) > 0 else -1
sign_Y = 1 if (y_move[f"{sensor_axis_for_Y}_mean"] - rest[f"{sensor_axis_for_Y}_mean"]) > 0 else -1

# Salva calibrazione
calib = {
    'mapping': {'X': sensor_axis_for_X, 'Y': sensor_axis_for_Y},
    'sign': {'X': sign_X, 'Y': sign_Y},
    'rest': {'dx': rest['x_mean'], 'dy': rest['y_mean'], 'dz': rest['z_mean']}
}

with open(CALIB_FILE, 'w') as f:
    json.dump(calib, f, indent=2)

print("\nCalibrazione completata!")
print(f"Mapping: {calib['mapping']}, Segni: {calib['sign']}")
print(f"Valori di riposo: {calib['rest']}")
print(f"Salvato in {CALIB_FILE}")
