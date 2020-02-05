#!/usr/bin/env python3

import socket
import os
import psutil

# TO CHANGE if not connected to mobnet
HOST = '192.168.1.101'  # IP address of this computer (reachable by the MAC)


PORT = 65432        # Port to listen on (no need to change)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))


print("Starting server")
while True:
        s.listen(5)
        client, address = s.accept()
        print("{} connected".format( address ))

        response = client.recv(255)
        response = response.decode('utf-8')
        print("-> " + response)

        if response == "open ellisys":
            print("<- Starting Ellisys")
            os.system('cmd /c "AutoIt3 au3Commands\\open_ellisys.au3"')
            client.sendall(b"Ellisys opened")
            print("<- Ellisys opened")

        if response == "close ellisys":

            os.system('cmd /c "AutoIt3 au3Commands\\close_ellisys.au3"')
            client.sendall(b"Ellisys closed")
            print("<- Ellisys closed")

        if response[:13] == "start capture":
            fname = response.split(", ")
            if len(fname) == 2:
                fname = fname[1]

                os.system('cmd /c "AutoIt3 au3Commands\\start_capture.au3 {}"'.format(fname))
            else:
                os.system('cmd /c "AutoIt3 au3Commands\\start_capture.au3"')
            client.sendall(b"Capture started")
            print("<- Capture started")

        if response == "stop capture":

            os.system('cmd /c "AutoIt3 au3Commands\\stop_capture.au3"')
            client.sendall(b"Capture stopped")
            print("<- capture stoped")

        if response[:12] == "save capture":
            fname = response.split(", ")[1]
            print("Saving capture: ", fname, ".btt")
            os.system('cmd /c "AutoIt3 au3Commands\\save_capture.au3 {}"'.format(fname))
            client.sendall(str.encode("Capture " +fname+" saved"))
        else:
            client.sendall(b"Failure. Command unkown")
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        print("   CPU usage: {}% \n   Memory usage: {}".format(cpu, ram))

print("Close")
client.close()
s.close()
