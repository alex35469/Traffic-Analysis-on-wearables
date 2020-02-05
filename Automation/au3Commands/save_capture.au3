; save a capture

$FNAME = $CmdLine[1]

WinActivate("Untitled* - Ellisys Bluetooth Analyzer")
Send("^s")

WinWaitActive("Save", "File &name:")
Send($FNAME)
Send("{ENTER}")
WinWaitActive($FNAME & ".btt - Ellisys Bluetooth Analyzer")
