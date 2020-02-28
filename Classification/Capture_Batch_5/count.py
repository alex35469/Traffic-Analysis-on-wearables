#!/usr/local/bin/python3

import os
import glob
import sys

errors = []
PATH = 'data/open_2/'
def parse(file):
    name = file.replace(PATH, '').replace(EXTENTION, '')
    parts = name.split('_')
    if len(parts) == 4:
        device = parts[0].strip()
        ble = parts[1].strip()
        enc = parts[2].strip()
        repeat = parts[3].strip()

        try:
            repeat = int(repeat)
        except:
            repeat = None
        return device, "NoApp", "NoAction", ble, enc, repeat
    elif len(parts) == 5:
        device = parts[0].strip()
        action = parts[1].strip()
        ble = parts[2].strip()
        enc = parts[3].strip()
        repeat = parts[4].strip()

        try:
            repeat = int(repeat)
        except:
            repeat = None
        return device, "NoApp", action, ble, enc, repeat
    else:
        device = parts[0].strip()
        app = parts[1].strip()
        action = parts[2].strip()
        ble = parts[3].strip()
        enc = parts[4].strip()
        repeat = parts[5].strip()

        try:
            repeat = int(repeat)
        except:
            repeat = None
        return device, app, action, ble, enc, repeat

EXTENTION = ".csv"

counts = dict()

files = glob.glob(PATH + '*'+EXTENTION, recursive=False)
for file in files:

    device, app, action, ble, enc, repeat = parse(file)

    if not device in counts:
        counts[device] = dict()
    if not app in counts[device]:
        counts[device][app] = dict()
    if not action in counts[device][app]:
        counts[device][app][action] = 0

    counts[device][app][action] += 1

print(counts)

for d in counts:
    for a in counts[d]:
        for a2 in counts[d][a]:
            print(d,a,a2,counts[d][a][a2])


# fix errors
for e in errors:
    print(e)
