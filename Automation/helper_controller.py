#!/usr/bin/env python3
"""
Helper fonction that is used only by the controller
"""
import yaml
import config


def dump_yaml(data, fname):
    """
    Take a dict and writes its content un a yaml file
    Args:
        data: dict. Dict to dump into file
        fname: string. Path and file name where to dump data
    Return:
        None
    """

    f = open(fname, "w")
    yaml.dump(data, f)
    f.close()


def get_action_numb(action, app, data):
    """
    Give the last event number for a particular app - action pair.
    Args:
        action : string. Name of the action
        app : string. Name of the app
        data : dict[app][action] = event_nb.
    Return:
        data : dict[app][action] = event_nb. Updated
        event_nb : int. Last envent number.
    """

    if app in data:
        actions = data[app]
        if action in actions:
            return data, actions[action]
        else:
            data[app][action] = 0
            return data, 0
    else:
        data[appName] = {action:0}
        return data, 0


def read_app(app_fname):
    """
    Read applications settings file into dictionary
    Args:
        app_fname: String. Apps data file name
    Return:
        Dict. Contains app data
    """
    f = open(app_fname)
    l = f.read()
    f.close()
    apps = yaml.load(l)
    return apps



def flush_left_state_number():
    """
    Reset the left_state.yaml file with the corresponding Experience Number
    """
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
