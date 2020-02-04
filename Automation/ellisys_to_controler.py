#!/usr/bin/env python3

import socket
import os

HOST = '192.168.1.101'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

"""
print("Starting server")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
"""

print("Starting server")
while True:
        s.listen(5)
        client, address = s.accept()
        print("{} connected".format( address ))

        response = client.recv(255)
        response = response.decode('utf-8')
        print(response)

        # Check that the message is correct
        if len(response) < 12:
            print("Incorrect command: ", response)
            client.sendall(b"Command unkown")

        if response == "start ellisys":
            print("Starting Ellisys")
            os.system('cmd /c "AutoIt3 au3Commands\\open_ellisys.au3"')
            client.sendall(b"Ellisys started")

        if response == "stop ellysis":
            print("Stopping Ellisys")
            os.system('cmd /c "AutoIt3 au3Commands\\close_ellisys.au3"')
            client.sendall(b"Ellisys au3Commands\\stopped")

        if response == "start capture":
            print("Starting capture")
            os.system('cmd /c "AutoIt3 au3Commands\\start_capture.au3"')
            client.sendall(b"Capture started")

        if respone[:12] == "save capture":
            fname = response.split(", ")
            print("Stopping capture")
            os.system('cmd /c "AutoIt3 au3Commands\\stop_capture.au3"')

            print("Saving capture: ", fname)
            os.system('cmd /c "AutoIt3 au3Commands\\save_capture.au3"')
            client.sendall(b"Capture stopped and saved")

print("Close")
client.close()
s.close()
