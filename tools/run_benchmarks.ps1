#!/usr/bin/env pwsh
# Simple benchmark runner - execute all 12 trials

$Method = "bench-gui-haiku-medium"
$Title = "GUIBENCH_v0.vi"

cd 'G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop'

# U1_move - 3 trials
for ($i = 1; $i -le 3; $i++) {
    Write-Host "U1_move trial $i"
    & py tools/bench/verify_op.py revert $Method U1_move $i | Out-Null
    Start-Sleep -Seconds 1
    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    & .\tools\lv_gui.ps1 -Action drag -X 500 -Y 350 -X2 600 -Y2 400 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 500
    & py tools/bench/verify_op.py verify $Method U1_move $i --shots 2 --gated 1 2>&1
}

# U2_place - 3 trials
for ($i = 1; $i -le 3; $i++) {
    Write-Host "U2_place trial $i"
    & py tools/bench/verify_op.py revert $Method U2_place $i | Out-Null
    Start-Sleep -Seconds 1
    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    & .\tools\lv_gui.ps1 -Action rclick -X 700 -Y 500 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 200
    & .\tools\lv_gui.ps1 -Action click -X 850 -Y 400 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 100
    & .\tools\lv_gui.ps1 -Action click -X 900 -Y 450 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 100
    & .\tools\lv_gui.ps1 -Action click -X 900 -Y 450 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 100
    & .\tools\lv_gui.ps1 -Action click -X 920 -Y 480 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 100
    & .\tools\lv_gui.ps1 -Action click -X 1111 -Y 641 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 500
    & py tools/bench/verify_op.py verify $Method U2_place $i --shots 2 --gated 6 2>&1
}

# U4_menu - 3 trials
for ($i = 1; $i -le 3; $i++) {
    Write-Host "U4_menu trial $i"
    & py tools/bench/verify_op.py revert $Method U4_menu $i | Out-Null
    Start-Sleep -Seconds 1
    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    & .\tools\lv_gui.ps1 -Action rclick -X 620 -Y 360 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 200
    & .\tools\lv_gui.ps1 -Action click -X 700 -Y 390 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 500
    & py tools/bench/verify_op.py verify $Method U4_menu $i --shots 2 --gated 2 2>&1
}

# U5_dialog - 3 trials
for ($i = 1; $i -le 3; $i++) {
    Write-Host "U5_dialog trial $i"
    & py tools/bench/verify_op.py revert $Method U5_dialog $i | Out-Null
    Start-Sleep -Seconds 1
    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    & .\tools\lv_gui.ps1 -Action keys -Key "^f" -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 1500
    & py tools/bench/verify_op.py u5open $Method U5_dialog $i 2>$null
    Start-Sleep -Milliseconds 200
    & .\tools\lv_gui.ps1 -Action click -X 800 -Y 550 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Milliseconds 500
    & py tools/bench/verify_op.py verify $Method U5_dialog $i --shots 3 --gated 2 2>&1
}

Write-Host "All trials complete"
