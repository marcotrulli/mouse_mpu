# tcp_server.py
import socket
from pynput.mouse import Controller

PC_IP = "0.0.0.0"
PORT = 5005

mouse = Controller()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((PC_IP, PORT))
sock.listen(1)
print(f"Server TCP avviato sulla porta {PORT}...")
conn, addr = sock.accept()
print(f"Connessione da {addr}")

try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        try:
            # Riceve dx,dy + gyro X/Y/Z + accel X/Y/Z (8 valori)
            dx_str, dy_str, gx_str, gy_str, gz_str, ax_str, ay_str, az_str = data.decode().split(",")

            dx = float(dx_str)
            dy = float(dy_str)
            gx = float(gx_str)
            gy = float(gy_str)
            gz = float(gz_str)
            ax = float(ax_str)
            ay = float(ay_str)
            az = float(az_str)

            # Muove mouse relativamente
            mouse.move(dx, dy)

            # Stampa per debug valori X/Y/Z
            print(f"dx={dx:.2f}, dy={dy:.2f} | gx={gx:.2f}, gy={gy:.2f}, gz={gz:.2f} | ax={ax:.2f}, ay={ay:.2f}, az={az:.2f}")

        except Exception as e:
            print(f"Errore parsing dati: {e}")

except KeyboardInterrupt:
    print("\nChiusura server...")
    conn.close()
    sock.close()
