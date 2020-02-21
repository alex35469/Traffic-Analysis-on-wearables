#Include <File.au3>
#Include <Array.au3>

$path = "C:\Users\ellisys\Desktop\Traffic-Analysis-on-wearables\Classification\data\open\"
$FileList = _FileListToArray($path, "*.btt")

$ellisys_app = "C:\Program Files (x86)\Ellisys\Ellisys Bluetooth Analyzer\Ellisys.BluetoothAnalyzer.exe"

WinKill("Ellisys Bluetooth Analyzer")
Local $process = ProcessList("Ellisys.BluetoothAnalyzer.exe")
For $j = 1 To $process[0][0]
	ProcessClose($process[$j][1])
Next

Run($ellisys_app)
WinWaitActive("Ellisys Bluetooth Analyzer", "Welcome")

For $i = 1 To UBound($FileList)-1

	$f = $FileList[$i]
	ConsoleWrite($f & @CRLF)

	; WinKill("Ellisys Bluetooth Analyzer")
	; Local $process = ProcessList("Ellisys.BluetoothAnalyzer.exe")
	; For $j = 1 To $process[0][0]
	; 	ProcessClose($process[$j][1])
	; Next

	

	Send("^o")
	WinWaitActive("Open", "&Open")
	Sleep(100)
	WinActivate("Open")
	ClipPut($path & $f)
	Send("^v")
	WinWaitActive("Open", $f)
	Send("{ENTER}")

	$res = WinWaitActive($f & " - Ellisys Bluetooth Analyzer", "Search", 5)
	If $res == 0 Then
		WinWaitActive($f & "* - Ellisys Bluetooth Analyzer", "Search", 2)
	EndIf
	Send("^e")
	WinWaitActive("Export", "Export")

	Send("!n")
	WinWaitActive("Export", "&Next >")
	Send("{TAB 8}")
	Send("{DOWN 2}")
	Send("!n")
	WinWaitActive("Export", "Fi&nish")
	Send("!n")
	Sleep(500)
	Send("^s")
	;If WinActive($f  & " - Ellisys Bluetooth Analyzer") Then
	WinActivate($f  & " - Ellisys Bluetooth Analyzer")

Next