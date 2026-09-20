#!/usr/bin/env pwsh
# Simple benchmark runner - captures verify JSON output directly

$Method = "bench-gui-haiku-medium"
$Title = "GUIBENCH_v0.vi Block Diagram"
$Results = @()

cd 'G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop'

function Run-Op {
    param([string]$Op, [int]$Trial, [scriptblock]$ActionBlock)

    # Revert
    py tools/bench/verify_op.py revert $Method $Op $Trial | Out-Null
    Start-Sleep -Ms 300

    # Screenshot before
    $shotBefore = "tools/bench/shot_${Op}_${Trial}_before.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotBefore 2>$null

    # Focus
    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    Start-Sleep -Ms 100

    # Action
    & $ActionBlock

    # Screenshot after
    $shotAfter = "tools/bench/shot_${Op}_${Trial}_after.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotAfter 2>$null

    # Verify - capture the JSON line
    $verifyOut = py tools/bench/verify_op.py verify $Method $Op $Trial --shots "$shotBefore,$shotAfter" --gated "action" 2>&1

    # Extract the JSON line (last line that starts with {)
    $jsonLine = ($verifyOut | Where-Object { $_.Trim().StartsWith('{') } | Select-Object -Last 1).Trim()

    if ($jsonLine) {
        $Results += $jsonLine
        Write-Host "[$Op $Trial] OK"
    } else {
        Write-Host "[$Op $Trial] No JSON output"
    }

    Start-Sleep -Ms 200
}

# U1_move - drag Invoke Node +100 right, +50 down
Write-Host "Running U1_move trials..."
for ($i = 1; $i -le 3; $i++) {
    Run-Op "U1_move" $i {
        & .\tools\lv_gui.ps1 -Action drag -X 500 -Y 350 -X2 600 -Y2 400 -Exception Approved -Evidence "vision bench" 2>$null
    }
}

# U2_place - navigate palette and place Index Array at (1111,641)
Write-Host "Running U2_place trials..."
for ($i = 1; $i -le 3; $i++) {
    Run-Op "U2_place" $i {
        # Right-click canvas
        & .\tools\lv_gui.ps1 -Action rclick -X 700 -Y 500 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Ms 300
        # Click Functions palette (approximate)
        & .\tools\lv_gui.ps1 -Action click -X 850 -Y 400 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Ms 200
        # Click Array category (twice)
        & .\tools\lv_gui.ps1 -Action click -X 900 -Y 450 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Ms 150
        & .\tools\lv_gui.ps1 -Action click -X 900 -Y 450 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Ms 150
        # Click Index Array
        & .\tools\lv_gui.ps1 -Action click -X 920 -Y 480 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Ms 200
        # Click canvas at target location
        & .\tools\lv_gui.ps1 -Action click -X 1111 -Y 641 -Exception Approved -Evidence "vision bench" 2>$null
    }
}

# U4_menu - right-click Property Node Position row and change to write
Write-Host "Running U4_menu trials..."
for ($i = 1; $i -le 3; $i++) {
    Run-Op "U4_menu" $i {
        # Right-click Property Node Position row
        & .\tools\lv_gui.ps1 -Action rclick -X 620 -Y 360 -Exception Approved -Evidence "vision bench" 2>$null
        Start-Sleep -Ms 300
        # Click "Change To Write"
        & .\tools\lv_gui.ps1 -Action click -X 700 -Y 390 -Exception Approved -Evidence "vision bench" 2>$null
    }
}

# U5_dialog - Ctrl+F, wait, check dialog, close with Cancel
Write-Host "Running U5_dialog trials..."
for ($i = 1; $i -le 3; $i++) {
    # Revert
    py tools/bench/verify_op.py revert $Method "U5_dialog" $i | Out-Null
    Start-Sleep -Ms 300

    # Screenshot before
    $shotBefore = "tools/bench/shot_U5_dialog_${i}_before.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotBefore 2>$null

    # Focus
    & .\tools\lv_gui.ps1 -Action focus -Title $Title 2>$null
    Start-Sleep -Ms 100

    # Ctrl+F
    & .\tools\lv_gui.ps1 -Action keys -Key "^f" -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Ms 1500

    # u5open check
    py tools/bench/verify_op.py u5open $Method "U5_dialog" $i 2>$null
    Start-Sleep -Ms 200

    # Screenshot with dialog
    $shotOpen = "tools/bench/shot_U5_dialog_${i}_open.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotOpen 2>$null

    # Click Cancel button
    & .\tools\lv_gui.ps1 -Action click -X 800 -Y 550 -Exception Approved -Evidence "vision bench" 2>$null
    Start-Sleep -Ms 300

    # Screenshot after close
    $shotAfter = "tools/bench/shot_U5_dialog_${i}_after.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotAfter 2>$null

    # Verify
    $verifyOut = py tools/bench/verify_op.py verify $Method "U5_dialog" $i --shots "$shotBefore,$shotOpen,$shotAfter" --gated "keys,click" 2>&1
    $jsonLine = ($verifyOut | Where-Object { $_.Trim().StartsWith('{') } | Select-Object -Last 1).Trim()

    if ($jsonLine) {
        $Results += $jsonLine
        Write-Host "[U5_dialog $i] OK"
    }

    Start-Sleep -Ms 200
}

# Output results
Write-Host "`n===== RESULTS ====="
foreach ($result in $Results) {
    Write-Host $result
}
