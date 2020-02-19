
# Watches
HUWAWEI_WATCH_IP_PORT = "192.168.1.134:5555"  # Watch ip config.WATCH_IP_PORTess. Change if not connected to Mobnet
FOSILL_WATCH_IP_PORT = "192.168.1.130:5555"
HOME_PACKAGE = "com.google.android.wearable.app"  # To check thaz the home is indeed reached
DEVICES = [HUWAWEI_WATCH_IP_PORT] #, FOSILL_WATCH_IP_PORT]


DEBUG_WATCH = False  # Does not communiacte with ellisys controller
WATCH_CONNECTION_TIMEOUT = 10  # timeout after watch not connected (First instruction)
DEBUG_ELLISYS = True

# Apps
APPLICATIONS_FNAME = "applications.yaml"  # Applications actions instr. & data
N_REPEAT_CAPTURE = 20
WAITING_TIME_AFTER_START_CAPTURE = 4  # Before lauching an action on the watch
WAITING_TIME_BEFORE_STOP_CAPTURE = 2
KEEP_ONLY = "all"  # Applications to keep for the automation
SKIPPING = ["Endomondo", "Reminders", "FindMyPhone","DiabetesM", "PlayStore",
            "WearCasts", "KeepNotes", "HeartRate", "ASB","Qardio", "Outlook",
            "DailyTracking", "Spotify", "Stopwatch", "Flashlight"]

CLOSING_METHOD = "close_app" # Either close_app or background
WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION = 10  # Such that the app reach a stable stat

# Cleaning
CLEAN_ALL_APPS = False
INTER_CLEANING_WAITING_TIME = 5
FORCE_STOP_CLEANING = True
CLEAR_DATA_CLEANING = False

# Ellisys
N_CAPTURE_AFTER_ELLISYS_RESART = 15 # 0 for none
RESTART_ELLISYS_WHEN_CHANGING_APP = True

# Windows PC connected to the Ellisys
ELLISYS_HOST = '192.168.1.101'
ELLISYS_PORT = 65432
SOCKET_RECEIVE_BUFFER = 1024
ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED = 150  # Error msg after timeout reached after receiving Command

# Controller MAC laptop connected to the watch and the Window PC
CONTROLLER_HOST = ""
