# ATTACK this claim — a static gate failed, the offending leg was then DELETED, and I am about to proceed

## The claim you must try to REFUTE

> "`tools/bench/c63_astcheck.log:15` (`=== ASTCHECK FAILED; failing: 3 allow_broken=True is never passed`,
> `FAIL  3 allow_broken=True is never passed  1 site(s)`) is now MOOT, not merely authorised. The single
> offending site was `g.save(T2_FILE, allow_broken=True)` inside `tools/bench/diag_c63_connect_perturb.py`,
> and that whole T2 save/reopen leg has been DELETED. Its replacement
> `tools/bench/diag_c64_perturb_t1t3.py` writes no VI file at all, so `tools/bench/c60c_astcheck.py` will
> return ASTCHECK OK on every gate, and the remaining T1 + T3 legs still measure something that moves the
> open question."

The open question (Pre-decided 53(d⁷) of `docs/cycle27-plan.md`): cycle 62 measured that
`OpConnectNested_v1.vi` drives `ExecState` **1 → 0** on an UNCHANGED VI after a ZERO-CHANGE idempotent
connect (`tools/bench/diag_c62_negctrl.log:24-31`: `wire_delta` 0, `Wire` census 1905 → 1905, op error
column `''`, the op's own embedded readback `{'UID': 10407, 'UID 2': 10799, 'Is Broken?': False}`). Two
explanations are open: the op PERTURBS THE READING, or it GENUINELY BREAKS the VI. `docs/NAMES.md:912-929`
records the same signature from cycle 23 and says the mechanism is OPEN.

Context, in full, so you can attack the premise and not only the conclusion:

- `tools/bench/c60c_astcheck.py` is a STATIC gate (AST only, no LabVIEW). Gate 3 refuses any script passing
  `allow_broken=True`; gate 2 refuses `gui_save` being imported or called. On the c63 file gate 2 PASSED and
  gate 3 FAILED with exactly 1 site; every other gate passed. The c63 diagnostic then NEVER RAN — the cycle
  runner's own bgrun deadline killed the process tree at 11:56 — so nothing was measured, nothing was saved,
  and no LabVIEW object was touched.
- `tools/bench/diag_c64_perturb_t1t3.py` is that file with T2 deleted and two legs added. What it now does,
  on ONE scratch duplicate of `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d91f16b034707e4d1285ca8cb`,
  pinned FATAL, never written), deleted in the same run:
  cold `ExecState` → ONE idempotent `connect_nested_v1(46,24,0,46,25,0)` → a timestamped `ExecState`
  timeline: (i) eight bare re-reads ~2 s apart; (ii) a read after each of `count('Node')`,
  `node_terms(#10407)`, `count('Wire')`, the 116-row `panel_wiring`, `count('Local')`,
  `count('ControlTerminal')`; (iii) one benign edit (`create_control` on an unwired SINK terminal on
  `Diagram #639`) and its deletion by uid; **(iv) release the VI Server reference and acquire a NEW one to the
  same in-memory VI, then drop the Application proxy (`gscript.reset()`) and read again — LabVIEW is NOT
  restarted**; **(v) with the perturbed scratch still open, open a SECOND independent duplicate of the same
  bed in the SAME LabVIEW session and read its cold `ExecState`**. T3 is a pure file census of which op VIs
  carry an internal `Wire.Is Broken?` / `6371004` readback.
- A fact I measured before writing it, which may undercut leg (iv): `gscript.exec_state`
  (`tools/gscript.py:1977-1979`) is `with vi_ref(target) as r: return int(r.ExecState)` — it ALREADY opens a
  short-lived VI reference per call and releases it (`vi_ref`, `tools/gscript.py:243-259`). So every
  `ExecState` reading in the whole run is already taken through a fresh VI reference, and leg (iv) adds only
  the dropping of the cached Application proxy.
- The run is bounded by `py tools/bgrun.py --material --max-min 25`, which kills the process tree at the
  deadline. Four md5 pins (project ORIGINAL `2a78e17c449cacdaf5da389818526859`, `D1_s1_copy`, `D1_s2_loops`,
  `D1_s3a_focus_ind`) are checked before AND after; the op under test is checked byte-unchanged.

## Already ruled out (do not spend your answer on these)

1. "Edit the gate / rename the argument / hide the call from the AST / set `CYCLE_GUARD_OFF`" — forbidden by
   the brief and by CLAUDE.md; not on the table.
2. "Reinstate the save leg" — dropping it was this cycle's judgement decision, taken above my level. I may
   report that it was needed; I may not put it back.
3. "Do not measure at all" — two cycles have already been spent building on an `ExecState` reading nobody can
   interpret.

## What I want from you

1. The STRONGEST reason the claim is WRONG. In particular: with the save/cold-reopen leg gone, is there ANY
   observation in T1 (i)–(v) that can actually discriminate "perturbs the reading" from "really breaks the
   VI" — or is the whole remaining run incapable of separating them, whatever it returns? If it is incapable,
   say so plainly and say what the run IS evidence about.
2. Attack legs (iv) and (v) specifically. Given that `exec_state` already uses a fresh per-call reference,
   what could a new reference or a new COM Dispatch plausibly change, and what would each possible outcome
   (same value / different value) actually license? For (v): can a second in-memory copy of the same bed in
   the same LabVIEW session be contaminated by the first — shared subVI/typedef instances, one compile cache,
   name collisions between two VIs with different file names but the same internals — so that a 0 (or a 1) on
   the second bed means something other than what it appears to?
3. A THIRD explanation of the cycle-62 reading beyond "perturbs the reading" and "really breaks the VI" that
   this design would NOT distinguish.
4. What would FALSIFY the claim, and the CHEAPEST discriminating test that needs NO save of any VI, NO new op,
   and NO edit to `tools/gscript.py` — something I could add to this same diagnostic.

Answer against the files in this project directory; you may read them. Do not ask me to confirm anything.
