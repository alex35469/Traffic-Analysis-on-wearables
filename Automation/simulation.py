# Main script
# Simulate touch on the watch


from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_moves import *
sys.path.append(r"/Users/alexandredumur/Documents/EPFL/PDM/Traffic-Analysis_on_wearables/Automation/yaml")
import yaml
from controler_to_ellisys import send_instruction


################## PARAMETERS ########################
addr = "192.168.1.134:5555"  # Watch ip address. Change if not connected to Mobnet
watchName = "HuaweiWatch2"  # Hardcoded for now...
repeat = 2  # Number of time to repeat action.
timeout = 3  # timeout after watch not connected (First instruction)
skipOpenAndClose = False
restartEllisysWhenChangingApp = True
DEBUG_WATCH = False  # Does not communiacte with ellisys controller

# Applications to keep for the automation
# To see what action to simulate, see application_action.yaml under keepOnly field
keepOnly = ["Daily_tracking", "DCML_Radio", "Endomondo"]
blacklist = []  # TODO Does not work yet


######################## MAIN ########################

###### Capture Preparation
# Read the applications info file
f = open("applications.yaml")
l = f.read()
f.close()
apps = yaml.load(l)

launchTime = time.strftime("%H:%M:%S", time.localtime())  # for log file name

# Connects to the current device, returning a MonkeyDevice object
device = None
width = None
lastInfo = ""
lastApp = False  # Ensure we do not open and close twice

##### Connection with the watch
# Ensure that the connection proprely worked
tries = 0
while width is None:

    device = MonkeyRunner.waitForConnection(deviceId=addr, timeout=timeout)


    width = device.getProperty("display.width")
    height = device.getProperty("display.height")
    time.sleep(0.5)
    if tries > 15:
        print("Connection with device error.\naborting...")
        sys.exit(1)

print("Device accessed")
width = int(width) - 1
height = int(height) - 1
display = (width, height)



# MAIN
if not DEBUG_WATCH:
    print("<- open ellisys")
    send_instruction("open ellisys")
else:
    repeat = 1

appNb = 0
log = ""

# Loop on applications
for appName in apps:
    if appName in keepOnly or len(keepOnly) == 0:


        if appName in blacklist:
            continue

        appNb += 1

        # Extract info about applications
        info = appName
        app = apps[appName]
        package = app["package"]
        activity = app["activity"]
        actions = app["actions"]
        actionsKeepOnly = app["keepOnly"]
        lastApp = (appName == keepOnly[-1])

        # Loop on the set of actions of a patricular app
        for i, action in enumerate(actions):
            i += 1
            if (skipOpenAndClose and i == 1) or i not in actionsKeepOnly:
                continue

            action = [eval(a) for a in action]

            # Loop on a particular action
            for j in range(repeat):
                j += 1
                info = watchName + "_" +appName +"_Action"+ str(i)+ "_Classic_enc_" + str(j) + " : "
                print(info)

                # Start capture
                if not DEBUG_WATCH:
                    print(" <- start capture")
                    send_instruction("start capture" + lastInfo)

                #  launch action
                infoSim = simulate(device, display, package, activity, action)

                # Stop Capture
                if not DEBUG_WATCH:
                    print(" <- stop capture")
                    send_instruction("stop capture")
                    print(" <- save capture, " + info[:-3])
                    send_instruction("save capture, " + info[:-3])

                log += info + '\n' + infoSim
                lastInfo = ", " + info
                time.sleep(2)

        # Restart Ellisys
        if (restartEllisysWhenChangingApp and len(actionsKeepOnly) != 0) and not appName == app and not DEBUG_WATCH:
            print("<- close ellisys")
            send_instruction("close ellisys")
            lastInfo = ""

            if appNb != len(keepOnly):
                time.sleep(10)  # Sleeping a bit before capturing new app
                print("<- open ellisys")
                send_instruction("open ellisys")



print("---- LOG -----")
print(log)



f = open("./logs/"+ "capture-" + launchTime + ".yaml", "w")
f.write(log)
f.close()
print("done")
