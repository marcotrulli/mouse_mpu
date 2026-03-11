# manual_axis_test.py
import smbus2
import time

# Configurazione MPU6050
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)  # sveglia MPU

def read_accel():
    data = bus.read_i2c_block_data(MPU_ADDR, ACCEL_XOUT_H, 6)
    x = (data[0] << 8 | data[1])
    y = (data[2] << 8 | data[3])
    z = (data[4] << 8 | data[5])
    # Converti da 2's complement
    x = x - 65536 if x > 32767 else x
    y = y - 65536 if y > 32767 else y
    z = z - 65536 if z > 32767 else z
    return x, y, z

# Chiedi quale asse vuoi testare
axis = input("Quale asse vuoi testare? (X/Y/Z): ").upper()
if axis not in ['X', 'Y', 'Z']:
    print("Asse non valido!")
    exit(1)

# Leggi valori a riposo
x0, y0, z0 = read_accel()
print(f"Valori a riposo: X={x0}, Y={y0}, Z={z0}")
print("Muovi l'asse selezionato. Premi INVIO per fermare.")

# Loop finché l’utente non preme INVIO
try:
    while True:
        x, y, z = read_accel()
        dx = x - x0
        dy = y - y0
        dz = z - z0

        if axis == 'X':
            print(f"Delta X = {dx}")
        elif axis == 'Y':
            print(f"Delta Y = {dy}")
        elif axis == 'Z':
            print(f"Delta Z = {dz}")

        # Controllo se INVIO è premuto senza bloccare
        import sys, select
        if select.select([sys.stdin], [], [], 0)[0]:
            break

        time.sleep(0.1)
except KeyboardInterrupt:
    pass

print("Test terminato.")
