import socket

HOST = '0.0.0.0'  # ascolta tutte le interfacce
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
            print(f"dx={dx:.2f}, dy={dy:.2f}")
        except:
            print("Errore parsing dati:", line)
