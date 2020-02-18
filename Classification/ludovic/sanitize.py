#!/usr/local/bin/python3

import os
import glob
import sys

errors = []

def parse(file):
    name = file.replace('data/', '').replace(EXTENTION, '')
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

labels=dict()
labels['device'] = set()
labels['app'] = set()
labels['action'] = set()
labels['ble'] = set()
labels['enc'] = set()
labels['repeat'] = set()

EXTENTION = ".btt"
    
files = glob.glob('data/*'+EXTENTION, recursive=False)
for file in files:
    
    device, app, action, ble, enc, repeat = parse(file)
    
    labels['device'].add(device)
    labels['app'].add(app)
    labels['action'].add(action)
    labels['ble'].add(ble)
    labels['enc'].add(enc)
    labels['repeat'].add(repeat)
    
    #print(file, device, app, action, ble, enc, repeat)
            
    if False and device == 'AS80':
        device = 'BeurerAS80'

        newname = "data/"+"_".join([str(x) for x in [device, app, action, ble, enc, repeat]])+EXTENTION
        print("Would rename", file, "to", newname)
        os.rename(file, newname)


    if False and app is None or action is None:
        if app is None:
            app = "NoApp"
        if action is None:
            action = "NoAction"
        newname = "data/"+"_".join([str(x) for x in [device, app, action, ble, enc, repeat]])+EXTENTION
        print("Would rename", file, "to", newname)
        #os.rename(file, newname)
    
    if False and device == "Samsung":
        newname = file.replace("Samsung_", "SamsungGalaxyWatch_")
        print("Would rename", file, "to", newname)
        #os.rename(file, newname)
    
    if False and "Water" in file:
        parts = file.split("_")
        app = parts[2]
        if "endomondo" in app.lower():
            app = "Endomondo"
        elif "fitiv" in app.lower():
            app = "FITIV"
        elif "mapmyrun" in app.lower():
            app = "MapMyRun"
        elif "pear" in app.lower():
            app = "Pear"
        elif "myfitnesspal" in app.lower():
            app = "MyFitnessPal"
        elif "sh" in app.lower():
            app = "SamsungHealth"
        newname = "data/Samsung_MyFitnessPal_WaterAdd_Classic_enc_" + parts[-1]
        print("Would rename", file, "to", newname)
        #os.rename(file, newname)

print('Devices:', labels['device'])
print('App:', labels['app'])
print('Action:', labels['action'])
print('BLE:', labels['ble'])
print('Enc:', labels['enc'])
print('Repeat:', labels['repeat'])
        
# fix errors
for e in errors:
    print(e)