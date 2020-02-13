#!/usr/bin/env python3
"""
All the fonctions that can be both used by the controller
and the ellisys laptop
"""
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
