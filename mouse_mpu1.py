# mouse_pi.py
import time
import socket
import struct
import threading
from queue import Queue, Empty
from mpu_reader import MPUReader

PC_IP = '192.168.1.179'
PORT = 5005

FPS = 120
FRAME_TIME = 1.0 / FPS
SEND_THRESHOLD = 0.1
SAMPLES_AVG = 3

# Queue per passare i campioni dal reader al sender
send_queue = Queue(maxsize=256)

# Inizializza MPU (usa lettura I2C in blocco)
mpu = MPUReader(alpha=0.95, deadzone=0.2, max_delta=15)

# Thread che legge continuamente il sensore e mette medie in coda
def reader_thread(stop_event):
    sample_buffer = []
    last_time = time.perf_counter()
    while not stop_event.is_set():
        # Legge un campione veloce (non fa sleep interno)
        sample = mpu.read_filtered(dt=None, samples=1)
        sample_buffer.append(sample)
        # Mantieni al massimo SAMPLES_AVG campioni
        if len(sample_buffer) >= SAMPLES_AVG:
            dx = sum(s['dx'] for s in sample_buffer) / len(sample_buffer)
            dy = sum(s['dy'] for s in sample_buffer) / len(sample_buffer)
            sample_buffer.clear()
            # Invia solo se significativo
            if abs(dx) > SEND_THRESHOLD or abs(dy) > SEND_THRESHOLD:
                try:
                    send_queue.put_nowait((dx, dy))
                except:
                    # se la coda è piena, scarta (preferibile a bloccare)
                    pass
        # Leggero yield per evitare busy-waiting aggressivo
        time.sleep(0.0005)

# Thread che invia i pacchetti al PC con timing costante
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
        # Prendi l'ultimo valore disponibile nella coda (drop older)
        dx = dy = 0.0
        try:
            # svuota la coda mantenendo solo l'ultimo elemento
            while True:
                dx, dy = send_queue.get_nowait()
        except Empty:
            pass
        # Se abbiamo un movimento significativo, invia
        if abs(dx) > SEND_THRESHOLD or abs(dy) > SEND_THRESHOLD:
            # pacchetto binario: 2 float32 (8 byte)
            pkt = struct.pack('<ff', float(dx), float(dy))
            try:
                sock.sendall(pkt)
            except Exception:
                # in caso di errore di rete, prova a riconnettere (semplice retry)
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
