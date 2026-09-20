# motor_send_pi.ps1 - the PI (C-863.11, COM3) side of tools/motor_gate.py. THREE modes, one port open each:
#   -Mode limits-set     : SPA 1 0x15 <ExpectHi> + SPA 1 0x30 <ExpectLo>, then read TMN?/TMX?/SPA? back.
#   -Mode limits-release : the same write with the release values the gate passes (0 .. 52), then read back.
#   -Mode send           : READ THE CONTROLLER LIMITS FIRST, inside this same port open and BEFORE the transmit;
#                          refuse (exit 7) unless they match -ExpectLo/-ExpectHi (from tools/bench/motor_limits.json)
#                          within -Tol; then transmit ONE 'MOV 1 <n>' and poll POS? until the axis settles.
# REWORKED 2026-09-18: the old private 0..39 re-check is GONE - the real limit is the controller's (TMN/TMX), and
# what this script now proves is that the controller is really carrying the file's limits at transmit time.
# Never WPA (the soft limits are RAM by design). Every mode prints one machine-readable 'LIMITS TMN=.. TMX=..' line
# AFTER the write; the limits-set/limits-release modes ALSO print 'PRELIMITS TMN=<n> TMX=<n>' BEFORE it (2026-09-18,
# STATUS.md OPEN 55) - that is the only line that says what the controller held on arrival.
# send mode refuses to run unless the gate's one-shot token file names this exact command (the gate writes it after
# an ALLOW decision and this script deletes it before opening the port), so running this file by hand sends nothing.
# guard_bash.py also blocks it by name.
param(
    [ValidateSet('send', 'limits-set', 'limits-release')][string]$Mode = 'send',
    [string]$Command = '',
    [string]$TokenFile = '',
    [double]$ExpectLo = 0.0,
    [double]$ExpectHi = 39.0,
    [double]$Tol = 0.001,
    [string]$Port = 'COM3',
    [int]$Baud = 115200,
    [int]$SettleTimeoutS = 90
)
$ErrorActionPreference = 'Stop'
if ($Mode -eq 'send') {
    if (-not (Test-Path -LiteralPath $TokenFile)) { Write-Output 'SEND REFUSED: no gate token'; exit 7 }
    $tok = (Get-Content -LiteralPath $TokenFile -Raw).Trim()
    Remove-Item -LiteralPath $TokenFile -Force -Confirm:$false
    if ($tok -ne $Command) { Write-Output 'SEND REFUSED: token does not name this command'; exit 7 }
    if ($Command -notmatch '^MOV 1 (\d+(?:\.\d+)?)$') { Write-Output "SEND REFUSED: only 'MOV 1 <n>' is transmittable"; exit 7 }
    $target = [double]$Matches[1]
}

$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 600
$sp.NewLine = "`n"
function Ask([string]$q) {
    $sp.DiscardInBuffer(); $sp.WriteLine($q)
    try { return $sp.ReadLine().Trim() } catch { return '' }
}
function Num([string]$r) { if ($r -match '=\s*([-+0-9.eE]+)') { return [double]$Matches[1] } return $null }
function ReadLimits() {
    $tmn = Num (Ask 'TMN?'); $tmx = Num (Ask 'TMX?')
    $s15 = Num (Ask 'SPA? 1 0x15'); $s30 = Num (Ask 'SPA? 1 0x30')
    if ($null -eq $tmn -or $null -eq $tmx) { return $null }
    if ($null -eq $s15) { $s15 = $tmx }; if ($null -eq $s30) { $s30 = $tmn }
    return @{ TMN = $tmn; TMX = $tmx; S15 = $s15; S30 = $s30 }
}
try {
    $sp.Open()
    if ($Mode -ne 'send') {
        # The four raw replies are captured ONCE, so the human-readable `before:` line and the
        # machine-readable `PRELIMITS` line below are built from the SAME strings - no extra serial
        # traffic, and the two lines cannot disagree.
        $rPos = Ask 'POS?'; $rTmn = Ask 'TMN?'; $rTmx = Ask 'TMX?'; $rErr = Ask 'ERR?'
        Write-Output ("before: POS?={0} TMN?={1} TMX?={2} ERR?={3}" -f $rPos, $rTmn, $rTmx, $rErr)
        # PRELIMITS = the PRE-WRITE limits, normalised by THIS script's own `Num` parser (:41), so no
        # downstream reader has to know the controller answers `<cmd>=<axis>=<value>` (`TMX?=1=39.00000`).
        # It is printed BEFORE the SPA write, which is the only line that can answer "what did the
        # controller hold when we got here"; the `LIMITS` lines at :58/:78 are printed AFTER the write and
        # answer "did we just set it". Reading the wrong one is a SILENT FALSE GREEN on a motor-limit
        # check (STATUS.md OPEN 55; archive/peer/2026-09-18-tmx-lastfield-parse.md Q2/Q3).
        # If a reply is unreadable `Num` returns $null and the field prints EMPTY, so the downstream
        # anchored regex fails LOUDLY instead of falling through to some other line.
        Write-Output ("PRELIMITS TMN={0} TMX={1}" -f (Num $rTmn), (Num $rTmx))
        $sp.WriteLine(("SPA 1 0x15 {0}" -f $ExpectHi)); Start-Sleep -Milliseconds 250
        $sp.WriteLine(("SPA 1 0x30 {0}" -f $ExpectLo)); Start-Sleep -Milliseconds 250
        Write-Output ("ERR? after SPA = {0}" -f (Ask 'ERR?'))
        $L = ReadLimits
        if ($null -eq $L) { Write-Output 'LIMIT READBACK FAILED: TMN?/TMX? gave no number'; exit 6 }
        Write-Output ("LIMITS TMN={0} TMX={1} SPA15={2} SPA30={3}" -f $L.TMN, $L.TMX, $L.S15, $L.S30)
        if ([math]::Abs($L.TMN - $ExpectLo) -gt $Tol -or [math]::Abs($L.TMX - $ExpectHi) -gt $Tol) {
            Write-Output ("RESULT: MISMATCH - wanted TMN={0} TMX={1}" -f $ExpectLo, $ExpectHi); exit 7
        }
        if ($Mode -eq 'limits-set') {
            # MEASURED 2026-09-18 15:5x: writing SPA 0x15/0x30 leaves the axis UNREFERENCED (FRF? 0), and every MOV
            # then answers ERR 5 before the soft limit is ever consulted (tools/bench/motor_gate2_live.log L2/L3).
            # So the session-start hook restores the reference the ONE way that moves nothing and shifts no zero:
            # RON 1 0 (referencing off - it already is) and POS 1 <the value POS? just returned>, i.e. the SAME
            # number. Never FRF/FNL/FPL/GOH (those MOVE the axis). Nothing else in the fleet may send POS.
            $p0 = Num (Ask 'POS?')
            if ($null -eq $p0) { Write-Output 'REF RESTORE FAILED: POS? gave no number'; exit 6 }
            $sp.WriteLine('RON 1 0'); Start-Sleep -Milliseconds 200
            $sp.WriteLine(("POS 1 {0:0.00000}" -f $p0)); Start-Sleep -Milliseconds 200
            $ron = Num (Ask 'RON?'); $frf = Num (Ask 'FRF?'); $p1 = Num (Ask 'POS?')
            Write-Output ("REFSTATE RON={0} FRF={1} POS={2} POS_BEFORE={3} ERR={4}" -f $ron, $frf, $p1, $p0, (Ask 'ERR?'))
            if ($frf -ne 1) { Write-Output 'RESULT: axis still UNREFERENCED after RON/POS - no move will be allowed'; exit 7 }
            if ([math]::Abs($p1 - $p0) -gt $Tol) { Write-Output 'RESULT: POS CHANGED during the reference restore - zero may have shifted'; exit 7 }
            $L2 = ReadLimits
            if ($null -eq $L2) { Write-Output 'RESULT: limit re-readback failed after the reference restore'; exit 7 }
            Write-Output ("LIMITS TMN={0} TMX={1} SPA15={2} SPA30={3}" -f $L2.TMN, $L2.TMX, $L2.S15, $L2.S30)
            if ([math]::Abs($L2.TMN - $ExpectLo) -gt $Tol -or [math]::Abs($L2.TMX - $ExpectHi) -gt $Tol) {
                Write-Output 'RESULT: MISMATCH - the limits did not survive the reference restore'; exit 7
            }
            $L = $L2
        }
        Write-Output ("RESULT: controller limits are TMN={0} TMX={1} (mode {2})" -f $L.TMN, $L.TMX, $Mode); exit 0
    }

    # --- send: the readback comes FIRST, in this same port open, before anything is transmitted ---
    $L = ReadLimits
    if ($null -eq $L) { Write-Output 'SEND REFUSED: limit readback failed (TMN?/TMX? gave no number)'; exit 7 }
    Write-Output ("LIMITS TMN={0} TMX={1} SPA15={2} SPA30={3}" -f $L.TMN, $L.TMX, $L.S15, $L.S30)
    if ([math]::Abs($L.TMN - $ExpectLo) -gt $Tol -or [math]::Abs($L.TMX - $ExpectHi) -gt $Tol) {
        Write-Output ("SEND REFUSED: controller limits TMN={0} TMX={1} do not match the file ({2}..{3}) - run the session-start hook" -f $L.TMN, $L.TMX, $ExpectLo, $ExpectHi)
        exit 7
    }
    $frf = Num (Ask 'FRF?')
    Write-Output ("before: POS?={0}  SVO?={1}  FRF?={2}  VEL?={3}  ERR?={4}" -f (Ask 'POS?'), (Ask 'SVO?'), $frf, (Ask 'VEL?'), (Ask 'ERR?'))
    if ($frf -ne 1) {
        Write-Output 'SEND REFUSED: the axis is NOT REFERENCED (FRF? 0) - every MOV would answer ERR 5 without ever reaching the soft limit. Run the session-start hook, which restores the reference with RON 1 0 + POS 1 <current>.'
        exit 7
    }
    $sp.WriteLine($Command)
    Write-Output "SENT: $Command"
    $err = Ask 'ERR?'
    Write-Output "ERR? right after send = $err"
    $t0 = Get-Date; $last = $null; $still = 0
    while (((Get-Date) - $t0).TotalSeconds -lt $SettleTimeoutS) {
        Start-Sleep -Milliseconds 500
        $p = Num (Ask 'POS?')
        if ($null -ne $p) {
            if ($p -gt ($ExpectHi + 0.5) -or $p -lt ($ExpectLo - 0.5)) {
                $sp.WriteLine('HLT'); Write-Output "HALT SENT: position $p outside the controller limits $ExpectLo..$ExpectHi"; break
            }
            if ($null -ne $last -and [math]::Abs($p - $last) -lt 0.0005) { $still++ } else { $still = 0 }
            $last = $p
            if ($still -ge 3) { break }
        }
    }
    Write-Output ("after:  POS?={0}  ONT?={1}  ERR?={2}  elapsed={3:n1}s" -f (Ask 'POS?'), (Ask 'ONT?'), (Ask 'ERR?'), ((Get-Date) - $t0).TotalSeconds)
    $final = Num (Ask 'POS?')
    # SUCCESS NEEDS BOTH: the controller accepted the command (ERR? 0 right after the send) AND the axis is at the
    # target. Position alone is not enough - `MOV 1 0` while already at 0 was REJECTED with ERR 5 on 2026-09-18
    # and still printed "reached 0" and exited 0, writing a false position belief into every downstream record
    # (both arms of archive/peer/2026-09-18-pi-err5-unreferenced-*.md, finding D1).
    if ($err -ne '0') { Write-Output "RESULT: REJECTED BY THE CONTROLLER - ERR $err right after send, POS=$final (target $target)"; exit 9 }
    if ($null -ne $final -and [math]::Abs($final - $target) -lt 0.01) { Write-Output "RESULT: reached $final (target $target)"; exit 0 }
    Write-Output "RESULT: NOT at target - final=$final target=$target  (ERR right after send was $err)"; exit 8
}
finally { if ($sp.IsOpen) { $sp.Close() }; $sp.Dispose() }
