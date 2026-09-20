@echo off
rem run_matrix.cmd — launcher for the GUI-executor matrix driver, meant to be started by Windows
rem Task Scheduler (outside any Claude Code process tree / job object: two detached drivers died
rem at cell boundaries on 2026-09-05). Edit the CELLS/REPEAT lines, then:
rem   Register-ScheduledTask ... -Action (New-ScheduledTaskAction -Execute cmd.exe -Argument '/c "<this file>"')
set CELLS=sonnet-medium
set REPEAT=sonnet-medium=1
cd /d "%~dp0..\.."
py tools\bench\matrix_run.py --cells %CELLS% --repeat %REPEAT% >> tools\bench\matrix_run.stdout3.txt 2>&1
