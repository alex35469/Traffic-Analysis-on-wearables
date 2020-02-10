from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import config

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

    device.touch(10, 20, MonkeyDevice.UP)

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
    device.startActivity(component=package_and_activity)

def close_app(device, package):
    device.shell("pm clear " + package)



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
        return "   CHECK: Bluetooth connection OK"
    else:
        return "   CHECK: Bluetooth connection FAIL"

def check_package_opened(device, package):
    status = str(device.shell("dumpsys window windows | grep Focus"))

    if package in status:
        return "   CHECK: Package opened OK"
    else:
        return "   CHECK: Package opened FAIL\n        Status: "+status 

def check_package_closed(device, package):
    status = str(device.shell("dumpsys window windows | grep Focus"))
    if config.HOME_PACKAGE in status:
        return "   CHECK: Package closed OK"
    else:
        return "   CHECK: Package closed FAIL\n        Status: "+status

# SIMULATION


def simulate(device, display, package, activity, actions_waiting, phoneName, check=True):
    cumInfo = ""
    checkInfo = ""
    # Simulate a sequence of action
    if check:
        checkInfo += check_bluetooth_enabled(device, phoneName) + '\n'

    for a, w in actions_waiting:
        info = "    - " + a.__name__ +", "+time.strftime("%H:%M:%S", time.localtime())
        if a.__name__ == "open_app":
            a(device, package, activity)
            checkInfo += check_package_opened(device, package) + '\n'

        elif a.__name__ == "close_app" or a.__name__ == "background" :
            a(device, package)
            checkInfo += check_package_closed(device, package) + '\n'


        else:
            a(device, display)
        info += ", "+time.strftime("%H:%M:%S", time.localtime())
        print(info)
        cumInfo += info + "\n"
        time.sleep(w)
    print(checkInfo)

    return cumInfo, checkInfo
