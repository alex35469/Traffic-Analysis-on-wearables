#!/usr/bin/env python3

# Program that controls the communication with the computer controlling the ellisys.

import socket

HOST = '192.168.1.101'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


def send_instruction(instruction):
    instructions = ["open ellisys", "close ellisys", "start capture", "stop capture"]
    if instruction not in instructions and instruction[:12] != "save capture" and instruction[:13] != "start capture":
        raise AttributeError("Should be either: " + ", ".join(instructions))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(str.encode(instruction))
    data = s.recv(1024)
    s.close()
    print(" -> " + data.decode('utf-8'))
    return data
