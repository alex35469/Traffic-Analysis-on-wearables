
CMD_OPEN_ELLISYS = 'open'
CMD_CLOSE_ELLISYS = 'close'
CMD_START_CAPTURE = 'start' #has a SPACE + filename afterwards
CMD_STOP_CAPTURE = 'stop'
CMD_SAVE_CAPTURE = 'save' #has a SPACE + filename afterwards
MESSAGE_ACK = 'ack' #has a SPACE + some info afterwards

def NewStartCaptureCommand(payload):
    return CMD_START_CAPTURE + ' ' + payload

def NewSaveCaptureCommand(payload):
    return CMD_SAVE_CAPTURE + ' ' + payload

def NewACK(payload):
    return MESSAGE_ACK + ' ' + payload