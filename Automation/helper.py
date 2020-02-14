#!/usr/bin/env python3
"""
All the fonctions that can be both used by the controller
and the ellisys laptop
"""
import time
import yaml
def write_logs(log_fname, log, how='a'):
    "Write to log"
    path = "./logs/" + log_fname + ".log"
    f = open(path, how)
    f.write(log)
    f.close()
    if how == "w":
        print("log file: " + path +" init")



# Read the applications info file
def read_app(app_fname):
    f = open(app_fname)
    l = f.read()
    f.close()
    apps = yaml.load(l)
    return apps


def tprint(txt, log_fname=None):
    "Print with time and log to file"

    currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
    txt = ' [' + currentTime + '] ' + txt
    print(txt)
    if log_fname != None:
        write_logs(log_fname, txt + '\n')
