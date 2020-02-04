#!/usr/bin/env python3

# Program that controls the communication with the computer controlling the ellisys.

import socket

HOST = '192.168.1.101'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


def send_instruction(instruction):
    instructions = ["start ellisys", "stop ellisys", "start capture", "save capture"]
    if instruction not in instructions:
        print("falls instruction")
        raise AttributeError("Should be either: " + ", ".join(instructions))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(instruction)
    data = s.recv(1024)
    s.close()

    return data

data = send_instruction("start ellisys")
print repr(data)
print type(data)
