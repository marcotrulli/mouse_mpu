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
        print(f"Errore: {CALIB_FILE} non trovato! Creane uno con valori di default.")
        exit(1)

def map_to_xy(raw, calib):
    map_axis = calib['mapping']
    sign = calib['sign']
    rest = calib['rest']
    x = sign['X'] * (raw[map_axis['X']] - rest[map_axis['X']])
    y = sign['Y'] * (raw[map_axis['Y']] - rest[map_axis['Y']])
    return x, y

# =======================
# Thread reader
# =======================
def reader_thread(stop_event):
    sample_buffer = []
    while not stop_event.is_set():
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
        time.sleep(0.0005)

# =======================
# Thread sender
# =======================
def sender_thread(stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(2.0)
    try:
        sock.connect((PC_IP, PORT))
    except Exception as e:
        print("Connessione fallita:", e)
        return
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
            try:
                sock.sendall(pkt)
            except Exception:
                try:
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.connect((PC_IP, PORT))
                except Exception:
                    time.sleep(0.1)
    sock.close()

# =======================
# Main
# =======================
if __name__ == "__main__":
    calib = load_calib()  # carica il file calib.json già creato

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
