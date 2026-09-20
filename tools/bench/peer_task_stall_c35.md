# ATTACK this explanation of a STALL record

## The record that fired the gate

`tools/bench/stall_pid11536_193335.log` (this file is the subject of the review; name it in your answer):

```
STALL: 2026-09-18 19:36:21 pid 11536 alive 166s, log stale, CPU +0.00s in the last 75s
dialog: unknown
cmd pid 11536: C:\...\python.exe -c "import time,os,re;p='tools/bench/cycle_runner.log';...
import time,re
p='tools/bench/cycle_runner.log'
n=len(open(p,encoding='utf-8',errors='replace').read())
while not re.search(r'RUNNER STOP', open(p,encoding='utf-8',errors='replace').read()[n:]): time.sleep(20)
print('RUNNER EXITED')"
```

`tools/lv_stallcheck.ps1` writes such a record when a watched process shows a stale log and no CPU
progress; `tools/hooks/guard_peer.py` then blocks every `py tools/{recipes,bench}/*.py` run until an
ANSWERED adversarial review newer than that record names it.

## THE CLAIM YOU ARE ASKED TO REFUTE

**Claim C:** this STALL record is a *detector artefact*, not evidence of a hung process. pid 11536 is a
deliberate polling waiter: an inline `python -c` loop whose entire body is
`while not re.search('RUNNER STOP', <read cycle_runner.log>): time.sleep(20)`. It was started by the
previous session to hold its turn open until `tools/cycle_runner.py` printed `RUNNER STOP`
(STATUS.md OPEN 54: "dispatch in the FOREGROUND and wait ... hold the turn open until it lands").
By construction it (a) writes no log of its own, so "log stale" is guaranteed from its first second,
(b) burns no CPU, so "CPU +0.00s in the last 75 s" is its correct steady state, and (c) opens no
LabVIEW / VI Server / COM reference at all, so it cannot be holding a LabVIEW handle or a dialog.
Therefore the safe action is to treat the record as discharged and proceed with unrelated
parser/self-test and read-only COM measurement work, without killing or restarting anything.

Attack it. In particular:
1. The strongest reason Claim C is WRONG.
2. An alternative explanation of the same three observations (alive 166 s / log stale / CPU +0.00 s)
   that does NOT require the process to be a benign waiter — including any way the observations could
   be produced by something that genuinely is stuck, or by a *different* process than the one the
   `cmd pid` line names (PID reuse, a wrapper shell, the watcher reading the wrong handle).
3. What observation would FALSIFY Claim C — something checkable now, on Windows 10, without a rig.
4. The cheapest discriminating test between "benign poller" and "genuinely stuck", given that the
   process may already have exited by the time anyone looks.
5. Whether proceeding under Claim C can cause harm that the STALL gate exists to prevent. The rig is
   **assembled** (motors/ASI reachable only through a gate, camera idle); the work this unblocks is a
   pure-function parser self-test and read-only VI-Server reads of a `claudeDev` copy — no motor, no
   serial, no camera, no run of any VI.

## Already ruled out — do not spend your answer on these

- "It is a pre-experiment sleep inside the LabVIEW driver, so the sleep is real work being waited on":
  that class was reviewed on 2026-09-17 (`archive/peer/2026-09-17-stall-preexperiment-sleep-codex.md`
  and `-opus.md`, both ANSWERED, both REFUSING the "false positive" framing) for a sleep *inside* a
  process that held LabVIEW references. This process is not a LabVIEW client and holds none — say so
  if you think that distinction does not survive contact with how `lv_stallcheck.ps1` actually picks
  its targets.
- "Just set PEER_GUARD_OFF=1": forbidden by this project's rules; not an option under consideration.
- "Kill LabVIEW and restart": standing permission exists, but no LabVIEW instance is running
  (`tasklist | grep -i labview` returned nothing at the start of this session).
