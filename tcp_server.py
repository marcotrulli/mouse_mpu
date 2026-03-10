import socket
from pynput.mouse import Controller

mouse = Controller()
HOST = '0.0.0.0'
PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print(f"Connessione da {addr}")

buffer = ""

while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    buffer += data
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        try:
            dx, dy = map(float, line.split(","))
            mouse.move(dx, dy)  # movimento diretto per massimo FPS
        except:
            print("Errore parsing dati:", line)
