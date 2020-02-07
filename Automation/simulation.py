# Main script
# Simulate touch on the watch
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_moves import *
#TODO: not portable, put a relative path
sys.path.append(r"/Users/alexandredumur/Documents/EPFL/PDM/Traffic-Analysis_on_wearables/Automation/yaml")
import yaml
from controler_to_ellisys import send_instruction
import messages

################## PARAMETERS ########################
# TODO: move this in config.py, give very explicit names like "N_REPEAT_CAPTURE" instead of "repeat", etc.
addr = "192.168.1.134:5555"  # Watch ip address. Change if not connected to Mobnet
watchName = "HuaweiWatch2"  # Hardcoded for now...
repeat = 300  # Number of time to repeat action.
timeout = 3  # timeout after watch not connected (First instruction)
skipOpenAndClose = False
restartEllisysWhenChangingApp = True

#TODO: All constants as UPPER_CASE like this
DEBUG_WATCH = False  # Does not communiacte with ellisys controller

# Applications to keep for the automation
# To see what action to simulate, see application_action.yaml under keepOnly field
keepOnly = ["DiabeteM"] #, "DailyTracking", "DCMLRadio"]
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
    if tries > 10:
        print("Connection with device error.\naborting...")
        sys.exit(1)
    tries += 1

print("Device accessed")
width = int(width) - 1
height = int(height) - 1
display = (width, height)


# MAIN
if not DEBUG_WATCH:
    send_instruction(messages.CMD_OPEN_ELLISYS)


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
        for i, actionName in enumerate(actions):
            i += 1
            if (skipOpenAndClose and i == 1) or i not in actionsKeepOnly:
                continue

            # TODO: eval ? what's happening here ?
            action = [eval(a) for a in actions[actionName]]


            # Loop on a particular action
            for j in range(repeat):
                j += 1
                # TODO: rename in "filename" or something clearer
                info = watchName + "_" +appName +"_Action"+ str(i)+ "_Classic_enc_" + str(j) + " : "
                print("Info:", info)

                # Start capture
                if not DEBUG_WATCH:
                    send_instruction(messages.NewStartCaptureCommand(payload=lastInfo))

                #  launch action
                infoSim = simulate(device, display, package, activity, action)

                # Stop Capture
                if not DEBUG_WATCH:
                    send_instruction(messages.CMD_STOP_CAPTURE)

                    # TODO: why -3 here ? explain / make clearer. If it's to cut the extention, use the correct python thingy to do it (os.path....)
                    send_instruction(messages.NewSaveCaptureCommand(payload=info[:-3]))

                log += info + '\n' + infoSim

                #TODO: what's the use of "lastInfo" in this context ? does it build up in the loop ?
                lastInfo = ", " + info
                time.sleep(2)

        # Restart Ellisys
        if (restartEllisysWhenChangingApp and len(actionsKeepOnly) != 0) and not appName == app and not DEBUG_WATCH:
            send_instruction(messages.CMD_CLOSE_ELLISYS)
            lastInfo = ""

            if appNb != len(keepOnly):
                time.sleep(10)  # Sleeping a bit before capturing new app
                send_instruction(messages.CMD_OPEN_ELLISYS)



# TODO: Ah, I see. Don't do that: if the program crashes, this is never executed. Have a "log()" function which prints to stdout *and* to a file continuously called in the loop, not only at the end

print("---- LOG -----")
print(log)



f = open("./logs/"+ "capture-" + launchTime + ".yaml", "w")
f.write(log)
f.close()
print("done")
