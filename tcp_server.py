import socket
import pyautogui

# --- TCP setup ---
HOST = ''  # tutte le interfacce
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Server TCP avviato sulla porta {PORT}...")

conn, addr = server.accept()
print("Connessione da", addr)

pyautogui.FAILSAFE = False

while True:
    try:
        data = conn.recv(1024).decode()
        if not data:
            continue

        # parsing dei valori
        try:
            dx, dy, gx, gy, gz, ax, ay, az = map(float, data.split(','))
            print(f"dx={dx:.2f}, dy={dy:.2f} | gx={gx:.2f}, gy={gy:.2f}, gz={gz:.2f} | ax={ax:.2f}, ay={ay:.2f}, az={az:.2f}")
        except Exception as e:
            print("Errore parsing dati:", e)
            continue

        # sposta il mouse
        pyautogui.moveRel(dx, dy, duration=0)

    except Exception as e:
        print("Errore socket:", e)
        break
