#!/usr/bin/env python3

import socket
import os
import psutil
import messages
import config
import subprocess
import sys
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((config.ELLISYS_HOST, config.ELLISYS_PORT))

def write_logs(launchTime, log, how):
    fname = "./logs/ellisys_" + launchTime + ".log"
    f = open(fname, how)
    f.write(log)
    f.close()
    if how == "w":
        print("log file: " + fname +" init")

def autoItRunAndWait(file):
    print('Running AutoIT file "AutoIt3 au3Commands\\{0}"'.format(file))
    p = subprocess.Popen('cmd /c "AutoIt3 au3Commands\\{0}"'.format(file))
    successfull = True
    try:
        p.wait(config.ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED)
    except subprocess.TimeoutExpired:
        p.kill()
        successfull = False

    return successfull


def printCPUMemoryLogs():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
    sysInfo = ' [' + currentTime + '] CPU usage: {}%, Memory usage: {}'.format(cpu, ram)
    print(sysInfo)
    return sysInfo

def sendAck(client, payload):
    print('Sending ACK message with payload "{0}"'.format(payload))
    message = str.encode(messages.NewACK(payload))
    client.sendall(message)

def sendFail(client, payload):
    print('"Sending a FAIL message with payload "{0}"'.format(payload))
    message = str.encode(messages.NewFAIL(payload))
    client.sendall(message)


launchTime = time.strftime("%d-%m-%y_%H-%M-%S", time.localtime()) # for log file name
write_logs(launchTime, "--- Log init ---  \n", 'w')
log = ""

print("Starting server...")
while True:
        s.listen(5)
        client, address = s.accept()
        print("New client: {}, waiting on command".format( address ))

        # receive command
        response = client.recv(config.SOCKET_RECEIVE_BUFFER).decode('utf-8')

        # parse
        command, payload = response, ''
        if ' ' in response:
            parts = response.split(' ', 1)
            command = parts[0].strip()
            payload = parts[1].strip()

        currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        print(' [' + currentTime + '] -> Received message "{0}", parsed as "{1}" args "{2}"'.format(response, command, payload))


        if command == messages.CMD_OPEN_ELLISYS:
            successfull = autoItRunAndWait('open_ellisys.au3')
            if successfull:
                sendAck(client, "Ellisys opened")

        elif command == messages.CMD_CLOSE_ELLISYS:
            successfull = autoItRunAndWait('close_ellisys.au3')
            if successfull:
                sendAck(client, "Ellisys closed")

        # The file name is needed in order to AutoIt
        # to know which windws to activate (when saving a file the window name
        # changes as well)
        elif command == messages.CMD_START_CAPTURE:
            if payload != '':
                filename = payload
                successfull = autoItRunAndWait('start_capture.au3 {}'.format(filename))
            else:
                successfull = autoItRunAndWait('start_capture.au3')
            if successfull:
                sendAck(client, "Capture started")

        elif command == messages.CMD_STOP_CAPTURE:
            successfull = autoItRunAndWait('stop_capture.au3')
            if successfull:
                sendAck(client, "Capture stopped")

        elif command == messages.CMD_SAVE_CAPTURE:
            filename = payload
            successfull = autoItRunAndWait('save_capture.au3 {}'.format(filename))
            if successfull:
                sendAck(client, "Capture " +filename + " saved")

        else:
            sendFail(client, "Command unknown.")

        sysInfo = printCPUMemoryLogs()
        write_logs(launchTime, sysInfo, "a")

        if not successfull:
            sendFail(client, "AutoIt command time out: {}s reached ".format(config.ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED))
            autoItRunAndWait('close_ellisys.au3')
            time.sleep(10)
            autoItRunAndWait("open_ellisys.au3")


print("Server closed")
client.close()
s.close()
