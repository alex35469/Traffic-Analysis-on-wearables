; Starting a capture. Note that Ellisys has to be running into foreground
; And that the ellisys hardware is connected and recognized by ellisys software

; Get the window name
$WinName = "Ellisys Bluetooth Analyzer"
$InstanceNb = "36"

If $CmdLine[0] == 1 Then
  $WinName = $CmdLine[1] & ".btt - " & $WinName
  $InstanceNb = "44"
EndIf


; Filter on pixel 2 (only at the start)
If $CmdLine[0] == 0 Then
  $HWND = WinActivate($WinName)
  ; ControlClick($HWND, "", "[CLASS:WindowsForms10.Window.8.app.0.ea119_r6_ad1; INSTANCE:" & $InstanceNb &"]", "left", 1, 819, 10)
  ControlClick($HWND, "", "[CLASS:WindowsForms10.Window.8.app.0.ea119_r6_ad1; NAME:toolBar]", "left", 1, 819, 10)
  WinWaitActive("Device Traffic Filters", "&OK")
  Sleep(500)
  ;Send("Pixel 2")
  Send("HUAWEI WATCH 2")
  Send("{ENTER}")
  Send("{ENTER}")
EndIf

WinActivate($WinName)
Send("^r")
WinWaitActive("Recording from BV1-26140 - Ellisys Bluetooth Analyzer", "")
