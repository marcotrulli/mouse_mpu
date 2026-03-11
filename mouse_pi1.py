#!/usr/bin/env python3
"""
mouse_pi.py
Raspberry Pi + MPU6050 -> invio movimenti mouse via TCP/UDP
Include calibrazione automatica roll/pitch, salvataggio calibrazione e smoothing.
"""

import time
import json
import socket
import argparse
import statistics
from pathlib import Path

try:
    from mpu6050 import mpu6050
except Exception as e:
    raise SystemExit("Errore import mpu6050: assicurati di avere 'mpu6050-raspberrypi' installato.") from e

CALIB_FILE = Path("calib.json")

# --- Parametri modificabili ---
DEFAULT_HOST = "192.168.1.100"   # cambia con IP del PC client
DEFAULT_PORT = 5005
DEFAULT_RATE = 100               # Hz
SAMPLES_REST = 300
SAMPLES_MOVE = 300
DEADZONE = 0.02                  # soglia sotto cui ignora il movimento (in unità accelerometro)
ALPHA = 0.25                     # filtro esponenziale (0..1) più alto = meno smoothing
DEFAULT_SCALE_X = 200.0          # scala per dy (pitch -> asse X)
DEFAULT_SCALE_Y = 200.0          # scala per dx (roll -> asse Y)
SOCKET_TIMEOUT = 2.0

# --- Utility sensore ---
def sample_accel(sensor, samples=SAMPLES_REST, delay=0.005):
    xs, ys, zs = [], [], []
    for _ in range(samples):
        d = sensor.get_accel_data()
        xs.append(d['x'])
        ys.append(d['y'])
        zs.append(d['z'])
        time.sleep(delay)
    return {
        'x_mean': statistics.mean(xs),
        'y_mean': statistics.mean(ys),
        'z_mean': statistics.mean(zs),
        'x_std': statistics.pstdev(xs),
        'y_std': statistics.pstdev(ys),
        'z_std': statistics.pstdev(zs),
    }

# --- Calibrazione guidata ---
def run_calibration(sensor):
    print("\n=== Calibrazione automatica MPU6050 (roll/pitch) ===\n")
    input("Posiziona il sensore fermo e piatto (riposo). Premi INVIO per acquisire il valore di riposo...")
    rest = sample_accel(sensor, samples=SAMPLES_REST)
    print("Valori di riposo acquisiti:", {k: round(v,4) for k,v in rest.items()})

    # Muovi solo roll (destra/sinistra) -> corrisponde asse Y dell'accelerometro
    input("\nOra MUOVI SOLO il ROLL (destra/sinistra). Premi INVIO per iniziare la registrazione, poi muovi la mano per qualche secondo...")
    time.sleep(0.3)
    roll_move = sample_accel(sensor, samples=SAMPLES_MOVE)
    print("Campione roll acquisito.")

    # Muovi solo pitch (su/giù) -> corrisponde asse X dell'accelerometro
    input("\nOra MUOVI SOLO il PITCH (su/giù). Premi INVIO per iniziare la registrazione, poi muovi la mano per qualche secondo...")
    time.sleep(0.3)
    pitch_move = sample_accel(sensor, samples=SAMPLES_MOVE)
    print("Campione pitch acquisito.\n")

    # Calcola delta assoluti rispetto al riposo
    delta_roll = {
        'x': abs(roll_move['x_mean'] - rest['x_mean']),
        'y': abs(roll_move['y_mean'] - rest['y_mean']),
        'z': abs(roll_move['z_mean'] - rest['z_mean']),
    }
    delta_pitch = {
        'x': abs(pitch_move['x_mean'] - rest['x_mean']),
        'y': abs(pitch_move['y_mean'] - rest['y_mean']),
        'z': abs(pitch_move['z_mean'] - rest['z_mean']),
    }

    # Determina asse dominante per roll e pitch
    axis_for_roll = max(delta_roll, key=delta_roll.get)
    axis_for_pitch = max(delta_pitch, key=delta_pitch.get)

    # Se per qualche motivo è la stessa asse, prendi la seconda migliore per pitch
    if axis_for_roll == axis_for_pitch:
        sorted_pitch = sorted(delta_pitch.items(), key=lambda kv: kv[1], reverse=True)
        axis_for_pitch = sorted_pitch[1][0] if len(sorted_pitch) > 1 else axis_for_pitch

    # Determina segno: se il valore medio durante la mossa è maggiore del riposo -> +1, altrimenti -1
    sign_roll = 1 if (roll_move[f"{axis_for_roll}_mean"] - rest[f"{axis_for_roll}_mean"]) > 0 else -1
    sign_pitch = 1 if (pitch_move[f"{axis_for_pitch}_mean"] - rest[f"{axis_for_pitch}_mean"]) > 0 else -1

    # Mappatura finale: roll -> dx, pitch -> dy
    calib = {
        "mapping": {"dx": axis_for_roll, "dy": axis_for_pitch},
        "sign": {"dx": sign_roll, "dy": sign_pitch},
        "rest": {"x": rest['x_mean'], "y": rest['y_mean'], "z": rest['z_mean']},
        "scale": {"dx": DEFAULT_SCALE_Y, "dy": DEFAULT_SCALE_X},
        "deadzone": DEADZONE,
        "last_calibrated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open(CALIB_FILE, "w") as f:
        json.dump(calib, f, indent=2)

    print("Calibrazione completata. File salvato:", CALIB_FILE)
    print("Mapping:", calib['mapping'], "Segni:", calib['sign'])
    return calib

def load_calibration():
    if CALIB_FILE.exists():
        with open(CALIB_FILE, "r") as f:
            return json.load(f)
    return None

# --- Networking ---
class Sender:
    def __init__(self, host, port, use_udp=False):
        self.host = host
        self.port = port
        self.use_udp = use_udp
        self.sock = None
        self.connect()

    def connect(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        if self.use_udp:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(SOCKET_TIMEOUT)
            try:
                self.sock.connect((self.host, self.port))
            except Exception as e:
                print(f"[WARN] Connessione TCP fallita: {e}. Riprovo più tardi.")
                self.sock = None

    def send(self, dx, dy, ts=None):
        payload = json.dumps({"dx": dx, "dy": dy, "ts": ts or time.time()})
        try:
            if self.use_udp:
                self.sock.sendto(payload.encode("utf-8"), (self.host, self.port))
            else:
                if not self.sock:
                    self.connect()
                    if not self.sock:
                        return
                # invia con newline come separatore
                self.sock.sendall((payload + "\n").encode("utf-8"))
        except Exception as e:
            print(f"[WARN] Errore invio: {e}. Riconnessione in corso.")
            self.connect()

# --- Main loop ---
def main():
    parser = argparse.ArgumentParser(description="MPU6050 -> mouse (Raspberry Pi)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="IP del PC client")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port del client")
    parser.add_argument("--rate", type=int, default=DEFAULT_RATE, help="Frequenza di aggiornamento (Hz)")
    parser.add_argument("--udp", action="store_true", help="Usa UDP invece di TCP")
    parser.add_argument("--recalibrate", action="store_true", help="Forza ricalibrazione")
    args = parser.parse_args()

    sensor = mpu6050(0x68)
    calib = None if args.recalibrate else load_calibration()
    if calib is None:
        calib = run_calibration(sensor)

    sender = Sender(args.host, args.port, use_udp=args.udp)

    # Parametri runtime
    rate = max(10, min(500, args.rate))
    period = 1.0 / rate
    alpha = ALPHA
    deadzone = calib.get("deadzone", DEADZONE)
    scale_dx = calib.get("scale", {}).get("dx", DEFAULT_SCALE_Y)
    scale_dy = calib.get("scale", {}).get("dy", DEFAULT_SCALE_X)
    sign_dx = calib["sign"]["dx"]
    sign_dy = calib["sign"]["dy"]
    map_dx = calib["mapping"]["dx"]
    map_dy = calib["mapping"]["dy"]
    rest = calib["rest"]

    print("\nAvvio loop principale. Premere CTRL+C per terminare.")
    prev_dx = 0.0
    prev_dy = 0.0

    try:
        while True:
            a = sensor.get_accel_data()
            # leggi i valori raw dell'asse mappata
            raw_dx = a[map_dx] - rest[map_dx]
            raw_dy = a[map_dy] - rest[map_dy]

            # applica deadzone
            if abs(raw_dx) < deadzone:
                raw_dx = 0.0
            if abs(raw_dy) < deadzone:
                raw_dy = 0.0

            # applica segno e scala (dx = roll -> orizzontale, dy = pitch -> verticale)
            dx = sign_dx * raw_dx * scale_dx
            dy = sign_dy * raw_dy * scale_dy

            # filtro esponenziale per smoothing
            dx = alpha * dx + (1 - alpha) * prev_dx
            dy = alpha * dy + (1 - alpha) * prev_dy
            prev_dx, prev_dy = dx, dy

            # invio al client (timestamp opzionale)
            sender.send(dx, dy, ts=time.time())

            # per debug: stampa valori ogni tot cicli (non troppo verboso)
            # print(f"dx={dx:.2f} dy={dy:.2f}", end="\r")

            time.sleep(period)
    except KeyboardInterrupt:
        print("\nTerminato dall'utente.")
    finally:
        if sender.sock:
            try:
                sender.sock.close()
            except:
                pass

if __name__ == "__main__":
    main()
