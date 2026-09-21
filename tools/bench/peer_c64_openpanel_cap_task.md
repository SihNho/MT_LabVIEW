# ATTACK this: a failed prediction — `open_panel` on a plain FILE COPY did not return within the 180 s cap

## The failed prediction, verbatim in its consequences

We predicted that `g.open_panel(<path>)` on `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\OpConnectNested_v2.vi`
would return in a few tens of seconds, as the identical call had just done in an earlier run of the same
script. It did not. The measured facts, all from `tools/bench/diag_c64_connect_v2.log` (run 2,
`BGRUN END rc=1 after 329s`, 2026-09-21 12:57):

* `OpConnectNested_v2.vi` at that moment was **a plain byte-for-byte file copy** of
  `OpConnectNested_v1.vi` (md5 `b7a1bb56…`, 14,666 B). **No edit of any kind had been made to it**, and it
  had never been opened or saved by LabVIEW under its new name.
* `g.open_panel()` on it — which calls `VirtualInstrument.OpenFrontPanel(False, 1)` over COM through
  `tools/gscript.py` `_invoke`, whose watchdog cap is **180 s** — **did not return within the cap**. The
  module was therefore POISONED (`gscript._set_poison`): the worker thread was abandoned alive and every
  later COM call raises `COMPoisoned` rather than queueing behind it.
* The abandoned call **did come back, ~66 s later** — roughly **246 s in total** for one `OpenFrontPanel`.
  `gscript._check_poison` then cleared the poison on its own (`thread.is_alive()` False).
* In **run 1** of the same script, ~19 minutes earlier, the **same call on the same file** returned in
  **~60 s**.
* A **LabVIEW restart had just completed** before run 2's batch (`Z_R1`, kernel handle count 30,839 →
  30,687). `tools/lv_restart.py` waits a fixed settling period after the process answers COM.
* Machine: Windows 10, LabVIEW 2026 (26.3.1f1), single COM client, nothing else driving LabVIEW. The op's
  hierarchy includes `vi.lib` members (e.g. `Clear Errors.vi`, `UID to GObject Reference.vi`) and
  erdosmiller scripting VIs.

## The two explanations on the table — NEITHER is established, and both may be wrong

1. **First-load cost.** Opening the panel of this op forces a full load of its subVI hierarchy
   (`vi.lib` + erdosmiller). On this machine that cost sits near the 180 s cap, so the same call lands
   either side of the cap depending on what is already resident.
2. **Restart settling.** LabVIEW answers COM before it has finished its own start-up work, so a panel
   open issued immediately after a restart contends with it; run 1 was issued into an already-warm
   instance.

## What I am about to do, and why your answer matters

The next diagnostic is forbidden from calling `open_panel` at all. But its edit legs go through
`gscript.connect_terminals` / `connect_nested_v1`, and **those wrappers call `ensure_loaded()`, which
calls `open_panel()` internally** (`tools/gscript.py:1268-1337`) — because a scripting EDIT on a target
loaded only through `GetVIReference` is silently declined. Read-only census calls do not need it. So the
plan is: run every file-only and read-only leg first (which incidentally loads much of the op hierarchy),
and only then let the edit legs trigger the internal `open_panel` on scratch copies of a SMALL op VI.

## Attack all of it

1. Give me the **strongest reason the framing above is wrong** — including the possibility that neither
   explanation is right (e.g. the cap measured something that is not "loading" at all: recompile of a copy
   whose compiled code cache does not match its new path, a modal dialog behind the call, cross-apartment
   marshalling, the file being a copy under a name LabVIEW has never seen, a `Run When Opened` flag, the
   `activate=False` path, or the 66-s tail being the call finishing vs. being cancelled).
2. Is "run the read-only legs first to warm the hierarchy" a **real mitigation or a superstition**? Say
   what it would and would not change, and what it could make WORSE.
3. What is the **cheapest discriminating test** between your candidates — one that costs a single batch,
   touches no original file, saves no VI, and does not itself risk a 4-minute stall?
4. What would **falsify** each explanation?
5. Is there a way to reach the "edits actually land" state **without** `OpenFrontPanel` that this project
   has not measured? Our own file records that reading `VI.Block Diagram` (23C) was NOT enough
   (`tools/gscript.py:1273-1295`), and that the experiment which showed that was itself attacked as
   unsound (the diagram ref was not held live at mutation time). Search outside our files before answering.

## Already ruled out — do not spend your answer here

* Not a hung/wedged LabVIEW: the call returned on its own, and the instance served every later call.
* Not our own foreground timeout being too short in the sense of "just raise it": the cap exists because a
  blocking COM call in a single-threaded apartment silently queues every later call behind it.
* Not a second COM client or a human at the keyboard: the run is unattended, one client, rig disassembled
  from LabVIEW's point of view (no instrument is touched).
