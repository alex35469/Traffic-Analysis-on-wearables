#Include <File.au3>
#Include <Array.au3>

$path = "C:\Users\ellisys\Desktop\export\"
$FileList = _FileListToArray($path, "*.btt")

$ellisys_app = "C:\Program Files (x86)\Ellisys\Ellisys Bluetooth Analyzer\Ellisys.BluetoothAnalyzer.exe"

For $i = 1 To UBound($FileList)-1

	$f = $FileList[$i]
    ConsoleWrite($f & @CRLF)

	WinKill("Ellisys Bluetooth Analyzer")
	Local $process = ProcessList("Ellisys.BluetoothAnalyzer.exe")
	For $j = 1 To $process[0][0]
		ProcessClose($process[$j][1])
	Next

	Run($ellisys_app)
	WinWaitActive("Ellisys Bluetooth Analyzer")
	Sleep(5000)

	Send("^o")
	Sleep(1000)
	ClipPut($path & $f)
	Send("^v")
	Sleep(1000)
	Send("{ENTER}")

	Sleep(3000)

	Send("^e")
	Sleep(1000)
	Send("!n")
	Sleep(1000)
	Send("{TAB 8}")
	Send("{DOWN 2}")
	Sleep(1000)
	Send("!n")
	Sleep(1000)
	Send("!n")

	Sleep(3000)
Next