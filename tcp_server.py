# tcp_server.py
import socket
import struct
import uinput
import time

HOST = '0.0.0.0'
PORT = 5005

# scala per convertire angoli/movimenti in pixel (aggiusta empiricamente)
SCALE_X = 1.5
SCALE_Y = 1.5

# crea device uinput
events = (uinput.REL_X, uinput.REL_Y)
device = uinput.Device(events, name="mpu_mouse_uinput")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
print("In ascolto su", PORT)
conn, addr = s.accept()
print("Connessione da", addr)

buf = b""
try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        buf += data
        # ogni pacchetto è 8 byte (2 float32)
        while len(buf) >= 8:
            pkt = buf[:8]
            buf = buf[8:]
            try:
                dx, dy = struct.unpack('<ff', pkt)
                # applica scala e invia evento relativo
                rx = int(dx * SCALE_X)
                ry = int(dy * SCALE_Y)
                if rx != 0 or ry != 0:
                    device.emit(uinput.REL_X, rx, syn=False)
                    device.emit(uinput.REL_Y, ry, syn=True)
            except Exception as e:
                print("Errore parsing:", e)
except KeyboardInterrupt:
    pass
finally:
    conn.close()
    s.close()
