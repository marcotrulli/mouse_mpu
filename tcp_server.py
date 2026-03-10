import socket
import struct
import pyautogui

PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

print("Server avviato...")

while True:

    data, addr = sock.recvfrom(1024)

    dx, dy = struct.unpack("bb", data)

    pyautogui.moveRel(dx, dy)
