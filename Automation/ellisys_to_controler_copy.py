#!/usr/bin/env python3

import socket
import os
import psutil
import messages
import config

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((config.ELLISYS_HOST, config.ELLISYS_PORT))

def autoItRunAndWait(file):
    print('Running AutoIT file "AutoIt3 au3Commands\\' + file + '"'
    os.system('cmd /c "AutoIt3 au3Commands\\ + file)

def printCPUMemoryLogs():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    print("CPU usage: " + cpu + "%, Memory usage: " + ram

def sendAck(client, payload):
    print('Sending ACK message with payload "' + payload + '"'
    message = str.encode(messages.NewACK(payload))
    client.sendall(message)

print("Starting server...")

while True:
        s.listen(5)
        client, address = s.accept()
        print("New client: " + address + ", waiting on command")

        # receive command
        response = client.recv(config.SOCKET_RECEIVE_BUFFER) # TODO: increased from 255 to 1024 (to avoid having an extra magic number), maybe it will cause problems ? to check
        response = response.decode('utf-8')

        # parse
        command, payload = response, ''
        if ',' in response:
            parts = response.split(',')
            command = parts[0].strip()
            payload = parts[1].strip()

        print('-> Received message "' + response + '"", parsed as "' + command + '" args "payload"'
        if command == messages.CMD_OPEN_ELLISYS:
            autoItRunAndWait('open_ellisys.au3')
            sendAck(client, "Ellisys opened")

        elif command == messages.CMD_CLOSE_ELLISYS:
            autoItRunAndWait('close_ellisys.au3')
            sendAck(client, "Ellisys closed")

        # The file name is needed in order to AutoIt
        # to know which windws to activate (when saving a file the window name
        # changes as well)
        elif command == messages.CMD_START_CAPTURE:
            if payload != '': #TODO: if that's not needed anymore, remove
                filename = payload
                autoItRunAndWait('start_capture.au3 ' + filename)
            else:
                autoItRunAndWait('start_capture.au3')
            sendAck(client, "Capture started")

        elif command == messages.CMD_STOP_CAPTURE:
            autoItRunAndWait('stop_capture.au3')
            sendAck(client, "Capture stopped")

        elif command == messages.CMD_SAVE_CAPTURE:
            filename = payload
            autoItRunAndWait('save_capture.au3 ' + filename)
            sendAck(client, "Capture " +filename + " saved")

        else:
            sendAck(client, "Failure. Command unknown.")

        printCPUMemoryLogs()

print("Server closed")
client.close()
s.close()
