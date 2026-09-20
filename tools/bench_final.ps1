#!/usr/bin/env pwsh
# Final benchmark runner - uses 'py' command

$Method = "bench-gui-haiku-medium"
$Title = "GUIBENCH_v0.vi"

cd 'G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop'

function Run-Op {
    param([string]$Op, [int]$Trial, [scriptblock]$ActionBlock)

    & py tools/bench/verify_op.py revert $Method $Op $Trial | Out-Null
    Start-Sleep -Seconds 1

    $shotBefore = "tools/bench/shot_${Op}_${Trial}_before.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotBefore 2>$null

    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    Start-Sleep -Seconds 0.5

    & $ActionBlock

    $shotAfter = "tools/bench/shot_${Op}_${Trial}_after.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotAfter 2>$null

    & py tools/bench/verify_op.py verify $Method $Op $Trial --shots "$shotBefore,$shotAfter" --gated "action" 2>&1 | Out-Null

    Start-Sleep -Seconds 0.5
}

for ($i = 1; $i -le 3; $i++) {
    Run-Op "U1_move" $i {
        & .\tools\lv_gui.ps1 -Action drag -X 500 -Y 350 -X2 600 -Y2 400 -Exception Approved -Evidence "vision bench" 2>$null
    }
    Write-Host "U1_move $i done"
}

for ($i = 1; $i -le 3; $i++) {
    Run-Op "U2_place" $i {
        & .\tools\lv_gui.ps1 -Action rclick -X 700 -Y 500 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Seconds 0.3
        & .\tools\lv_gui.ps1 -Action click -X 850 -Y 400 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Seconds 0.2
        & .\tools\lv_gui.ps1 -Action click -X 900 -Y 450 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Seconds 0.1
        & .\tools\lv_gui.ps1 -Action click -X 900 -Y 450 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Seconds 0.1
        & .\tools\lv_gui.ps1 -Action click -X 920 -Y 480 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Seconds 0.2
        & .\tools\lv_gui.ps1 -Action click -X 1111 -Y 641 -Exception Approved -Evidence "vision bench" 2>$null
    }
    Write-Host "U2_place $i done"
}

for ($i = 1; $i -le 3; $i++) {
    Run-Op "U4_menu" $i {
        & .\tools\lv_gui.ps1 -Action rclick -X 620 -Y 360 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Seconds 0.3
        & .\tools\lv_gui.ps1 -Action click -X 700 -Y 390 -Exception Approved -Evidence "vision bench" 2>$null
    }
    Write-Host "U4_menu $i done"
}

for ($i = 1; $i -le 3; $i++) {
    & py tools/bench/verify_op.py revert $Method "U5_dialog" $i | Out-Null
    Start-Sleep -Seconds 1

    $shotBefore = "tools/bench/shot_U5_dialog_${i}_before.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotBefore 2>$null

    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    Start-Sleep -Seconds 0.5

    & .\tools\lv_gui.ps1 -Action keys -Key "^f" -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Seconds 1.5

    & py tools/bench/verify_op.py u5open $Method "U5_dialog" $i 2>$null
    Start-Sleep -Seconds 0.2

    $shotOpen = "tools/bench/shot_U5_dialog_${i}_open.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotOpen 2>$null

    & .\tools\lv_gui.ps1 -Action click -X 800 -Y 550 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Seconds 0.5

    $shotAfter = "tools/bench/shot_U5_dialog_${i}_after.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotAfter 2>$null

    & py tools/bench/verify_op.py verify $Method "U5_dialog" $i --shots "$shotBefore,$shotOpen,$shotAfter" --gated "keys,click" 2>&1 | Out-Null

    Write-Host "U5_dialog $i done"
}

Write-Host "All trials complete"
