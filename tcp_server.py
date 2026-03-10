import socket
from pynput.mouse import Controller

# --- Setup mouse ---
mouse = Controller()
HOST = '0.0.0.0'
PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print(f"Connessione da {addr}")

buffer = ""
smooth_dx = 0
smooth_dy = 0
SMOOTH_FACTOR = 0.2  # regola fluidità (0-1)

while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    buffer += data
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        try:
            dx, dy = map(float, line.split(","))
            # Smoothing esponenziale per fluidità
            smooth_dx = smooth_dx + (dx - smooth_dx) * SMOOTH_FACTOR
            smooth_dy = smooth_dy + (dy - smooth_dy) * SMOOTH_FACTOR
            mouse.move(smooth_dx, smooth_dy)
        except:
            print("Errore parsing dati:", line)
