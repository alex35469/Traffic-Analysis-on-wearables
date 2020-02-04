# Skeleton of the monkeyrunner instructions
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_moves import *
sys.path.append(r"/Users/alexandredumur/Documents/EPFL/PDM/Traffic-Analysis_on_wearables/Automation/yaml")
import yaml
import logging
import controler_to_ellisys

launchTime = time.strftime("%H:%M:%S", time.localtime())


# Param
repeat = 3
addr = "192.168.1.134:5555"
timeout = 3
skipOpenAndClose = True

# Applications to test
keepOnly = ["DCML Radio"]

# Read the applications info file
f = open("applications.yaml")
l = f.read()
f.close()

apps = yaml.load(l)



# Connects to the current device, returning a MonkeyDevice object
device = None
width = None

# Ensure that the connection proprely worked
tries = 0
while width is None:
    device = MonkeyRunner.waitForConnection(deviceId=addr, timeout=timeout)

    print(device.getProperty("display.width"))

    width = device.getProperty("display.width")
    height = device.getProperty("display.height")
    time.sleep(0.5)
    if tries > 15:
        print("Connection error.\naborting...")
        sys.exit(1)

width = int(width) - 1
height = int(height) - 1
display = (width, height)






# MAIN
# Scam all applications
log = ""
for appName in apps:
    if appName in keepOnly:
        info = appName
        app = apps[appName]
        package = app["package"]
        activity = app["activity"]
        actions = app["actions"]

        # Loop on the set of actions of a patricular app
        for i, action in enumerate(actions):
            if skipOpenAndClose and i == 0:
                continue

            action = [eval(a) for a in action]

            # Loop on a particular action
            for j in range(repeat):
                info = appName + " Action "+ str(i+1)+ " - " + str(j + 1) + " : "
                print(info)
                infoSim = simulate(device, display, package, activity, action)
                log += info + '\n' + infoSim
                time.sleep(2)
print("----")
print(log)


f = open("./logs/"+ "capture-" + launchTime + ".yaml", "w")
f.write(log)
f.close()
print("done")
