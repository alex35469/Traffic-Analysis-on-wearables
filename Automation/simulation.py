# Main script
# Simulate touch on the watch
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_moves import *
sys.path.append(r"./yaml")
import yaml
from controler_to_ellisys import send_instruction
import messages
import config
from java.util.logging import Level, Logger, StreamHandler, SimpleFormatter
from java.io import ByteArrayOutputStream
import signal
import subprocess



######################## MAIN ########################

def main():
    ###### Capture Preparation
    # Read the applications info file
    f = open("applications.yaml")
    l = f.read()
    f.close()
    apps = yaml.load(l)

    def write_logs(launchTime, log, how):
        fname = "./logs/" + launchTime + ".log"
        f = open(fname, how)
        f.write(log)
        f.close()
        if how == "w":
            print("log file: " + fname +" init")



    launchTime = time.strftime("%d-%m-%y_%H-%M-%S", time.localtime()) # for log file name
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

    appNb = 0
    log = ""
    comm_log_start = ""
    comm_log_stop = ""
    comm_log_save = ""

    # MAIN
    if not config.DEBUG_WATCH:
        log = send_instruction(messages.CMD_OPEN_ELLISYS)





    # Loop on applications
    for appName in config.KEEP_ONLY:


        appNb += 1

        # Extract info about applications
        app = apps[appName]
        package = app["package"]
        activity = app["activity"]
        actions = app["actions"]
        actionsKeepOnly = app["keepOnly"]
        lastApp = (appName == config.KEEP_ONLY[-1])

        # Loop on the set of actions of a patricular app
        for actionName in actionsKeepOnly:

            # Parse the actions contained in applications.yaml
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
                        comm_log_start = send_instruction(messages.NewStartCaptureCommand(payload=lastFilename)) + '\n'


                    #  launch action
                    time.sleep(config.WAITING_TIME_AFTER_START_CAPTURE)
                    simulation_log, infoCheck = simulate(device, display, package, activity, action, config.PHONE_NAME, check=config.PERFORM_EXTRA_CHECK)
                    time.sleep(config.WAITING_TIME_BEFORE_STOP_CAPTURE)


                    # Stop Capture
                    if not config.DEBUG_WATCH:
                        com_log_stop = send_instruction(messages.CMD_STOP_CAPTURE) + '\n'
                        com_log_save = send_instruction(messages.NewSaveCaptureCommand(payload=filename)) + '\n'

                    log = filename + '\n' + comm_log_start + simulation_log + infoCheck + com_log_stop + com_log_save

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



def exitGracefully(signum, frame):
    """
    Kill monkey on the device or future connections will fail
    """
    print "Exiting Gracefully..."
    try:
        subprocess.call("adb shell kill -9 $(adb shell ps | grep monkey | awk '{print $2}')", shell=True)
    except Exception, e:
        print(e)
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exitGracefully)
    main()
