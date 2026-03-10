# tcp_server.py
import socket
from pynput.mouse import Controller

PC_IP = "0.0.0.0"
PORT  = 5005

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
            # dx, dy + gyro + accel
            dx_str, dy_str, gx, gy, gz, ax, ay, az = data.decode().split(",")
            dx = float(dx_str)
            dy = float(dy_str)
            gx = float(gx)
            gy = float(gy)
            gz = float(gz)
            ax = float(ax)
            ay = float(ay)
            az = float(az)

            # Muove mouse
            mouse.move(dx, dy)

            # Stampa valori per debug
            print(f"dx={dx:.2f}, dy={dy:.2f} | gx={gx:.2f}, gy={gy:.2f}, gz={gz:.2f} | ax={ax:.2f}, ay={ay:.2f}, az={az:.2f}")

        except Exception as e:
            print(f"Errore parsing dati: {e}")

except KeyboardInterrupt:
    print("\nChiusura server...")
    conn.close()
    sock.close()
