#!/usr/bin/env python3
"""
All the fonctions that can be both used by the controller
and the ellisys laptop
"""
import yaml
import config

def write_logs(log_fname, log, how='a'):
    "Write to log"
    path = "./logs/" + log_fname + ".log"
    f = open(path, how)
    f.write(log)
    f.close()
    if how == "w":
        print("log file: " + path +" init")


def dump_yaml(data, fname):
    f = open(fname, "w")
    yaml.dump(data, f)
    f.close()


def get_action_numb(action, appName, data):


    if appName in data:
        actions = data[appName]
        if action in actions:
            return data, actions[action]
        else:
            data[appName][action] = 0
            return data, 0
    else:
        data[appName] = {action:0}
        return data, 0

# Read the applications info file
def read_app(app_fname):
    f = open(app_fname)
    l = f.read()
    f.close()
    apps = yaml.load(l)
    return apps



def flush_left_state_number():
    L = "000"  # Means a capture can contain maximum 999 experiences runs

    if not config.FLUSH_CAPTURE_NUMBER:
        return

    apps = read_app("left_state.yaml")
    init_numb = str(config.EXPERIENCE_NUMBER) + L
    init_numb = int(init_numb)
    for app in apps:
        if app == "lastCapture":
            continue
        for action in apps[app]:
            apps[app][action] = init_numb
    dump_yaml(apps, "left_state.yaml")
