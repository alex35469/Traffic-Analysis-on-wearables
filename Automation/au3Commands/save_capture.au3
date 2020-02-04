; save a capture

$FNAME = $CmdLine[1]

Sleep(2000)
; WinWaitActive("Recording from BV1-26140 - Ellisys Bluetooth Analyzer")
Send("!{LSHIFT}r")

Sleep(500)
Send("^s")

WinWaitActive("Save", "File &name:")
Send($FNAME)
Send("{ENTER}")
