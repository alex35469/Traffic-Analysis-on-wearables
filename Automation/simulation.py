# Main script
# Simulate touch on the watch
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
from watch_commands import *  # it is important to import all the functions
sys.path.append(r"./yaml")
import yaml
from controler_to_ellisys import send_instruction
import messages
import config
import signal
import subprocess
from helper import write_logs


######################## MAIN ########################

def main():
    ###### Capture Preparation
    # Read the applications info file
    f = open("applications.yaml")
    l = f.read()
    f.close()
    apps = yaml.load(l)



    launchTime = time.strftime("%d-%m-%y_%H-%M-%S", time.localtime()) # for log file name
    log_fname = "controller_" + launchTime
    write_logs(log_fname, "--- Log init ---  \n", 'w')
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
                print("Connection with device error. Max tries "+ str(tries) +" reached.\naborting...")
                sys.exit(1)
            tries += 1

        watchName = str(watchName.replace(" ", "-"))
        print("Device: " + watchName + " connected")
        devices.append((device, (int(width) - 1, int(height) -1), watchName))

    print("All devices are connected")


    # MAIN
    if not config.DEBUG_WATCH:
        log = send_instruction(messages.CMD_OPEN_ELLISYS)
        write_logs(log_fname, log)

    counter = 0

    # Loop on applications
    for appName in config.KEEP_ONLY:


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
                    filename = '\n' + watchName + "_" +appName +"_"+ actionName+ "_Classic_enc_" + str(j)
                    print(filename)
                    write_logs(log_fname, filename + '\n')

                    # Open Application if the first instruction is not open
                    # (Openning the application is not part of the capture)
                    if action[0][0].__name__ != "open_app":
                        command_sent = open_app(device, package, activity) + '\n'
                        write_logs(log_fname, command_sent)
                        check_opened = check_package_opened(device, package) + '\n'
                        write_logs(log_fname, check_opened)
                    #

                    # Start capture
                    if not config.DEBUG_WATCH:
                        comm_start_log = send_instruction(messages.NewStartCaptureCommand(payload=lastFilename)) + '\n'
                        write_logs(log_fname, comm_start_log)

                    #  launch action
                    time.sleep(config.WAITING_TIME_AFTER_START_CAPTURE)
                    simulation_log = simulate(device, display, package, activity, action, config.PHONE_NAME, log_fname, check=config.PERFORM_EXTRA_CHECK)
                    write_logs(log_fname, simulation_log)
                    time.sleep(config.WAITING_TIME_BEFORE_STOP_CAPTURE)


                    # Stop Capture
                    if not config.DEBUG_WATCH:
                        comm_stop_log = send_instruction(messages.CMD_STOP_CAPTURE) + '\n'
                        write_logs(log_fname, comm_stop_log)
                        comm_save_log = send_instruction(messages.NewSaveCaptureCommand(payload=filename)) + '\n'
                        write_logs(log_fname, comm_save_log)


                    # close the application if it is required
                    if action[-1][0].__name__ != "close_app" and action[-1][0].__name__ != "background":
                        close_command_sent = eval(config.CLOSING_METHOD)(device, package)
                        if close_command_sent is not None :
                            write_logs(log_fname, close_command_sent + '\n')
                        check_closed = check_package_closed(device, package) + '\n'
                        write_logs(log_fname, check_closed + '\n')

                    # Add a space to the log file
                    write_logs(log_fname, '\n')
                    lastFilename = ", " + filename
                    counter = counter + 1
                    time.sleep(2)

        # Restart Ellisys
        if (config.RESTART_ELLISYS_WHEN_CHANGING_APP and len(actionsKeepOnly) != 0) and not config.DEBUG_WATCH:
            send_instruction(messages.CMD_CLOSE_ELLISYS)
            lastFilename = ""

            # if the app is not the last app
            if appName != config.KEEP_ONLY[-1]:
                time.sleep(10)  # Sleeping a bit before capturing new app
                send_instruction(messages.CMD_OPEN_ELLISYS)

    print("done")



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
