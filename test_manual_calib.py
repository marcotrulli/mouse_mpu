# test_manual_calib.py
import time
from mpu_reader import MPUReader

# ----------------- CONFIGURAZIONE MANUALE -----------------
map_axis = {
    'X': 0,  # 0 = primo valore restituito da read_filtered
    'Y': 1   # 1 = secondo valore restituito da read_filtered
}

sign = {
    'X': 1,  # invertire direzione X se necessario
    'Y': 1   # invertire direzione Y se necessario
}
# ----------------------------------------------------------

# Inizializza MPU
mpu = MPUReader(alpha=0.95, deadzone=0.0, max_delta=50)

# Leggi valori di riposo (fermo)
samples = [mpu.read_filtered(dt=None, samples=1) for _ in range(10)]
# Supporta sia dizionario sia tupla/lista
x_rest = sum(s[map_axis['X']] if isinstance(s, (list, tuple)) else s.get('x', 0) for s in samples)/len(samples)
y_rest = sum(s[map_axis['Y']] if isinstance(s, (list, tuple)) else s.get('y', 0) for s in samples)/len(samples)

print("Valori di riposo registrati:")
print(f"x={x_rest:.2f}, y={y_rest:.2f}")
print("Muovi il sensore e osserva le variazioni...")
print("Premi Ctrl+C per uscire.\n")

try:
    while True:
        sample = mpu.read_filtered(dt=None, samples=1)
        # Leggi dx/dy in modo compatibile
        dx = (sample[map_axis['X']] if isinstance(sample, (list, tuple)) else sample.get('x',0)) - x_rest
        dy = (sample[map_axis['Y']] if isinstance(sample, (list, tuple)) else sample.get('y',0)) - y_rest

        dx *= sign['X']
        dy *= sign['Y']

        dir_x = "destra" if dx > 0 else ("sinistra" if dx < 0 else "fermo")
        dir_y = "su" if dy > 0 else ("giù" if dy < 0 else "fermo")

        print(f"dx={dx:+.2f} ({dir_x}) | dy={dy:+.2f} ({dir_y})")
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nTest terminato.")
