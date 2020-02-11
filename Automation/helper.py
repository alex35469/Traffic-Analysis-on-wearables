#!/usr/bin/env python3
"""
All the fonctions that can be both used by the controller
and the ellisys laptop
"""

def write_logs(log_fname, log, how):
    "Write to log"
    path = "./logs/" + log_fname + ".log"
    f = open(path, how)
    f.write(log)
    f.close()
    if how == "w":
        print("log file: " + path +" init")
