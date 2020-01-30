from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
def swipe_left(device, display):
    width = display[0]
    height = display[1]
    device.drag((0,height/2), (3*width/4,height/2), 0.1)
    MonkeyRunner.sleep(0.5)


def swipe_right(device, display):
    width, height = display[0], display[1]
    device.drag((width, height/2), (width/3,height/2), 0.1)
    MonkeyRunner.sleep(0.5)

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


def simulate(device, display, package, activity, actions_waiting):
    cumInfo = ""
    # Simulate a sequence of action
    for a, w in actions_waiting:
        info = "    - " + a.__name__ +", "+time.strftime("%H:%M:%S", time.localtime())
        if a.__name__ == "open_app":
            a(device, package, activity)
        elif a.__name__ == "close_app":
            a(device, package)
        else:
            a(device, display)
        info += ", "+time.strftime("%H:%M:%S", time.localtime()) 
        print(info)
        cumInfo += info + "\n"
        time.sleep(w)

    return cumInfo
