#!/usr/bin/env python3

import socket
import os
import psutil
import messages
import config

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((config.ELLISYS_HOST, config.ELLISYS_PORT))

def autoItRunAndWait(file):
    print('Running AutoIT file "AutoIt3 au3Commands\\{0}"'.format(file))
    os.system('cmd /c "AutoIt3 au3Commands\\{0}"'.format(file))

def printCPUMemoryLogs():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    print("CPU usage: {}%, Memory usage: {}".format(cpu, ram))

def sendAck(client, payload):
    print('Sending ACK message with payload "{0}"'.format(payload))
    message = str.encode(messages.NewACK(payload))
    client.sendall(message)

print("Starting server...")
while True:
        s.listen(5)
        client, address = s.accept()
        print("New client: {}, waiting on command".format( address ))

        # receive command
        response = client.recv(config.SOCKET_RECEIVE_BUFFER) # TODO: increased from 255 to 1024 (to avoid having an extra magic number), maybe it will cause problems ? to check
        response = response.decode('utf-8')

        # parse
        command, payload = response, ''
        if ',' in response:
            parts = response.split(',')
            command = parts[0].strip()
            payload = parts[1].strip()

        print('-> Received message "{0}", parsed as "{1}" args "{2}"'.format(response, command, payload))

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
            if payload != '':
                filename = payload
                autoItRunAndWait('start_capture.au3 {}'.format(filename))
            else:
                autoItRunAndWait('start_capture.au3')
            sendAck(client, "Capture started")

        elif command == messages.CMD_STOP_CAPTURE:
            autoItRunAndWait('stop_capture.au3')
            sendAck(client, "Capture stopped")

        elif command == messages.CMD_SAVE_CAPTURE:
            filename = payload
            autoItRunAndWait('save_capture.au3 {}'.format(filename))
            sendAck(client, "Capture " +filename + " saved")

        else:
            sendAck(client, "Failure. Command unknown.")

        printCPUMemoryLogs()

print("Server closed")
client.close()
s.close()
