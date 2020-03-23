import sys
# Watches
HUWAWEI_WATCH_IP_PORT = "192.168.1.134:5555"  # '192.168.43.17:5555' Watch ip config.WATCH_IP_PORTess. Change if not connected to Mobnet
FOSILL_WATCH_IP_PORT = "192.168.1.129:5555"
HOME_PACKAGE = "com.google.android.wearable.app"  # To check thaz the home is indeed reached
DEVICES = [HUWAWEI_WATCH_IP_PORT] #, FOSILL_WATCH_IP_PORT]

DEBUG_ELLISYS = False
DEBUG_WATCH = False  # Does not communiacte with ellisys controller
WATCH_CONNECTION_TIMEOUT = 10  # timeout after watch not connected (First instruction)

# Apps
APPLICATIONS_FNAME = "applications.yaml"  # Applications actions instr. & data
N_REPEAT_CAPTURE = 100

KEEP_ONLY = [] # FindMyPhone Applications to keep for the automation
SKIPPING = ["Stopwatch", "Medisafe", "DailyTracking", "AthkarOfPrayer",
            "SmartZmanim", "Alarm", "ASB", "Flashlight", "Timer", "Battery"]

# Simulation
CLOSING_METHOD = "force_stop" # Either close_app or background or force_stop
CLEAR_WHEN_CHANGE_APP_AFTER_BACKGROUND = True  # Make a clear when changing to a new action after a background close
LOGIN_BEFORE_CAPTURE = True
WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION = 6  # Such that the app reach a stable stat
WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION = 1 # Such that the app reach a stable stat after closing
PACKAGE_NOT_TO_STOP = ["com.google.android.wearable.app", "com.huawei.health", "com.huawei.watch.supersavepower"]

WAITING_METHOD = "exponential"
EXPOVARIATE_LAMBDA_MINUTE = 0.1
EXPOVARIATE_LAMBDA = EXPOVARIATE_LAMBDA_MINUTE / 60  # We divide by 60 to convert into seconds
WAITING_LOWER = 2 * 60
WAITING_UPPER = 20 * 60

# Cleaning
CLEAN_ALL_APPS = False
INTER_CLEANING_WAITING_TIME = 2
CLEANING_FORCE_STOP = True
CLEANING_CLEAR_DATA = False
SLEEP_AFTER_CLEANING = 180

# Ellisys
N_CAPTURE_AFTER_ELLISYS_RESART = 8 # in min


# Windows PC connected to the Ellisys
ELLISYS_HOST = '192.168.1.101'
ELLISYS_PORT = 65432
SOCKET_RECEIVE_BUFFER = 1024
ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED = 50  # Error msg after timeout reached after receiving Command

# Controller laptop connected to the watch and the Window PC
