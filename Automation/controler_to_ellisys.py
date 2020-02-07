#!/usr/bin/env python3

# Program that controls the communication with the computer controlling the ellisys.

import socket
import config

def send_instruction(instruction):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.ELLISYS_HOST, config.ELLISYS_PORT))

    print(' -> Sending "' + instruction + '"')
    s.sendall(str.encode(instruction))
    data = s.recv(config.SOCKET_RECEIVE_BUFFER)
    s.close()

    data = data.decode('utf-8')
    print(' <- Received "' + data + '"')
    return data
