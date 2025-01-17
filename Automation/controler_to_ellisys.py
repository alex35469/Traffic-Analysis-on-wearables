#!/usr/bin/env python3

# Program that controls the communication with the computer controlling the ellisys.

import socket
import config
import longrun_config
import time
import sys
import messages
from helper import write_logs, tprint
import os

instr_to_required_state = {
    "open" : "open ellisys software on the Welcome page",
    "close" : "close ellisys",
    "start" : "start a capture",
    "startArgs" : "start a capture",
    "save" : "Save or focus a ellisys capture with the name: ",
    "stop" : "stop a capture, if buggy kill ellisys and stop a 'fake' capture"
}


def send_instruction(instruction, log_fname):

    if longrun_config.DEBUG_WATCH == True:
        return False

    errorEllisys = False

    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((config.ELLISYS_HOST, config.ELLISYS_PORT))

        currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        send_msg = '<- Sending "' + instruction + '"'
        tprint(send_msg, log_fname)
        s.sendall(str.encode(instruction))
        data = s.recv(config.SOCKET_RECEIVE_BUFFER)
        s.close()

        data = data.decode('utf-8')
        currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        rcv_msg = '-> Received "' + data + '"'
        tprint(rcv_msg, log_fname)

        msg = data.split(' ', 1)
        if msg[0] == messages.MESSAGE_FAIL:
            instructionSplited = instruction.split(' ', 1)
            payload = ""
            cmd = instructionSplited[0]
            if len(instructionSplited) == 2:
                payload = instructionSplited[1]
            if len(msg) == 2:
                if msg[1] == "EllisysErrorSave":
                    errorEllisys = True
                    return errorEllisys
                if msg[1] == "EllisysErrorStop":
                    errorEllisys = True
                    return errorEllisys



            print("'" + cmd + "', '" + payload + "'")
            os.system("spd-say 'Ellisys laptop stuck. Please come fix it!'")
            raw_input("timeout error. Ellisys program is stuck or is not responsive.\n Fix it to the required state: : '" + instr_to_required_state[cmd] + payload + "' press enter to continue: ")
            print("issuing the command again. Keep in mind that the capture "+ payload + " might be corrupted")
            break

        return errorEllisys
