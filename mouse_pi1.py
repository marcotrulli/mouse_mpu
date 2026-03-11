# mouse_pi1.py
import time
import socket
import struct
import threading
import json
from queue import Queue, Empty
from mpu_reader import MPUReader

PC_IP = '192.168.1.179'
PORT = 5005

FPS = 120
FRAME_TIME = 1.0 / FPS
SEND_THRESHOLD = 0.1
SAMPLES_AVG = 3

send_queue = Queue(maxsize=256)

# Inizializza MPU
mpu = MPUReader(alpha=0.95, deadzone=0.2, max_delta=15)

# Carica calibrazione
with open('calib.json', 'r') as f:
    calib = json.load(f)
print("Calibrazione caricata da file.")

def map_to_xy(raw, calib):
    rest = calib['rest']
    map_axis = calib['mapping']
    sign = calib['sign']

    # mappa le chiavi raw alle chiavi di rest
    axis_map = {'x': 'dx', 'y': 'dy', 'z': 'dz'}

    x = sign['X'] * (raw[axis_map[map_axis['X']]] - rest['dx'])
    y = sign['Y'] * (raw[axis_map[map_axis['Y']]] - rest['dy'])
    return x, y

def reader_thread(stop_event):
    sample_buffer = []
    last_time = time.perf_counter()
    while not stop_event.is_set():
        sample = mpu.read_filtered(dt=None, samples=1)
        sample_buffer.append(sample)
        if len(sample_buffer) >= SAMPLES_AVG:
            # media dei campioni
            avg_sample = {'dx': 0, 'dy': 0}
            avg_sample['dx'] = sum(s['dx'] for s in sample_buffer) / len(sample_buffer)
            avg_sample['dy'] = sum(s['dy'] for s in sample_buffer) / len(sample_buffer)
            sample_buffer.clear()

            dx, dy = map_to_xy(avg_sample, calib)

            if abs(dx) > SEND_THRESHOLD or abs(dy) > SEND_THRESHOLD:
                try:
                    send_queue.put_nowait((dx, dy))
                except:
                    pass
        time.sleep(0.0005)

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

if __name__ == "__main__":
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
