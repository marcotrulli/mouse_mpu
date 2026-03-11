# test_axes.py
import smbus2
import time

# MPU6050 registri
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
    # Converti da 2’s complement
    x = x - 65536 if x > 32767 else x
    y = y - 65536 if y > 32767 else y
    z = z - 65536 if z > 32767 else z
    return x, y, z

print("Tieni fermo il sensore...")
time.sleep(2)

# Legge i valori di riposo
x0, y0, z0 = read_accel()
print(f"Valori a riposo: X={x0}, Y={y0}, Z={z0}")

for axis in ['X', 'Y', 'Z']:
    input(f"\nMuovi solo l'asse {axis} e premi INVIO per iniziare...")
    print(f"Misurando {axis}...")
    for _ in range(20):
        x, y, z = read_accel()
        dx, dy, dz = x - x0, y - y0, z - z0
        print(f"Delta X={dx}, Delta Y={dy}, Delta Z={dz}")
        time.sleep(0.1)
