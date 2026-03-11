import time
import socket
import struct
import threading
from queue import Queue, Empty
from mpu_reader import MPUReader
import json

PC_IP = '192.168.1.179'
PORT = 5005

FPS = 120
FRAME_TIME = 1.0 / FPS
SEND_THRESHOLD = 0.1
SAMPLES_AVG = 3
CALIB_FILE = "calib.json"
PRINT_DEBUG = True  # True per vedere dx, dy sul terminale

send_queue = Queue(maxsize=256)

# Inizializza MPU
mpu = MPUReader(alpha=0.95, deadzone=0.2, max_delta=15)

# =======================
# Funzioni calibrazione
# =======================
def load_calib():
    try:
        with open(CALIB_FILE, 'r') as f:
            print("Calibrazione caricata da file.")
            return json.load(f)
    except FileNotFoundError:
        print(f"Errore: {CALIB_FILE} non trovato!")
        exit(1)

def map_to_xy(raw, calib):
    map_axis = calib['mapping']
    sign = calib['sign']
    rest = calib['rest']
    # Gestione sicura: se manca una chiave, usa 0
    x = sign['X'] * (raw.get(map_axis['X'], 0) - rest.get(map_axis['X'], 0))
    y = sign['Y'] * (raw.get(map_axis['Y'], 0) - rest.get(map_axis['Y'], 0))
    return x, y

# =======================
# Thread reader
# =======================
def reader_thread(stop_event):
    sample_buffer = []
    while not stop_event.is_set():
        try:
            raw = mpu.read_filtered(dt=None, samples=1)
            dx, dy = map_to_xy(raw, calib)
            sample_buffer.append({'dx': dx, 'dy': dy})

            if len(sample_buffer) >= SAMPLES_AVG:
                dx_avg = sum(s['dx'] for s in sample_buffer) / len(sample_buffer)
                dy_avg = sum(s['dy'] for s in sample_buffer) / len(sample_buffer)
                sample_buffer.clear()
                if abs(dx_avg) > SEND_THRESHOLD or abs(dy_avg) > SEND_THRESHOLD:
                    try:
                        send_queue.put_nowait((dx_avg, dy_avg))
                    except:
                        pass
                if PRINT_DEBUG:
                    print(f"dx={dx_avg:.3f}, dy={dy_avg:.3f}")
            time.sleep(0.005)  # leggermente più lento per stabilità I2C
        except OSError as e:
            print("Errore I2C, retry in 0.05s:", e)
            time.sleep(0.05)
        except Exception as e:
            print("Errore lettura:", e)
            time.sleep(0.05)

# =======================
# Thread sender
# =======================
def sender_thread(stop_event):
    sock = None
    while not stop_event.is_set():
        try:
            if sock is None:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(2.0)
                sock.connect((PC_IP, PORT))
                print("Connesso al PC!")
            next_frame = time.perf_counter()
            while not stop_event.is_set():
                now = time.perf_counter()
                if now < next_frame:
                    time.sleep(next_frame - now)
                    continue
                next_frame += FRAME_TIME

                dx = dy = 0.0
                try:
                    while True:
                        dx, dy = send_queue.get_nowait()
                except Empty:
                    pass

                if abs(dx) > SEND_THRESHOLD or abs(dy) > SEND_THRESHOLD:
                    pkt = struct.pack('<ff', float(dx), float(dy))
                    sock.sendall(pkt)
        except Exception as e:
            print("Errore connessione/invio:", e)
            if sock:
                sock.close()
            sock = None
            time.sleep(0.5)

# =======================
# Main
# =======================
if __name__ == "__main__":
    calib = load_calib()

    stop = threading.Event()
    r = threading.Thread(target=reader_thread, args=(stop,), daemon=True)
    s = threading.Thread(target=sender_thread, args=(stop,), daemon=True)
    r.start()
    s.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop.set()
        r.join(timeout=1)
        s.join(timeout=1)
