Failed prediction, card 104-6 (tools/bench/cards/task_104-6.json), log tools/bench/diag_c104f_leg.log, facts tools/bench/facts_c104f_rotor.json.

Predicted (gate R3, tools/bench/diag_c104f_leg.py): at the L2 point the rotor's instr.lib\Autonics Motor\Configure.vi 'error out' (status, code, source) can be read by COM GetControlValue.
Observed: GetControlValue('error out') -> LabVIEW 5005 "parameter not found in the VI's connector pane" (diag_c104f_leg.log:175). The capture tools/bench/m8_shots/20260927_050724_c104f_run1_L2.png shows Configure.vi's diagram: VISA resource name -> VISA Configure Serial Port (VISA Defaults, F) -> VISA Write 'PRG X00' -> VISA resource name out; no error cluster terminal on the panel.

Other measured reads in the same leg (one leg of claudeDev\D1_s1_copy.vi, md5 3e3d23ce, the file that ran 4 legs normally on 2026-09-26 14:18 in card 96-1):
- Run(False) RETURNED after 4.0 s, err=None (log:173); main ExecState 2 at t=2 s, 1 (idle) at t=5 s (log:172,178).
- Window list at L2: Configure.vi Block Diagram, Configure.vi Front Panel, main Front Panel (edit mode), LabVIEW; dialogs(): "VERDICT: clear (no modal dialog)" (log:179-180).
- Configure.vi ExecState 1; its 'VISA resource name' control and 'VISA resource name out' indicator both read ["", 0] (empty) (log:175).
- In S1 the Configure.vi call #30064 'VISA resource name' is wired from VISAResourceNameConstant #30488 (docs/wiki/subvi/D1_s1_copy.json:87622-87632); its error terminals are unwired (only two terminals listed for owner 30064, :41604-41622). The constant's value has never been read offline.
- NI-VISA alias file: 'Rotor' = ASRL5::INSTR = COM5 9600 (C:\ProgramData\National Instruments\NIvisa\visaconf.ini:13,40-44).
- COM5 exclusive open/close probe (no bytes): FREE before LabVIEW, FREE after the VI opened but before Run, FREE after LabVIEW exited (log:4,166,609). No foreign process with a serial/VISA command line at T0 (facts json procs_T0: cycle_runner, bgrun, this script only).
- Cycle 104's motor session start (motor_gate.py --session start) names no port and only touches PI and ASI (motor_gate.py:374 session_start(limits, pi_call, asi_call)).

Claim to attack: the empty VISA resource name read on Configure.vi's panel is the value S1 passed in at this run (constant #30488 evaluates to an empty resource on this machine today), so VISA Configure Serial Port errors inside Configure.vi, Configure.vi's automatic error handling opens its diagram and the run ends after 4 s.
Already ruled out: Configure.vi on disk unchanged since 2026-08-21 (diag_c104_rotorport.log:3); COM5 present, PnP OK, and not held by another process at T0/T1/T2; S1 md5 unchanged.
Question: what is the strongest alternative explanation of an EMPTY resource on Configure.vi's panel after the run (e.g. a panel that shows defaults, not the last call's value), and which ONE cheap read (COM reads, file reads, screenshots; no VI edit or save, no bytes to COM5) separates the claim from it?
