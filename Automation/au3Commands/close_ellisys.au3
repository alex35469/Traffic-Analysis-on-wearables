; Closing ellisys

WinKill("Ellisys Bluetooth Analyzer")
Local $process = ProcessList("Ellisys.BluetoothAnalyzer.exe")
For $j = 1 To $process[0][0]
  ProcessClose($process[$j][1])
Next

Sleep(1000)
