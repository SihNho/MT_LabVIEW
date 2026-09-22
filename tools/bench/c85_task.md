ATTACK the explanation below. It is a claim formed under pressure after a FAILED PREDICTION, and your job
is to refute it, not to agree with it.

THE FAILED PREDICTION (the log: `tools/bench/build_d1_m3a3b_d3.log`, recipe
`tools/recipes/build_d1_m3a3b_d3.py`, run 2026-09-22 14:0x, `BGRUN END rc=1 after 249s`, 35 gates pass /
12 fail). The FIRST failing gate, and the only machinery one, is:

    **FAIL**  G2 20 consecutive calls leave the handle count flat +-100 (a REGRESSION CHECK against the
    S0 baseline docs/toolkit-capabilities.md:460-478, not a hygiene proof)
    before 42471 -> after 42585, delta +114 ; private-bytes drift 3.3 MB

PREDICTION: a newly built op VI, `claudeDev\OpFsInnerTunnelConnect_v1.vi` (md5
5b4e5f0fb3baae96361c33ce81bcd7b1, 18,797 B, ExecState 1), called 20 times in a row against a scratch copy
of a 307 KB VI, would leave the Windows kernel handle count of LabVIEW.exe within +-100 of where it
started. That is the project's standing acceptance criterion for a new op (CLAUDE.md "Reference hygiene",
20 runs flat +-100). Its DONOR `OpFsInnerTunnelConnect_v0.vi` passed the identical test 5 days-of-work
earlier at **+94** (`tools/bench/build_opfsinnertunnelconnect_v0.log`, gate G2 PASS, private-bytes drift
0.03 MB).

OBSERVED: **+114**, i.e. 5.7 handles per call, and a private-bytes drift of **3.3 MB** where v0's was
0.03 MB - a 100x difference in the memory companion on an op that differs from v0 ONLY by which of two
existing wires feeds which of two existing Invoke terminals (the "roles exchanged" swap) plus one new
front-panel Boolean control for `Auto Route?`.

THE EXPLANATION THIS SESSION FORMED, WHICH YOU MUST ATTACK:
"v1 leaks a handful of VI Server references per call because its internal chain (`UID to GObject
Reference.vi` -> To More Specific Class -> `FlatSequenceInnerTunnel.Left Terminal` 1C3A9000 ->
`Terminal.Connect Wire` 6349C03 -> `Terminal.Connected Wire` 634A000 -> `Wire.Is Broken?` 6371004) opens
references it never closes, and the measured 1.00 stray `Invoke` node minted per call adds a persistent
object to the target VI; +114 over 20 calls is therefore a real per-call leak in the op, and the op needs
a `Close Reference` repair before it is used."

ALSO ON FILE, and relevant:
* `docs/toolkit-capabilities.md:462` - "`OpReport_v3.vi`, `OpReportAll_v0.vi` and `OpWireSource_v5.vi`
  carry a traverse and **no `Close Reference`**".
* `docs/toolkit-capabilities.md:484-485` - "the kernel handle count is BLIND to VI Server refnums".
* `docs/toolkit-capabilities.md:460-478` - the S0 baseline the +-100 tolerance comes from.
* CLAUDE.md - "this LabVIEW 2026 install holds ~31,500 handles one minute after a fresh start; the first
  '32,480 = leak' diagnosis was WRONG; judge growth relative to that baseline, never the absolute number."
  In this run the 20 calls started at 42,471 - i.e. ~11,000 handles ABOVE the fresh baseline, after an
  op build that had already opened panels, run Remove Bad Wires and saved.
* The same run's phase [1] restarted LabVIEW: 33,950 -> 33,994 handles; after all the work 42,763; at
  exit, after a second restart, 33,998.
* v1 was called 20 times with `Auto Route?` TRUE on a scratch copy of the bed; the SAME 20 calls produced
  a perfect uid echo on both sides (term_uid 7488, uid_back 7468 on 20/20) - i.e. every call did the
  same work.
* The 12 failing gates of that run are otherwise all the GATE S measurement outcome (the method MERGES
  nets instead of replacing), not machinery.

WHAT I NEED FROM YOU, in this order:
1. The strongest reason the explanation above is WRONG.
2. At least one ALTERNATIVE explanation for +114 / 3.3 MB that does not require a leak in v1 - and say
   what in the file record supports it. Consider in particular: whether a +-100 tolerance is even a
   meaningful discriminator at a 42,471 starting point; whether the handle counter can attribute
   anything to an op at all given the "blind to VI Server refnums" line; whether the 20 calls in v1's
   test differ from v0's 20 calls in a way OTHER than the op (v0's arm ran on a scratch with wire 7506
   ALIVE and was a BRANCH; v1's 20 calls also ran wire-alive, but v1 additionally carries the
   `Auto Route?` control and a front-panel Boolean write per call).
3. WHAT WOULD FALSIFY the leak claim.
4. The CHEAPEST DISCRIMINATING TEST, runnable with tools this project already has (no new op, no new
   device), that separates "v1 leaks" from your alternative - state it as concrete steps with the
   numbers that decide.
5. Whether this failure should block the NEXT dispatch at all, given that the next dispatch's task is a
   READ-ONLY measurement (delete one wire on a scratch copy and ask whether a tunnel uid still resolves)
   followed by at most TWO calls of the same op - i.e. a workload 10x smaller than the one that produced
   +114. Say plainly if you think the gate is being applied at the wrong granularity.

ALREADY RULED OUT (do not spend your answer on these):
* Not the op's correctness: v1 reached ExecState 1 both at the save and re-read after it, and its two uid
  echoes held on 20/20 calls.
* Not a hung or killed client: refs 29 opened / 29 closed / 0 live at exit, and the run ended rc=1 from
  its own gate arithmetic, not from a timeout.
* Not the stray `Invoke` nodes being left behind: they were purged in-run (Node 635 -> 655 -> 635) and
  the scratch was deleted.
