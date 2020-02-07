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
import config




######################## MAIN ########################

###### Capture Preparation
# Read the applications info file
f = open("applications.yaml")
l = f.read()
f.close()
apps = yaml.load(l)

def write_logs(launchTime, log, how):
    f = open("./logs/"+ "capture-" + launchTime + ".yaml", how)
    f.write(log)
    f.close()


launchTime = time.strftime("%H:%M:%S", time.localtime())  # for log file name
write_logs(launchTime, "--- Log init ---  \n", 'w')
log = ""

##### Connection with the watch(es)

tries = 0

print("Accessing device(s)...")


devices = []
for device_addr in config.DEVICES:

    # Connects to the current device, returning a MonkeyDevice object
    device = None
    width = None
    lastFilename = ""
    lastApp = False  # Ensure we do not open and close twice

    while width is None:

        device = MonkeyRunner.waitForConnection(deviceId=device_addr, timeout=config.WATCH_CONNECTION_TIMEOUT)


        width = device.getProperty("display.width")
        height = device.getProperty("display.height")
        watchName = device.getProperty("build.model")

        time.sleep(0.5)
        if tries > 10:
            print("Connection with device error.\naborting...")
            sys.exit(1)
        tries += 1

    watchName = str(watchName.replace(" ", "-"))
    print("Device: " + watchName + " connected")
    devices.append((device, (int(width) - 1, int(height) -1), watchName))

print("All devices are connected")


# MAIN
if not config.DEBUG_WATCH:
    send_instruction(messages.CMD_OPEN_ELLISYS)


appNb = 0
log = ""

# Loop on applications
for appName in apps:
    if appName in config.KEEP_ONLY or len(config.KEEP_ONLY) == 0:

        appNb += 1

        # Extract info about applications
        app = apps[appName]
        package = app["package"]
        activity = app["activity"]
        actions = app["actions"]
        actionsKeepOnly = app["keepOnly"]
        lastApp = (appName == config.KEEP_ONLY[-1])

        # Loop on the set of actions of a patricular app
        for i, actionName in enumerate(actionsKeepOnly):
            i += 1

            # TODO: eval ? what's happening here ?
            action = [eval(a) for a in actions[actionName]]


            # Loop on a particular action
            for j in range(config.N_REPEAT_CAPTURE):
                j += 1

                # Loop on watches
                for deviceStruct in devices:
                    device = deviceStruct[0]
                    display = deviceStruct[1]
                    watchName = deviceStruct[2]
                    filename = watchName + "_" +appName +"_"+ actionName+ "_Classic_enc_" + str(j)
                    print(filename)

                    # Start capture
                    if not config.DEBUG_WATCH:
                        send_instruction(messages.NewStartCaptureCommand(payload=lastFilename))

                    #  launch action
                    time.sleep(config.WAITING_TIME_AFTER_START_CAPTURE)
                    infoSim = simulate(device, display, package, activity, action)
                    time.sleep(config.WAITING_TIME_BEFORE_STOP_CAPTURE)

                    # Stop Capture
                    if not config.DEBUG_WATCH:
                        send_instruction(messages.CMD_STOP_CAPTURE)
                        send_instruction(messages.NewSaveCaptureCommand(payload=filename))

                    log = filename + '\n' + infoSim
                    write_logs(launchTime, log, 'a')
                    lastFilename = ", " + filename
                    time.sleep(2)

        # Restart Ellisys
        if (config.RESTART_ELLISYS_WHEN_CHANGING_APP and len(actionsKeepOnly) != 0) and not appName == app and not config.DEBUG_WATCH:
            send_instruction(messages.CMD_CLOSE_ELLISYS)
            lastFilename = ""

            if appNb != len(config.KEEP_ONLY):
                time.sleep(10)  # Sleeping a bit before capturing new app
                send_instruction(messages.CMD_OPEN_ELLISYS)

print("done")
