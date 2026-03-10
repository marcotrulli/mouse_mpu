import socket
import json
import time
from mpu_reader import MPUReader

# ===== CONFIGURAZIONE =====
PC_IP = "192.168.1.179"  # Inserisci l'IP del PC
PC_PORT = 5005            # Porta TCP del server sul PC
SEND_INTERVAL = 0.05      # Frequenza di invio dati (20 Hz)

# ===== INIZIALIZZAZIONE SENSORE =====
sensor = MPUReader()  # Si calibra automaticamente a riposo

# ===== CREAZIONE SOCKET TCP =====
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"Connessione al PC {PC_IP}:{PC_PORT} ...")
    try:
        s.connect((PC_IP, PC_PORT))
    except Exception as e:
        print("Impossibile connettersi al PC:", e)
        exit(1)
    print("Connesso! Invio dati MPU...")

    try:
        while True:
            # Legge dati filtrati dal sensore
            data = sensor.read_filtered()

            # Prepara payload JSON compatibile con il server
            payload = {"dx": data["dx"], "dy": -data["dy"]}

            # Invia al server TCP, aggiunge newline come separatore
            try:
                s.sendall((json.dumps(payload) + "\n").encode())
            except Exception as e:
                print("Errore invio dati:", e)
                break

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("Chiusura in corso...")

    except Exception as e:
        print("Errore imprevisto:", e)

print("Programma terminato.")
