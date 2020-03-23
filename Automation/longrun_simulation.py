# Main script
# Simulation watch

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_commands import *  # it is important to import all the functions
sys.path.append(r"./yaml")
from controler_to_ellisys import send_instruction
import messages
import longrun_config
import signal
import subprocess
import yaml
from helper_controller import *
from helper import *
from random import choice, uniform, expovariate
import os


######################## MAIN ########################

def main():
    ###### Capture Preparation
    # Read the applications info file
    apps_all = read_app(longrun_config.APPLICATIONS_FNAME)


    # Create log file
    launchTime = time.strftime("%d-%m-%y_%H-%M-%S", time.localtime()) # for log file name
    log_fname = "longrunner_capture_expanded_" + launchTime
    log_synthesis = "longrunner_capture_synth_" + launchTime
    write_logs(log_fname, "--- Log init ---  \n", 'w')
    write_logs(log_synthesis, "--- Log init ---  \n", 'w')

    # Make the list of all action to pick for the simulation
    all_action = []  # list of tuples: [(name_app, name_action)]

    for app in apps_all:
        if len(longrun_config.KEEP_ONLY) == 0 and not app in longrun_config.SKIPPING:
            all_action += [(app, action) for action in apps_all[app]["keepOnly"]]
        elif app in longrun_config.KEEP_ONLY and not app in longrun_config.SKIPPING:
                all_action += [(app, action) for action in apps_all[app]["keepOnly"]]
    print(all_action)



    ##### Connection with the watch(es)

    tprint("Accessing device(s)...", log_fname)

    tries = 0
    devices = []
    for device_addr in longrun_config.DEVICES:

        # Connects to the current device, returning a MonkeyDevice object
        device = None
        width = None
        lastFilename = ""
        lastApp = False  # Ensure we do not open and close twice

        while width is None:

            device = MonkeyRunner.waitForConnection(deviceId=device_addr, timeout=longrun_config.WATCH_CONNECTION_TIMEOUT)


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

    ##### Cleaning all applications
    if longrun_config.CLEAN_ALL_APPS:
        for device, _ , _ in devices:
            clean_apps(device, apps_all, log_fname)

    ##### Openning and startin capture Ellisys
    t_ref = None
    if not longrun_config.DEBUG_WATCH:
        send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)
        send_instruction(messages.NewStartCaptureCommand(payload=lastFilename), log_fname)
        t_ref = time.time()




    # Loop on watches
    for deviceStruct in devices:

        # Extract device info
        device = deviceStruct[0]
        display = deviceStruct[1]
        watchName = deviceStruct[2]




        # Loop on applications
        savedCounter = 0
        i = 0
        while i < longrun_config.N_REPEAT_CAPTURE:
            # Generate random sequence of action
            appName, actionName = choice(all_action)

            # Choose the waiting time
            if longrun_config.WAITING_METHOD == "exponential":
                t_wait = int(expovariate(longrun_config.EXPOVARIATE_LAMBDA))

            elif longrun_config.WAITING_METHOD == "uniform":
                t_wait = int(uniform(longrun_config.WAITING_LOWER, longrun_config.WAITING_UPPER))
            else:
                tprint("longrun_config.WAITING_METHOD: " + longrun_config.WAITING_METHOD + " not recognized", t_ref = t_ref)
                tprint("aborting...", t_ref = t_ref)
                sys.exit(1)


            # Extract info about applications
            app = apps_all[appName]

            package = app["package"]
            activity = app["activity"]
            actions = app["actions"]


            _, package_exist = verify_package_exist(device, package, log_fname)
            if not package_exist:
                continue

            i = i + 1
            tprint(str(i) + "/" +  str(longrun_config.N_REPEAT_CAPTURE) + " captures", t_ref = t_ref)

            # Parse the actions contained in applications.yaml
            action = [eval(a) for a in actions[actionName]]

            # actions variables
            success, success_command_sent, success_check_opened = True, True, True
            success_close_command_sent, success_check_closed = True, True
            success_simulate = True

            tprint("starting: " + appName + " - " + actionName + ". t_wait=" + str(t_wait), log_fname, t_ref)
            time.sleep(t_wait)
            os.system("spd-say 'Launching application: " +appName + " action: " + actionName + "'")
            # Open Application if the first instruction is not open
            # (Openning the application is not part of the capture)
            simulate_required = True
            if action[0][0].__name__ != "open_app" or ( action[0][0].__name__ == "open_app" and len(action[0]) == 1):
                tprint(" ! app " + appName +" openning", log_fname, t_ref=t_ref)
                sprint(appName +" openning", log_synthesis, t_ref=t_ref)
                _, success_command_sent = open_app(device, package, activity, log_fname)
                _, success_check_opened  = check_package_opened(device, package, log_fname)

                if not longrun_config.DEBUG_WATCH:
                    tprint("Sleeping " + str(longrun_config.WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION) + "s after opening")
                    time.sleep(longrun_config.WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION)
                if ( action[0][0].__name__ == "open_app" and len(action[0][0]) == 1):
                    simulate_required = False

            #  launch action
            if not longrun_config.DEBUG_ELLISYS and simulate_required:
                tprint(" ! action " + appName + " - " + actionName + " starting", log_fname, t_ref)
                sprint(appName + " - " + actionName + " starting", log_synthesis, t_ref)
                success_simulate = simulate(device, display, package, activity, action, log_fname, t_ref)



            # close the application if the last instruction is not background or close app
            if action[-1][0].__name__ != "close_app" and  action[-1][0].__name__ != "force_stop" and action[-1][0].__name__ != "background":
                tprint(" ! app " + appName + " closing", log_fname, t_ref = t_ref)
                sprint(appName + " closing", log_synthesis, t_ref = t_ref)
                if longrun_config.CLOSING_METHOD == "close_app":
                    _, success_close_command_sent = close_app(device, package, log_fname)
                    _, success_check_closed = check_package_closed(device, package, log_fname)

                if longrun_config.CLOSING_METHOD == "background":
                    background(device, package)
                    tprint("    - background command sent", log_fname, t_ref)
                    _, success_check_closed = check_package_closed(device, package, log_fname)
                    lastActionIsBackground = True

                if longrun_config.CLOSING_METHOD == "force_stop":
                    force_stop(device, package, log_fname)
                    _, success_check_closed = check_package_closed(device, package, log_fname)



                if not longrun_config.DEBUG_WATCH:
                    tprint("   sleeping after closing " + str(longrun_config.WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION) + "s to reach steady state", log_fname)
                    time.sleep(longrun_config.WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION)

            # Save capture under a different name if an error occured
            success = success and success_simulate and success_command_sent and success_check_closed and success_close_command_sent

            if not success:
                tprint(" ! ERROR Watch", log_fname, t_ref)
                sprint("ERROR Watch", log_synthesis, t_ref)

            # Restart Ellisys each N captures
            if not longrun_config.DEBUG_WATCH and i % longrun_config.N_CAPTURE_AFTER_ELLISYS_RESART == 0 :
                savedCounter += 1
                filename = "log-runcapture-"+ str(savedCounter)
                tprint(" ! capture " + filename + " finished", log_fname, t_ref)
                sprint("capture " + filename + " finished", log_synthesis, t_ref)
                errorStop = send_instruction(messages.CMD_STOP_CAPTURE, log_fname)
                errorEllisys = send_instruction(messages.NewSaveCaptureCommand(payload=filename), log_fname)
                if errorStop or errorEllisys:
                    os.system("spd-say 'Error please come help me'")
                    raw_input("Please check ellisys: errorStop=" + str(errorStop) + " errorEllisys=" + str(errorEllisys))

                send_instruction(messages.CMD_CLOSE_ELLISYS, log_fname)
                time.sleep(10)  # Sleeping a bit before capturing new app
                send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)
                send_instruction(messages.NewStartCaptureCommand(payload=""), log_fname)
                t_ref = time.time()
                filename = "log-runcapture-"+ str(savedCounter + 1)
                tprint(" ! capture " + filename + " started", log_fname, t_ref)
                sprint("capture " + filename + " started", log_synthesis, t_ref)



            tprint("", log_fname)  # add a space for more visibility



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