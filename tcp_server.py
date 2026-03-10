import socket
import json
from pynput.mouse import Controller

HOST = "0.0.0.0"  # ascolta tutte le interfacce
PORT = 5005

mouse = Controller()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server TCP in ascolto su {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print(f"Connessione da {addr}")
        buffer = ""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    payload = json.loads(line)
                    dx = payload.get("dx", 0)
                    dy = payload.get("dy", 0)
                    mouse.move(dx, dy)
                except Exception as e:
                    print("Errore:", e)
