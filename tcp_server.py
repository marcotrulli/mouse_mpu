# tcp_server_windows.py
import socket
import struct
import win32api
import win32con

HOST = '0.0.0.0'
PORT = 5005

SCALE_X = 1.5
SCALE_Y = 1.5

def move_mouse(dx, dy):
    # Movimento relativo usando API Windows
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

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

            dx, dy = struct.unpack('<ff', pkt)

            rx = dx * SCALE_X
            ry = dy * SCALE_Y

            if abs(rx) > 0.01 or abs(ry) > 0.01:
                move_mouse(rx, ry)

except KeyboardInterrupt:
    pass

finally:
    conn.close()
    s.close()
