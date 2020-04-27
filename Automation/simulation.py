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
from helper_controller import *
from helper import *
######################## MAIN ########################

def main():
    ###### Capture Preparation
    # Read the applications info file
    apps_all = read_app(config.APPLICATIONS_FNAME)

    # numbering the experiements
    flush_left_state_number()

    # Read the left_state
    left_state = read_app("left_state.yaml")

    # faking current number
    _, left_faking = get_action_numb("NoAction", "NoApp", left_state)
    left_faking = left_faking + 1

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

    # Openning Ellisys and start capture
    if not config.DEBUG_WATCH:
        send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)

    apps = config.KEEP_ONLY
    if len(config.KEEP_ONLY) == 0:
        apps = apps_all
    skipped = False
    counter = 0

    # Loop on watches
    for deviceStruct in devices:

        # Extract device info
        device = deviceStruct[0]
        display = deviceStruct[1]
        watchName = deviceStruct[2]
        faking_nb = 0

        record_apps_version(device, watchName)

        # Loop on applications
        for appName in apps:

            # If app is in skipping
            if appName in config.SKIPPING:
                continue
            # Extract info about applications
            app = apps_all[appName]
            package = app["package"]

            activity = app["activity"]
            actions = app["actions"]
            actionsKeepOnly = app["keepOnly"]

            info = " ---- " + appName + " capture started ---"

            # Add a space to the log file
            tprint('', log_fname)
            tprint(info, log_fname)

            _, package_exist = verify_package_exist(device, package, log_fname)
            if not package_exist:
                continue

            # # Application Preambule
            # if login:
            #     simulate(device, display, package, activity, action, log_fname)

            # Loop on the set of actions of a patricular app
            for actionName in actionsKeepOnly:

                lastActionIsBackground = "background" in actions[actionName][-1]
                # Parse the actions contained in applications.yaml
                action = [eval(a) for a in actions[actionName]]

                left_state, left_nb = get_action_numb(actionName, appName, left_state)



                # Loop on a particular action
                i = 0
                while i < config.N_REPEAT_CAPTURE:
                    i = i + 1
                    capt_number =  i + left_nb


                    faking = False if config.N_CAPTURE_AFTER_FAKE == 0 else counter % config.N_CAPTURE_AFTER_FAKE == 0

                    # actions variables
                    success, success_command_sent, success_check_opened = True, True, True
                    success_close_command_sent, success_check_closed = True, True
                    success_simulate = True
                    filename = watchName + "_" +appName +"_"+ actionName+ "_Classic_enc_" + str(capt_number)

                    if faking:

                        filename = watchName + "_NoApp_NoAction_Classic_enc_" + str(left_faking + faking_nb)
                        faking_nb = faking_nb + 1
                        i = i - 1

                    # skip until we reach the last capture state
                    if not config.DEBUG_WATCH and not skipped and config.REACH_LEFT_STATE:
                        lastCapAppName = left_state["lastCapture"].split("_")[1]
                        last_nb = left_state["lastCapture"].split("_")[5]
                        currCapAppName = filename.split("_")[1]
                        curr_nb = filename.split("_")[5]
                        if currCapAppName!= lastCapAppName:
                            print("Skipping " + filename)
                            continue
                        else:
                            skipped = True

                    tprint("starting: " + filename, log_fname)

                    # Open Application if the first instruction is not open
                    # (Openning the application is not part of the capture)
                    if action[0][0].__name__ != "open_app":
                        _, success_command_sent = open_app(device, package, activity, log_fname)
                        _, success_check_opened  = check_package_opened(device, package, log_fname)

                        if not config.DEBUG_WATCH:
                            tprint("Sleeping " + str(config.WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION) + "s after opening")
                            time.sleep(config.WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION)

                    # Start capture
                    if not config.DEBUG_WATCH:
                        send_instruction(messages.NewStartCaptureCommand(payload=lastFilename), log_fname)

                    #  launch action
                    time.sleep(config.WAITING_TIME_AFTER_START_CAPTURE)
                    if not faking and not config.DEBUG_ELLISYS :
                        success_simulate = simulate(device, display, package, activity, action, log_fname)
                    else:

                        tprint("    - fake capture no app opening. Sleeping " + str(config.FAKE_WAITTING_TIME) + "s", log_fname)
                        time.sleep(config.FAKE_WAITTING_TIME)

                    time.sleep(config.WAITING_TIME_BEFORE_STOP_CAPTURE)

                    # Stop Capture
                    if not config.DEBUG_WATCH:
                        errorStop = send_instruction(messages.CMD_STOP_CAPTURE, log_fname)

                    # close the application if the last instruction is not background or close app
                    if action[-1][0].__name__ != "close_app" and  action[-1][0].__name__ != "force_stop" and action[-1][0].__name__ != "background" and not faking:
                        if config.CLOSING_METHOD == "close_app":
                            _, success_close_command_sent = close_app(device, package, log_fname)
                            _, success_check_closed = check_package_closed(device, package, log_fname)

                        if config.CLOSING_METHOD == "background":
                            background(device, package)
                            tprint("    - background command sent", log_fname)
                            _, success_check_closed = check_package_closed(device, package, log_fname)
                            lastActionIsBackground = True

                        if config.CLOSING_METHOD == "force_stop":
                            force_stop(device, package, log_fname)
                            _, success_check_closed = check_package_closed(device, package, log_fname)


                        if not config.DEBUG_WATCH:
                            tprint("   sleeping after closing " + str(config.WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION) + "s to reach steady state")
                            time.sleep(config.WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION)

                    # Save capture under a different name if an error occured
                    success = success and success_simulate and success_command_sent and success_check_closed and success_close_command_sent

                    if not success:
                        filename = filename + "_errorWatch"


                    # Save capture
                    if not config.DEBUG_WATCH:
                        if errorStop:
                            filename = filename + "_errorStop"
                        errorEllisys = send_instruction(messages.NewSaveCaptureCommand(payload=filename), log_fname)

                        if errorEllisys:
                            filename = filename + "_errorEllisys"

                        if not "error" in filename:
                            if not faking:
                                left_state[appName][actionName] += 1
                                left_state["lastCapture"] = filename
                            else:
                                left_state["NoApp"]["NoAction"] += 1
                            dump_yaml(left_state, "left_state.yaml")

                    lastFilename = ", " + filename
                    counter = counter + 1
                    time.sleep(2)

                    # Restart Ellisys each N captures
                    if counter != 0 and not config.DEBUG_WATCH and counter % config.N_CAPTURE_AFTER_ELLISYS_RESART == 0 :
                        send_instruction(messages.CMD_CLOSE_ELLISYS, log_fname)
                        lastFilename = ""
                        time.sleep(10)  # Sleeping a bit before capturing new app
                        send_instruction(messages.CMD_OPEN_ELLISYS, log_fname)


                    # Event loop
                    tprint("", log_fname)  # add a space for more visibility


                # Action loop
                if lastActionIsBackground and config.CLEAR_WHEN_CHANGE_APP_AFTER_BACKGROUND:
                    force_stop(device, package, log_fname)

            # App loop
            info = " ---- " + appName + " capture finished --- "
            tprint(info, log_fname)

        # watch loop
        record_apps_version(device, watchName)




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
