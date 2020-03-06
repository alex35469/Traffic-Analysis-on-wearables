from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import config
import os
from helper import write_logs, tprint


def swipe_down(device, display):
    width, height = display[0], display[1]
    x1, y1 = (int(width/2), 5)
    x2, y2 = (int(width/2), int(2*height/3))
    duration = 100
    device.shell("input swipe "+ str(x1)+" "+ str(y1)+" "+ str(x2)+" "+ str(y2)+" "+ str(duration))


def swipe_up(device, display):
    width, height = display[0], display[1]
    x1, y1 = (int(width/2), height - 5)
    x2, y2 = (int(width/2), int(height/3))
    duration = 100
    device.shell("input swipe "+ str(x1)+" "+ str(y1)+" "+ str(x2)+" "+ str(y2)+" "+ str(duration))


def swipe_right(device, display):
    width, height = display[0], display[1]
    x1, y1 = (5, int(height/2))
    x2, y2 = (int(2*width/3), int(height/2))
    duration = 100
    device.shell("input swipe "+ str(x1)+" "+ str(y1)+" "+ str(x2)+" "+ str(y2)+" "+ str(duration))


def swipe_left(device, display):
    width, height = display[0], display[1]
    x1, y1 = (width - 10, int(height/2))
    x2, y2 = (width/5, height/2)
    duration = 120
    device.shell("input swipe "+ str(x1)+" "+ str(y1)+" "+ str(x2)+" "+ str(y2)+" "+ str(duration))



def scroll_left(device, display):
    width = display[0]
    height = display[1]
    device.drag((width/3, height/2), (2 * width/3, height/2), 0.1)
    MonkeyRunner.sleep(0.5)

def scroll_right(device, display):
    "Simulate a scroll down"
    width = display[0]
    height = display[1]
    device.drag((2 * width/3, height/2), (width/3, height/2), 0.1)
    MonkeyRunner.sleep(0.5)

def scroll_up(device, display):
    width = display[0]
    height = display[1]
    device.drag((width/2, height/3), (width/2, 2 * height/3), 0.1)
    MonkeyRunner.sleep(0.5)

def scroll_down(device, display):
    "Simulate a scroll down"
    width = display[0]
    height = display[1]
    device.drag((width/2, height/3), (width/2, 2 * height/3), 0.1)
    MonkeyRunner.sleep(0.5)


def click(location):
    """Return a function the perform a button touch
    on the device with the location = (x, y)"""

    def click_func(device, display):
        assert 0 < location[0] < display[0]
        assert 0 < location[1] < display[1]
        device.shell("input tap " + str(location[0]) + " " +str(location[1]))

    return click_func

def press_random_letters(device, display, n_press=3):
    alphabet = "abcdefghijklmnopqrstuvwxyz "
    text = "".join(random.choices(alphabet, k=n_press))

    def press_random_letters_func(device, display):
        device.shell("input text " + text)
    return press_random_letters_func

def press_random_numbers(device, display, n_press=3):
    numbers = "1234567890"
    text = "".join(random.choices(alphabet, k=n_press))
    device.shell("input text " + text)


def open_app(device, package, activity, log_fname):
    package_and_activity = package + "/" + activity
    success = True
    cmd = "am start " + package_and_activity
    for _ in range(3):
        response = os.popen("adb shell "+cmd).read()
        if not "Error" in response and response is not None:
            break
        else:
            success = False
    if success:
        result = "   CHECK: Sending '"+ cmd + "' OK"
    else:
        result = "   CHECK: Sending '"+ cmd + "' FAIL"
    tprint(result, log_fname)
    return result, success


def close_app(device, package, log_fname):
    success = False
    if package == "com.google.android.wearable.app":
        result = "   CHECK: Sending pm clear FAIL (package 'com.google.android.wearable.app' can not be close this way)"
        tprint(result, log_fname)
        return result, success

    cmd = "adb shell pm clear " + package
    for _ in range(3):
        response = os.popen(cmd).read()
        success = response == "Success\n"
        if success:
            break
    if success:
        result = "   CHECK: Sending command pm clear OK"
    else:
        result = "   CHECK: Sending command pm clear FAIL"
    tprint(result, log_fname)
    return result, success


def background(device, package):
    device.shell("input keyevent 3")


##### CHECK METHODE

def check_bluetooth_enabled(device, log_fname):
    answ = device.shell("dumpsys bluetooth_manager")
    if answ is None:
        # TODO: RECOVERY MODE WITH ADB
        return "   CHECK: Bluetooth connection return NoneType FAIL", False
    answ = answ.encode('utf8')
    success = "curState=Connected" in answ
    success = success or "ScanMode: SCAN_MODE_NONE" in answ
    if success:
        result = "   CHECK: Bluetooth connection OK"
    else:
        result = "   CHECK: Bluetooth connection FAIL"
    tprint(result, log_fname)
    return result, success


def check_package_opened(device, package, log_fname):
    for _ in range(3):
        status = device.shell("dumpsys window windows | grep Focus")
        if status is None:
            return "   CHECK: Package opened FAIL\n   Received NoneType", False
        status = status.encode('utf8')
        success = package in status
        if success:
            break
        time.sleep(0.5)
    if success:
        result = "   CHECK: Package opened OK"
    else:
        result = "   CHECK: Package opened FAIL\n   Status: '"+status+"'"
    tprint(result, log_fname)
    return result, success

def check_package_closed(device, package, log_fname):
    for _ in range(3):
        status = device.shell("dumpsys window windows | grep Focus")
        if status is None:
            return "   CHECK:  Watch on home sceen FAIL\n   Received NoneType", False
        status = status.encode('utf8')

        success = config.HOME_PACKAGE in status

        if success:
            break
        time.sleep(0.5)

    if success:
        result = "   CHECK: Watch on home screen OK"
    else:
        result = "   CHECK: Watch on home sceen FAIL\n        Status: '"+status + "'"
    tprint(result, log_fname)
    return result, success
# SIMULATION


def simulate(device, display, package, activity, actions_waiting, log_fname, check=True):
    checkInfo = ""
    success = True
    # Checks

    check_bluetooth, successTmp = check_bluetooth_enabled(device, log_fname)
    success = success and successTmp

    # Simulate a sequence of action
    for a, w in actions_waiting:
        info = "    - " + a.__name__ +", "+time.strftime("%H:%M:%S", time.localtime())
        if a.__name__ == "open_app":
            _, successTmp1 = a(device, package, activity, log_fname)
            _, successTmp2 = check_package_opened(device, package, log_fname)
            success = success and successTmp1 and successTmp2

        elif a.__name__ == "close_app":
            close_command_sent, successTmp1 = a(device, package, log_fname)
            check_closed, successTmp2 = check_package_closed(device, package, log_fname)
            success = success and successTmp1 and successTmp2

        elif a.__name__ == "background":
            a(device, package)
            check_closed, success6 = check_package_closed(device, package)
            write_logs(log_fname, check_closed + '\n')

        else:
            a(device, display)
        info += ", "+time.strftime("%H:%M:%S", time.localtime())
        tprint(info, log_fname)
        time.sleep(w)
    return success

def force_stop(device, package, log_fname):
    if package in config.PACKAGE_NOT_TO_STOP:
        info = "    - force stopping not apply because sys package. Home screen instead"
        tprint(info, log_fname)
        background(device, package)
        tprint("    - sleeping 15s. to replace package force stop", log_fname)
        time.sleep(15)
        return True, info

    cmd = "adb shell am force-stop " + package
    tprint( "    - force stop", log_fname)
    response = os.system(cmd)
    success = response == 0
    if success:
        result = "   CHECK: force stopping OK"
    else:
        result = "   CHECK: force stopping FAIL"

    tprint(result, log_fname)
    return result, success

def clean_apps(device, apps, log_fname):
    info = "Cleaning applications"
    tprint(info, log_fname)
    for app in apps:
        info = " -"+ app + ": package - " + apps[app]["package"]
        tprint(info, log_fname)
        if apps[app]["package"] != "com.google.android.wearable.app":
            if config.CLEANING_CLEAR_DATA:
                close_app(device, apps[app]["package"], log_fname)
            if config.CLEANING_FORCE_STOP:
                force_stop(device, apps[app]["package"], log_fname)
            time.sleep(config.INTER_CLEANING_WAITING_TIME) # Otherwise shellCommandUnresponsive

        else:
            info = "Skipping..."
            tprint(info, log_fname)

    info="\n ---- cleaning finished -----\n"
    tprint(info, log_fname)
    tprint("Sleeping after cleaning " + str(config.SLEEP_AFTER_CLEANING) + "s ", log_fname)
    time.sleep(config.SLEEP_AFTER_CLEANING)
