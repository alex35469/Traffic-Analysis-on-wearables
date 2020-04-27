#!/usr/local/bin/python3

import os
import glob
import sys

errors = []

PATH_CSV = "/Users/alexandredumur/Desktop/actions/D/"
PATH_BTT = "/Users/alexandredumur/Desktop/actions/D/"

if PATH_BTT == "":
    PATH_CSV + PATH_CSV[PATH_CSV[:-1].rfind("/")+1:-1] + "_btt/"

def parse(file, PATH, EXTENTION):
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

EXTENTION_CSV = ".csv"
EXTENTION_BTT = ".btt"


counts_btt = dict()

def count_classes(PATH, EXTENTION):
    files = glob.glob(PATH + '*'+EXTENTION, recursive=False)
    counts = dict()

    for file in files:

        device, app, action, ble, enc, repeat = parse(file, PATH, EXTENTION)

        if not device in counts:
            counts[device] = dict()
        if not app in counts[device]:
            counts[device][app] = dict()
        if not action in counts[device][app]:
            counts[device][app][action] = 0

        counts[device][app][action] += 1
    return counts



counts_csv = count_classes(PATH_CSV, EXTENTION_CSV)
counts_btt = count_classes(PATH_BTT, EXTENTION_BTT)

missing = set()

for d in counts_csv:
    for a in counts_csv[d]:
        for a2 in counts_csv[d][a]:
            try:
                cbtt = counts_btt[d][a][a2]
            except KeyError:
                missing.add(d + "_" + a + "_" + a2)
                continue

            print(d,a,a2, counts_csv[d][a][a2], counts_btt[d][a][a2])
            if counts_btt[d][a][a2] != counts_csv[d][a][a2]:
                missing.add(d + "_" + a + "_" + a2)
print("CAREFULL Missing data:")

print(missing)


for  i in missing:
    parts = i.split('_')
    d = parts[0]
    a = parts[1]
    a1 = parts[2]
    try:
        cbtt = counts_btt[d][a][a2]
    except KeyError:
        cbtt = 0
        continue

    print(d,a,a2, counts_csv[d][a][a2], cbtt)

# fix errors
for e in errors:
    print(e)
