
# Watches
HUWAWEI_WATCH_IP_PORT = "192.168.1.134:5555"  # Watch ip config.WATCH_IP_PORTess. Change if not connected to Mobnet
FOSILL_WATCH_IP_PORT = "192.168.1.130:5555"
HOME_PACKAGE = "com.google.android.wearable.app"  # To check thaz the home is indeed reached
DEVICES = [HUWAWEI_WATCH_IP_PORT] #, FOSILL_WATCH_IP_PORT]


DEBUG_WATCH = False  # Does not communiacte with ellisys controller
WATCH_CONNECTION_TIMEOUT = 10  # timeout after watch not connected (First instruction)
DEBUG_ELLISYS = False

# Apps
APPLICATIONS_FNAME = "applications.yaml"  # Applications actions instr. & data
N_REPEAT_CAPTURE = 40
REACH_LEFT_STATE = False
WAITING_TIME_AFTER_START_CAPTURE = 4  # Before lauching an action on the watch
WAITING_TIME_BEFORE_STOP_CAPTURE = 2
KEEP_ONLY =["HealthyRecipes", "Sleep", "Medisafe","Lifesum", "Qardio", "DiabetesM"] # FindMyPhone Applications to keep for the automation
SKIPPING = ["Stopwatch"]

# Simulation
CLOSING_METHOD = "force_stop" # Either close_app or background or force_stop
CLEAR_WHEN_CHANGE_APP_AFTER_BACKGROUND = False  # Make a clear when changing to a new action after a background close
LOGIN_BEFORE_CAPTURE = True
WAITING_TIME_AFTER_OPEN_WHEN_OPEN_IS_NOT_AN_ACTION = 10  # Such that the app reach a stable stat
WAITING_TIME_AFTER_CLOSING_WHEN_CLOSING_IS_NOT_AN_ACTION = 25 # Such that the app reach a stable stat after closing
PACKAGE_NOT_TO_STOP = ["com.google.android.wearable.app", "com.huawei.health", "com.huawei.watch.supersavepower"]

N_CAPTURE_AFTER_FAKE = 20  # 0 to not make any fake captures
FAKE_WAITTING_TIME = 50

# numbering
FLUSH_CAPTURE_NUMBER = False
FLUSH_CAPTURE_NUMBER = FLUSH_CAPTURE_NUMBER and not REACH_LEFT_STATE  ## Only flush if we do not want to reach the left state
EXPERIENCE_NUMBER = 3

# Cleaning
CLEAN_ALL_APPS = False
INTER_CLEANING_WAITING_TIME = 5
CLEANING_FORCE_STOP = True
CLEANING_CLEAR_DATA = False
SLEEP_AFTER_CLEANING = 180

# Ellisys
N_CAPTURE_AFTER_ELLISYS_RESART = 15 # 0 for none
RESTART_ELLISYS_WHEN_CHANGING_APP = True

# Windows PC connected to the Ellisys
ELLISYS_HOST = '192.168.1.101'
ELLISYS_PORT = 65432
SOCKET_RECEIVE_BUFFER = 1024
ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED = 50  # Error msg after timeout reached after receiving Command

# Controller MAC laptop connected to the watch and the Window PC
CONTROLLER_HOST = ""
