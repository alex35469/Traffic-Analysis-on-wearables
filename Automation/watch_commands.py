from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import config
from helper import write_logs


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
    x1, y1 = (width - 5, int(height/2))
    x2, y2 = (width/3, height/2)
    duration = 100
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


def open_app(device, package, activity):
    package_and_activity = package + "/" + activity
    success = True
    cmd = "am start -c api.android.intent.LAUNCHER -a api.android.category.MAIN " + package_and_activity
    for _ in range(3):
        response = device.shell(cmd)
        response = response.encode('utf8')
        if not "Error" in response and response is not None:
            break
        else:
            success = False
    if success:
        result = "   CHECK: When sending command: '"+ cmd + "' OK"
    else:
        result = "   CHECK: When sending command: '"+ cmd + "' FAIL"
    print(result)
    return result, success

def close_app(device, package):
    success = False
    for _ in range(3):
        response = device.shell("pm clear " + package)
        success = response == "Success\n"
        if success:
            break
    if success:
        result = "   CHECK: Sending command pm clear OK"
    else:
        result = "   CHECK: Sending command pm clear FAIL"
    print(result)
    return result, success


def button_click_func(location):
    """Return a function the perform a button touch
    on the device with the location = (x, y)"""

    def click(device, display):
        assert 0 < location[0] < display[0]
        assert 0 < location[1] < display[1]
        device.touch(location[0], location[1], "DOWN_AND_UP")

    return click

def background(device, package):
    device.press('KEYCODE_HOME',MonkeyDevice.DOWN_AND_UP)


##### CHECK METHODE

def check_bluetooth_enabled(device):
    answ = device.shell("dumpsys bluetooth_manager")
    answ = answ.encode('utf8')
    success = "curState=Connected" in answ
    if success:
        result = "   CHECK: Bluetooth connection OK"
    else:
        result = "   CHECK: Bluetooth connection FAIL"
    print(result)
    return result, success


def check_package_opened(device, package):
    status = str(device.shell("dumpsys window windows | grep Focus"))
    success = package in status
    if success:
        result = "   CHECK: Package opened OK"
    else:
        result = "   CHECK: Package opened FAIL\n        Status: "+status
    print(result)
    return result, success

def check_package_closed(device, package):
    status = str(device.shell("dumpsys window windows | grep Focus"))
    success = config.HOME_PACKAGE in status
    if success:
        result = "   CHECK: Watch on home screen OK"
    else:
        result = "   CHECK: Watch on home sceen FAIL\n        Status: '"+status + "'"
    print(result)
    return result, success
# SIMULATION


def simulate(device, display, package, activity, actions_waiting, log_fname, check=True):
    checkInfo = ""
    success = True
    # Checks
    if check:
        check_bluetooth, successTmp = check_bluetooth_enabled(device)
        write_logs(log_fname, check_bluetooth + '\n')
        success = success and successTmp

    # Simulate a sequence of action
    for a, w in actions_waiting:
        info = "    - " + a.__name__ +", "+time.strftime("%H:%M:%S", time.localtime())
        if a.__name__ == "open_app":
            command_sent, successTmp1 = a(device, package, activity)
            write_logs(log_fname, command_sent + '\n')
            check_opened, successTmp2 = check_package_opened(device, package)
            write_logs(log_fname, check_opened + '\n')
            success = success and successTmp1 and successTmp2

        elif a.__name__ == "close_app":
            close_command_sent, successTmp1 = a(device, package)
            write_logs(log_fname, close_command_sent + '\n')
            check_closed, successTmp2 = check_package_closed(device, package)
            write_logs(log_fname, check_closed + '\n')
            success = success and successTmp1 and successTmp2

        elif a.__name__ == "background":
            a(device, package)
            check_closed, success6 = check_package_closed(device, package)
            write_logs(log_fname, check_closed + '\n')

        else:
            a(device, display)
        info += ", "+time.strftime("%H:%M:%S", time.localtime())
        print(info)
        write_logs(log_fname, info + '\n')
        time.sleep(w)
    return success
