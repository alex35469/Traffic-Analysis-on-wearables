#include <AutoItConstants.au3>

$HWND = WinActivate("Ellisys Bluetooth Analyzer", "")
ControlClick($HWND, "", "[CLASS:WindowsForms10.Window.8.app.0.ea119_r6_ad1; INSTANCE:36]", "left", 1, 819, 10)
WinWaitActive("Device Traffic Filters", "&OK")

Send("Pixel 2")
Send("{ENTER}")
Send("{ENTER}")
