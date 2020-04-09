import sys

# Watches Settings
HUWAWEI_WATCH_IP_PORT = "192.168.1.134:5555"  # '192.168.43.17:5555' Watch ip config.WATCH_IP_PORTess. Change if not connected to Mobnet
FOSILL_WATCH_IP_PORT = "192.168.1.129:5555"
HOME_PACKAGE = "com.google.android.wearable.app"  # To check thaz the home is indeed reached
DEVICES = [HUWAWEI_WATCH_IP_PORT] #, FOSILL_WATCH_IP_PORT]

# Windows PC connected to the Ellisys Settings
ELLISYS_HOST = '192.168.1.101'
ELLISYS_PORT = 65432
SOCKET_RECEIVE_BUFFER = 1024
ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED = 130  # Error msg after timeout reached after receiving Command


# Debugging settings
DEBUG_ELLISYS = False
DEBUG_WATCH = False  # Does not communiacte with ellisys controller
WATCH_CONNECTION_TIMEOUT = 24  # timeout after watch not connected (First instruction)


# Simulation settings
CAPTURE_DURATION_MINUTES = 20  # Time duration of the capture in minutes
N_REPEAT_CAPTURE = 24   # Total number of captures 1 capt might have many actions
CLOSING_METHOD = "force_stop" # Either close_app or background or force_stop
WAITING_TIME_BEFORE_CLOSING = 5
WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION = 8  # Such that the app reach a stable stat
WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION = 3 # Such that the app reach a stable stat after closing
SPEAK_UP_INSTRUCTION = True  # Allows computer to speak up what it is doing (Linux Only)


# Apps settings
APPLICATIONS_FNAME = "applications-longrun.yaml"  # Applications actions instr. & data
KEEP_ONLY = [] # FindMyPhone Applications to keep for the automation
SKIPPING = ['Timer', 'Qardio', "Camera", "AppInTheAir",
            'GooglePay', 'PlayMusic', 'ASB',
            'DailyTracking', 'NoApp', 'Sleep', 'UARecord',
            'Alarm', 'HeartRate', 'AthkarOfPrayer', 'WearCasts', 'Workout',
            'Medisafe', 'Battery', 'Phone', 'Reminders',
            'DuaKhatqmAlQuran', 'Flashlight', 'SmartZmanim']
PACKAGE_NOT_TO_STOP = ["com.google.android.wearable.app", "com.huawei.health", "com.huawei.watch.supersavepower"]


# Longrun capture Specific
APP_CHOICE = "user_interact_pattern" # Prior probabilites of picking action
WAITING_METHOD = "user_interact_pattern"  # could be deterministic, uniform or exponential

USER_INTERACTION_PATTERN_DEVIATION = True
WAITING_TIME = 20  # Iner-acation Waiting in seconds when deterministic is chosen as WAITING_METHOD
# When method is uniform the waiting time follows
# U(WAITING_TIME + WAITING_DEVIATION_LOWER,WAITING_TIME + WAITING_DEVIATION_UPPER  )
WAITING_DEVIATION_LOWER = -10
WAITING_DEVIATION_UPPER = 10
EXPOVARIATE_LAMBDA_MINUTE = 0.1


# Cleaning Settings
CLEAN_ALL_APPS = False
INTER_CLEANING_WAITING_TIME = 2
CLEANING_FORCE_STOP = True
CLEANING_CLEAR_DATA = False
SLEEP_AFTER_CLEANING = 180






CAPTURE_DURATION = CAPTURE_DURATION_MINUTES * 60  # converting in seconds
EXPOVARIATE_LAMBDA = EXPOVARIATE_LAMBDA_MINUTE / 60  # We divide by 60 to convert into seconds

if APP_CHOICE not in ["equiprobable", "user_interact_pattern"]:
    print("APP_CHOICE not recognized.\nPlease, check longrun_config.")
    sys.exit(1)


if WAITING_METHOD not in ["deterministic", "uniform", "user_interact_pattern"]:
    print("WAITING_METHOD not recognized.\nPlease, check longrun_config.")
    sys.exit(1)
