; save a capture

$FNAME = $CmdLine[1]

; WinActivate("Untitled* - Ellisys Bluetooth Analyzer")
Send("^s")

$res = WinWaitActive("Save", "File &name:", 5)

If $res == 0 Then
  ; Kill all restart and
  _RunAU3("au3Commands\close_ellisys.au3")
  Sleep(3000)
  Run("C:\Program Files (x86)\Ellisys\Ellisys Bluetooth Analyzer\Ellisys.BluetoothAnalyzer.exe")
  WinWaitActive("Ellisys Bluetooth Analyzer")
  Sleep(8000)
  WinActivate("Lost files recovery", "Delete all")
  Send("{ENTER}")
  _RunAU3("au3Commands\start_capture.au3")
  WinWaitActive("Recording from BV1-26140 - Ellisys Bluetooth Analyzer")
  Sleep(2000)  
  _RunAU3("au3Commands\stop_capture.au3")
  Sleep(1500)

  WinActivate("Untitled* - Ellisys Bluetooth Analyzer" )
  Send("^s")

  WinWaitActive("Save", "File &name:")
  Send($FNAME & "_errorSave")
  Send("{ENTER}")
  Exit(1)

EndIf

Send($FNAME)
Send("{ENTER}")

$res = WinWaitActive($FNAME & ".btt - Ellisys Bluetooth Analyzer", "", 5)


Exit(0)




Func _RunAU3($sFilePath, $sWorkingDir = "", $iShowFlag = @SW_SHOW, $iOptFlag = 0)
    Return Run('"' & @AutoItExe & '" /AutoIt3ExecuteScript "' & $sFilePath & '"', $sWorkingDir, $iShowFlag, $iOptFlag)
EndFunc   ;==>_RunAU3
