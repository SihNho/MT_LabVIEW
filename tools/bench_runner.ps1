#!/usr/bin/env pwsh
# Benchmark cell runner for bench-gui-haiku-medium
# Executes all 12 revert/act/verify pairs for U1, U2, U4, U5

$Method = "bench-gui-haiku-medium"
$Title = "GUIBENCH_v0.vi Block Diagram"
$ProjectRoot = "G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
$VerifyOutput = @()

# Helper to run a trial
function Run-Trial {
    param(
        [string]$Op,
        [int]$Trial,
        [string]$ActionScript
    )

    Write-Host "=== $Op Trial $Trial ==="

    # Revert
    Write-Host "Reverting..."
    $revertOutput = & python tools/bench/verify_op.py revert $Method $Op $Trial 2>&1
    Write-Host "Revert done"
    Start-Sleep -Milliseconds 500

    # Capture screenshot before action
    Write-Host "Capturing screenshot..."
    $screenshotFile = "tools\bench\shot_${Op}_${Trial}_before.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $screenshotFile
    if (-not (Test-Path $screenshotFile)) {
        Write-Host "ERROR: Screenshot failed"
        return
    }
    Write-Host "Screenshot saved: $screenshotFile"

    # Focus window
    & .\tools\lv_gui.ps1 -Action focus -Title $Title
    Start-Sleep -Milliseconds 200

    # Execute action
    Write-Host "Executing action..."
    Invoke-Expression $ActionScript
    Start-Sleep -Milliseconds 500

    # Capture screenshot after action
    $shotAfter = "tools\bench\shot_${Op}_${Trial}_after.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotAfter

    # Verify
    Write-Host "Verifying..."
    $verifyCmd = "py tools/bench/verify_op.py verify $Method $Op $Trial --shots $screenshotFile,$shotAfter --gated `"$ActionScript`""
    $verifyOutput = & python tools/bench/verify_op.py verify $Method $Op $Trial --shots "$screenshotFile,$shotAfter" --gated "$ActionScript" 2>&1
    Write-Host "Verify output: $verifyOutput"

    return $verifyOutput
}

cd $ProjectRoot

# ===== U1_move: Drag Invoke Node by +100 px right, +50 px down =====
$u1Action = '& .\tools\lv_gui.ps1 -Action drag -X 500 -Y 300 -X2 600 -Y2 350 -Exception Approved -Evidence "vision bench"'

for ($trial = 1; $trial -le 3; $trial++) {
    $output = Run-Trial "U1_move" $trial $u1Action
    $VerifyOutput += $output
    Start-Sleep -Milliseconds 300
}

# ===== U2_place: Right-click → Functions → Array (×2) → Index Array → click at (1111, 641) =====
# This is complex - need to capture and read coordinates from screenshot
$u2Trial1Action = '& .\tools\lv_gui.ps1 -Action rclick -X 700 -Y 500 -Exception Approved -Evidence "vision bench"; Start-Sleep -Milliseconds 400; & .\tools\lv_gui.ps1 -Action click -X 800 -Y 400 -Exception Approved -Evidence "vision bench"; Start-Sleep -Milliseconds 300; & .\tools\lv_gui.ps1 -Action click -X 820 -Y 430 -Exception Approved -Evidence "vision bench"; Start-Sleep -Milliseconds 300; & .\tools\lv_gui.ps1 -Action click -X 900 -Y 480 -Exception Approved -Evidence "vision bench"; Start-Sleep -Milliseconds 300; & .\tools\lv_gui.ps1 -Action click -X 1111 -Y 641 -Exception Approved -Evidence "vision bench"'

for ($trial = 1; $trial -le 3; $trial++) {
    $output = Run-Trial "U2_place" $trial $u2Trial1Action
    $VerifyOutput += $output
    Start-Sleep -Milliseconds 300
}

# ===== U4_menu: Right-click Position row → Change To Write =====
$u4Action = '& .\tools\lv_gui.ps1 -Action rclick -X 620 -Y 350 -Exception Approved -Evidence "vision bench"; Start-Sleep -Milliseconds 400; & .\tools\lv_gui.ps1 -Action click -X 700 -Y 370 -Exception Approved -Evidence "vision bench"'

for ($trial = 1; $trial -le 3; $trial++) {
    $output = Run-Trial "U4_menu" $trial $u4Action
    $VerifyOutput += $output
    Start-Sleep -Milliseconds 300
}

# ===== U5_dialog: Ctrl+F, wait, u5open check, close with Cancel =====
$u5Action = '& .\tools\lv_gui.ps1 -Action keys -Key "^f" -WaitMs 1500 -Exception Approved -Evidence "vision bench"'

for ($trial = 1; $trial -le 3; $trial++) {
    Write-Host "=== U5_dialog Trial $trial ==="

    # Revert
    $revertOutput = & python tools/bench/verify_op.py revert $Method "U5_dialog" $trial 2>&1
    Start-Sleep -Milliseconds 500

    # Capture screenshot
    $screenshotFile = "tools\bench\shot_U5_dialog_${trial}_before.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $screenshotFile

    # Focus and issue Ctrl+F
    & .\tools\lv_gui.ps1 -Action focus -Title $Title
    Start-Sleep -Milliseconds 200
    & .\tools\lv_gui.ps1 -Action keys -Key "^f" -Exception Approved -Evidence "vision bench"
    Start-Sleep -Milliseconds 1500

    # Run u5open to check dialog state
    $u5openOutput = & python tools/bench/verify_op.py u5open $Method "U5_dialog" $trial 2>&1
    Write-Host "U5open output: $u5openOutput"
    Start-Sleep -Milliseconds 300

    # Capture screenshot with dialog
    $shotWithDialog = "tools\bench\shot_U5_dialog_${trial}_open.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotWithDialog

    # Click Cancel button to close dialog
    & .\tools\lv_gui.ps1 -Action click -X 800 -Y 550 -Exception Approved -Evidence "vision bench"
    Start-Sleep -Milliseconds 500

    # Capture final screenshot
    $shotAfter = "tools\bench\shot_U5_dialog_${trial}_after.png"
    & .\tools\lv_gui.ps1 -Action shotwin -Title $Title -Out $shotAfter

    # Verify
    $verifyOutput = & python tools/bench/verify_op.py verify $Method "U5_dialog" $trial --shots "$screenshotFile,$shotWithDialog,$shotAfter" --gated "keys,click" 2>&1
    Write-Host "Verify output: $verifyOutput"
    $VerifyOutput += $verifyOutput
    Start-Sleep -Milliseconds 300
}

# Output all verify lines
Write-Host "`n`n===== FINAL RESULTS ====="
foreach ($line in $VerifyOutput) {
    Write-Host $line
}
