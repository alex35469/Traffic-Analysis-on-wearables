from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import config
from helper import write_logs

def swipe_left(device, display):
    width = display[0]
    height = display[1]
    device.drag((0,height/2), (3*width/4,height/2), 0.1)
    MonkeyRunner.sleep(0.5)


def swipe_right(device, display):
    width, height = display[0], display[1]
    device.drag((width - 30, height/2), (width/3,height/2), 0.05, 1)
    MonkeyRunner.sleep(0.5)

def iter_swipe_right(device, display):
    # Touch down screen
    device.touch(300, 190, MonkeyDevice.DOWN)
    # Move from 100, 500 to 300, 500
    a = 1.6
    for i in range(1, 15):
        device.touch(350 - 3 * i * a * a , 190, MonkeyDevice.MOVE)
        print "move ", 350 - 3 * i * a * a, 190
        time.sleep(0.1)

def lowlevel_swipe_right(device, display):
    width, height = display[0], display[1]
    x1, y1 = (width - 5, int(height/2))
    x2, y2 = (width/3, height/2)
    duration = 100
    device.shell("input swipe "+ str(x1)+" "+ str(y1)+" "+ str(x2)+" "+ str(y2)+" "+ str(duration))

def swipe_up(device, display):
    width = display[0]
    height = display[1]
    device.drag((width/2, 0), (width/2, 2*height/3), 0.1)
    MonkeyRunner.sleep(0.5)

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

def swipe_down(device, display):
    width = display[0]
    height = display[1]
    device.drag((width/2, height), (width/2,height/3), 0.1)
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
    success = False
    cmd = "am start -c api.android.intent.LAUNCHER -a api.android.category.MAIN " + package_and_activity
    for _ in range(3):
        response = device.shell(cmd)
        success = response == "Success\n"
        if success:
            break
    if success:
        result = "   CHECK: When sending command: '"+ cmd + "' FAIL"
    else:
        result = "   CHECK: When sending command: '"+ cmd + "' OK"
    print(result)
    return result

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
    return result


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

def check_bluetooth_enabled(device, phoneName):
    answ = str(device.shell("dumpsys bluetooth_manager"))

    if phoneName in answ:
        result = "   CHECK: Bluetooth connection OK"
    else:
        result = "   CHECK: Bluetooth connection FAIL"
    print(result)
    return result
def check_package_opened(device, package):
    status = str(device.shell("dumpsys window windows | grep Focus"))

    if package in status:
        result = "   CHECK: Package opened OK"
    else:
        result = "   CHECK: Package opened FAIL\n        Status: "+status
    print(result)
    return result

def check_package_closed(device, package):
    status = str(device.shell("dumpsys window windows | grep Focus"))
    if config.HOME_PACKAGE in status:
        result = "   CHECK: Watch on home screen OK"
    else:
        result = "   CHECK: Watch on home sceen FAIL\n        Status: '"+status + "'"
    print(result)
    return result
# SIMULATION


def simulate(device, display, package, activity, actions_waiting, phoneName, log_fname, check=True):
    cumInfo = ""
    checkInfo = ""

    # Checks
    if check:
        check_bluetooth = check_bluetooth_enabled(device, phoneName) + '\n'
        write_logs(log_fname, check_bluetooth)

    # Simulate a sequence of action
    for a, w in actions_waiting:
        info = "    - " + a.__name__ +", "+time.strftime("%H:%M:%S", time.localtime())
        if a.__name__ == "open_app":
            command_sent = a(device, package, activity) + '\n'
            write_logs(log_fname, command_sent)
            check_opened = check_package_opened(device, package) + '\n'
            write_logs(log_fname, check_opened)

        elif a.__name__ == "close_app" or a.__name__ == "background" :
            close_command_sent = a(device, package)
            if close_command_sent is not None :
                write_logs(log_fname, close_command_sent + '\n')
            check_closed = check_package_closed(device, package) + '\n'
            write_logs(log_fname, check_closed + '\n')


        else:
            a(device, display)
        info += ", "+time.strftime("%H:%M:%S", time.localtime())
        print(info)
        write_logs(log_fname, info + '\n')
        time.sleep(w)


    return cumInfo
