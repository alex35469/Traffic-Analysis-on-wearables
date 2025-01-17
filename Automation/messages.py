#!/usr/bin/env python3
"""
Standardization of messages for Ellisys laptop <-> Controller laptop
"""

CMD_OPEN_ELLISYS = 'open'
CMD_CLOSE_ELLISYS = 'close'
CMD_START_CAPTURE = 'start' #has a SPACE + filename afterwards
CMD_STOP_CAPTURE = 'stop'
CMD_SAVE_CAPTURE = 'save' #has a SPACE + filename afterwards
MESSAGE_ACK = 'ack'  # has a SPACE + some info afterwards
MESSAGE_FAIL = 'fail'  # has a SPACE + some info afterwards


def NewStartCaptureCommand(payload):
    """
    Format a sartCapture message
    Args:
        payload : string. Payload contained within the formatted msg
    Return:
        formatted_msg : string. The formatted msg.
    """
    if payload != "":
        payload = " " + payload
    return CMD_START_CAPTURE + payload


def NewSaveCaptureCommand(payload):
    """
    Format a saveCapture message
    Args:
        payload : string. Payload contained within the formatted msg
    Return:
        formatted_msg : string. The formatted msg.
    """
    if payload != "":
        payload = " " + payload
    return CMD_SAVE_CAPTURE + payload


def NewACK(payload):
    """
    Format a ACK message
    Args:
        payload : string. Payload contained within the formatted msg
    Return:
        formatted_msg : string. The formatted msg.
    """
    if payload != "":
        payload = " " + payload
    return MESSAGE_ACK + payload


def NewFAIL(payload):
    """
    Format a FAIL message
    Args:
        payload : string. Payload contained within the formatted msg
    Return:
        formatted_msg : string. The formatted msg.
    """
    if payload != "":
        payload = " " + payload
    return MESSAGE_FAIL + payload


def parse_msg(response):
    """
    Parse a received message.
    Args:
        response : string. Message received.
    Return:
        command : string. Message tape (FAIL or ACK).
        payload : string. COntent of the message.
    """
    command, payload = response, ''
    if ' ' in response:
        parts = response.split(' ', 1)
        command = parts[0].strip()
        payload = parts[1].strip()
    return command, payload
