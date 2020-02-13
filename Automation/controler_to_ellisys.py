#!/usr/bin/env python3

# Program that controls the communication with the computer controlling the ellisys.

import socket
import config
import time
import sys
import messages
from helper import write_logs

def send_instruction(instruction, log_fname):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.ELLISYS_HOST, config.ELLISYS_PORT))

    currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
    send_msg = ' [' + currentTime + '] -> Sending "' + instruction + '"'
    print(send_msg)
    s.sendall(str.encode(instruction))
    data = s.recv(config.SOCKET_RECEIVE_BUFFER)
    s.close()

    data = data.decode('utf-8')
    currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
    rcv_msg = ' [' + currentTime + '] <- Received "' + data + '"'
    print(rcv_msg)
    if data.split(' ', 1)[0] == messages.MESSAGE_FAIL:
        print("timeout error. \naborting")
        sys.exit(1)

    comm = send_msg + '\n' + rcv_msg
    write_logs(log_fname, comm + '\n')
