# Main script
# Simulate touch on the watch
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_commands import *  # it is important to import all the functions
sys.path.append(r"./yaml")
from controler_to_ellisys import send_instruction
import messages
import config
import signal
import subprocess
import yaml
from helper import write_logs, read_app, tprint


######################## MAIN ########################

def main():
    ###### Capture Preparation
    # Read the applications info file
    apps_all = read_app(config.APPLICATIONS_FNAME)




    # Create log file
    launchTime = time.strftime("%d-%m-%y_%H-%M-%S", time.localtime()) # for log file name
    log_fname = "controller_" + launchTime
    write_logs(log_fname, "--- Log init ---  \n", 'w')

    ##### Connection with the watch(es)

    tprint("Accessing device(s)...", log_fname)

    tries = 0
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
                tprint("Connection with device error. Max tries "+ str(tries) +" reached.\naborting...")
                sys.exit(1)
            tries += 1

        watchName = str(watchName.replace(" ", "-"))
        tprint("Device: " + watchName + " connected")
        devices.append((device, (int(width) - 1, int(height) -1), watchName))

    tprint("All devices are connected")


    if config.CLEAN_ALL_APPS:
        for device, _ , _ in devices:
            clean_apps(device, apps_all, log_fname)

    # Openning Ellisys
    if not config.DEBUG_WATCH:
        send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)

    apps = config.KEEP_ONLY
    if config.KEEP_ONLY == "all":
        apps = apps_all

    counter = 0
    # Loop on applications
    for appName in apps:


        # Extract info about applications
        app = apps_all[appName]
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

                    # Extract device info
                    device = deviceStruct[0]
                    display = deviceStruct[1]
                    watchName = deviceStruct[2]

                    # actions variables
                    success, success_command_sent, success_check_opened = True, True, True
                    success_close_command_sent, success_check_closed = True, True

                    filename = watchName + "_" +appName +"_"+ actionName+ "_Classic_enc_" + str(j)

                    # Add a space to the log file
                    tprint('', log_fname)
                    tprint("starting: " + filename, log_fname)

                    # Open Application if the first instruction is not open
                    # (Openning the application is not part of the capture)
                    if action[0][0].__name__ != "open_app":
                        command_sent, success_command_sent = open_app(device, package, activity)
                        write_logs(log_fname, command_sent + '\n')
                        check_opened, success_check_opened  = check_package_opened(device, package)
                        write_logs(log_fname, check_opened + '\n')
                        if config.DEBUG_WATCH:
                            time.sleep(config.WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION)

                    # Start capture
                    if not config.DEBUG_WATCH:
                        send_instruction(messages.NewStartCaptureCommand(payload=lastFilename), log_fname)

                    #  launch action
                    time.sleep(config.WAITING_TIME_AFTER_START_CAPTURE)
                    success_simulate = simulate(device, display, package, activity, action, log_fname)
                    time.sleep(config.WAITING_TIME_BEFORE_STOP_CAPTURE)

                    # Stop Capture
                    if not config.DEBUG_WATCH:
                        send_instruction(messages.CMD_STOP_CAPTURE, log_fname)

                    # close the application if the last instruction is not background or close app
                    if action[-1][0].__name__ != "close_app" and action[-1][0].__name__ != "background":
                        if config.CLOSING_METHOD == "close_app":
                            _, success_close_command_sent = eval(config.CLOSING_METHOD)(device, package, log_fname)
                            _, success_check_closed = check_package_closed(device, package, log_fname)
                        else:
                            eval(config.CLOSING_METHOD)(device, package, log_fname)
                            _, success_check_closed = check_package_closed(device, package, log_fname)


                    # Save capture under a different name if an error occured
                    success = success and success_simulate and success_command_sent and success_check_closed and success_close_command_sent

                    if not success:
                        filename = filename + "_error"
                    # Save capture
                    if not config.DEBUG_WATCH:
                        send_instruction(messages.NewSaveCaptureCommand(payload=filename), log_fname)



                    lastFilename = ", " + filename
                    counter = counter + 1
                    time.sleep(2)

                    # Restart Ellisys each N captures
                    if counter != 0 and not config.DEBUG_WATCH and counter % config.N_CAPTURE_AFTER_ELLISYS_RESART == 0 :
                        send_instruction(messages.CMD_CLOSE_ELLISYS, log_fname)
                        lastFilename = ""
                        time.sleep(10)  # Sleeping a bit before capturing new app
                        send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)
        info = "\n ---- " + appName + " capture finished --- \n"
        tprint(info, log_fname)



    if not config.DEBUG_WATCH:
        send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)
    tprint("done", log_fname)



def killMonkey(signum, frame):
    """
    Kill monkey on the device or future connections will fail
    """
    print "killing monkey on the device"
    try:
        subprocess.call("adb shell kill -9 $(adb shell ps | grep monkey | awk '{print $2}')", shell=True)
    except Exception, e:
        print(e)
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, killMonkey)
    main()
