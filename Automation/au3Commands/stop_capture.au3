; Stop a capture. Note that Ellisys has to be running into foreground
; And that the ellisys hardware is connected and recognized by ellisys software

WinActivate("Recording from BV1-26140 - Ellisys Bluetooth Analyzer")
Send("^+r")
$res = WinWaitActive("Untitled* - Ellisys Bluetooth Analyzer", "", 15)

If $res == 0 Then
	Exit(1)
EndIf



Exit(0)
