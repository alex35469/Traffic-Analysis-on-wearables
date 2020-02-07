
CMD_OPEN_ELLISYS = 'open'
CMD_CLOSE_ELLISYS = 'close'
CMD_START_CAPTURE = 'start' #has a SPACE + filename afterwards
CMD_STOP_CAPTURE = 'stop'
CMD_SAVE_CAPTURE = 'save' #has a SPACE + filename afterwards
MESSAGE_ACK = 'ack'  # has a SPACE + some info afterwards
MESSAGE_FAIL = 'fail'  # has a SPACE + some info afterwards


def NewStartCaptureCommand(payload):
    if payload != "":
        payload = " " + payload
    return CMD_START_CAPTURE + payload

def NewSaveCaptureCommand(payload):
    if payload != "":
        payload = " " + payload
    return CMD_SAVE_CAPTURE + payload

def NewACK(payload):
    if payload != "":
        payload = " " + payload
    return MESSAGE_ACK + payload

def NewFAIL(payload):
    if payload != "":
        payload = " " + payload
    return MESSAGE_FAIL + payload
