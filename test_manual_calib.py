# test_manual_calib.py
import time
from mpu_reader import MPUReader

# ----------------- CONFIGURAZIONE MANUALE -----------------
# Mappa gli assi: quale asse del sensore diventa X e Y
map_axis = {
    'X': 'x',  # cambiare in 'y' se vuoi invertire asse X
    'Y': 'y'   # cambiare in 'x' se vuoi invertire asse Y
}

# Segni per invertire direzioni (+1 normale, -1 invertito)
sign = {
    'X': 1,  # cambiare in -1 se dx va in direzione opposta
    'Y': 1   # cambiare in -1 se dy va in direzione opposta
}
# ----------------------------------------------------------

# Inizializza MPU
mpu = MPUReader(alpha=0.95, deadzone=0.0, max_delta=50)

# Leggi valori di riposo (fermo)
rest = mpu.read_filtered(dt=None, samples=10)
x_rest = rest['x']
y_rest = rest['y']

print("Valori di riposo registrati:")
print(f"x={x_rest:.2f}, y={y_rest:.2f}")
print("Muovi il sensore e osserva le variazioni...")
print("Premi Ctrl+C per uscire.\n")

try:
    while True:
        sample = mpu.read_filtered(dt=None, samples=1)
        # Applica mapping e segni configurabili
        dx = sign['X'] * (sample[map_axis['X']] - x_rest)
        dy = sign['Y'] * (sample[map_axis['Y']] - y_rest)

        # Determina direzione testuale
        dir_x = "destra" if dx > 0 else ("sinistra" if dx < 0 else "fermo")
        dir_y = "su" if dy > 0 else ("giù" if dy < 0 else "fermo")

        print(f"dx={dx:+.2f} ({dir_x}) | dy={dy:+.2f} ({dir_y})")
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nTest terminato.")
