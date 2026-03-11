# test_manual_calib_i2c.py
import smbus2
import time

# ---------------- CONFIG ----------------
I2C_ADDR = 0x68   # Indirizzo MPU6050
bus = smbus2.SMBus(1)

REG_PWR_MGMT_1   = 0x6B
REG_ACCEL_XOUT_H = 0x3B

map_axis = {
    'X': 0,  # 0=Asse X
    'Y': 1   # 1=Asse Y
}
sign = {'X': 1, 'Y': 1}  # Inverti se serve

# ---------------- FUNZIONI ----------------
def write_reg(reg, val):
    bus.write_byte_data(I2C_ADDR, reg, val)

def read_raw_accel():
    data = bus.read_i2c_block_data(I2C_ADDR, REG_ACCEL_XOUT_H, 6)
    ax = (data[0] << 8) | data[1]
    ay = (data[2] << 8) | data[3]
    az = (data[4] << 8) | data[5]
    # correzione segno (16bit signed)
    ax = ax - 65536 if ax > 32767 else ax
    ay = ay - 65536 if ay > 32767 else ay
    az = az - 65536 if az > 32767 else az
    return ax, ay, az

# ---------------- INIT MPU ----------------
write_reg(REG_PWR_MGMT_1, 0)  # sveglia MPU6050

# ---------------- CALIBRAZIONE FERMO ----------------
print("Mantieni il sensore fermo e piatto...")
time.sleep(2)
samples = [read_raw_accel() for _ in range(20)]
x_rest = sum(s[map_axis['X']] for s in samples)/len(samples)
y_rest = sum(s[map_axis['Y']] for s in samples)/len(samples)
print(f"Riposo: x={x_rest:.2f}, y={y_rest:.2f}\n")

# ---------------- LOOP PRINCIPALE ----------------
try:
    while True:
        ax, ay, az = read_raw_accel()
        dx = (ax - x_rest) * sign['X']
        dy = (ay - y_rest) * sign['Y']

        dir_x = "destra" if dx > 0 else ("sinistra" if dx < 0 else "fermo")
        dir_y = "su" if dy > 0 else ("giù" if dy < 0 else "fermo")

        print(f"dx={dx:+.0f} ({dir_x}) | dy={dy:+.0f} ({dir_y})")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nTest terminato.")
