import socket
import pyautogui

HOST = ''
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Server TCP avviato sulla porta {PORT}...")

conn, addr = server.accept()
print(f"Connessione da {addr}")

while True:
    try:
        data = conn.recv(1024).decode()
        if not data:
            continue
        try:
            dx, dy, gx, gy, gz, ax, ay, az = [float(x) for x in data.strip().split(',')]
        except ValueError:
            print("Errore parsing dati:", data)
            continue

        # muovi mouse
        pyautogui.moveRel(dx, dy)

        # stampa valori su PC
        print(f"dx={dx:.2f}, dy={dy:.2f} | gx={gx:.2f}, gy={gy:.2f}, gz={gz:.2f} | ax={ax:.2f}, ay={ay:.2f}, az={az:.2f}")

    except Exception as e:
        print("Errore:", e)
        break

conn.close()
server.close()
