
# Watches
HUWAWEI_WATCH_IP_PORT = "192.168.1.134:5555"  # Watch ip config.WATCH_IP_PORTess. Change if not connected to Mobnet
FOSILL_WATCH_IP_PORT = "192.168.1.130:5555"
HOME_PACKAGE = "com.google.android.wearable.app"

# phone
PHONE_NAME = "Pixel 2"

DEBUG_WATCH = True  # Does not communiacte with ellisys controller
WATCH_CONNECTION_TIMEOUT = 5  # timeout after watch not connected (First instruction)


# simulation param
RESTART_ELLISYS_WHEN_CHANGING_APP = True
N_REPEAT_CAPTURE = 2
WAITING_TIME_AFTER_START_CAPTURE = 2
WAITING_TIME_BEFORE_STOP_CAPTURE = 2
KEEP_ONLY = ["GoogleFit", "DailyTracking"]  # Applications to keep for the automation
DEVICES = [HUWAWEI_WATCH_IP_PORT, FOSILL_WATCH_IP_PORT]
DEVICES = [HUWAWEI_WATCH_IP_PORT]
PERFORM_EXTRA_CHECK = True  # Check that packages have been proprely opened

# Windows PC connected to the Ellisys
ELLISYS_HOST = '192.168.1.101'
ELLISYS_PORT = 65432
SOCKET_RECEIVE_BUFFER = 1024
ELLYSIS_TIMEOUT_AFTER_COMMAND_RECEIVED = 50  # Error msg after timeout reached after receiving Command

# Controller MAC laptop connected to the watch and the Window PC
CONTROLLER_HOST = ""
