r"""S1 OF THE Pre-decided 22 STAGE CHAIN — the fixture TIFF writer is cut from a copy of the original and the
copy is SAVED, with the save route itself armed and controlled first.

  MATERIAL=1 py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_s1_cd.log \
      -- py -u tools/recipes/stage_d1_s1.py --phases CD

PHASES ARE SELECTABLE (`--phases`, default ABCD) — AND A AND B ARE DONE, 2026-09-19
------------------------------------------------------------------------------------
Phases A and B RAN on 2026-09-19 (`tools/bench/stage_d1_s1.log`, `BGRUN END rc=1 after 351s`, 13 PASS / 1 FAIL,
the FAIL being gate B by design). Phase A's artefact is on disk and is NOT re-made: `claudeDev\D1_s1arm_savetest.vi`,
md5 `e0112963cc1b9e3be29d2bb053ba9029`, 475,141 B, version bytes `26 00 80 00`. **Phase C starts from a FRESH
`shutil.copy2` of the ORIGINAL and depends on neither A nor B**, so `--phases CD` is a complete, self-contained
run of the stage proper; the selector exists so a phase that has already produced its artefact is not paid for
twice (CLAUDE.md, user 2026-09-19: "a step is not done until it has left a file", and a step that HAS left its
file is not re-run).

🔴 WHY GATE B's ACCEPTANCE REFERENCE CHANGED — `docs/cycle27-plan.md` Pre-decided 29(g), judgement, cycle 46
-------------------------------------------------------------------------------------------------------------
Gate B as first written compared the saved artefact against a PRISTINE BYTE COPY of the original. **The byte copy
is the DEFECTIVE side.** `tools/bench/s1_subvi_paths.log` (T1, 15 PASS / 0 FAIL, three COLD conditions each in its
own child process and its own fresh LabVIEW instance; artefact `tools/bench/s1_subvi_paths.json`) measured the full
98-row SubVI table on all three and found:
  * the COM-SAVED copy matches the **ORIGINAL** on **all 98 rows, name AND path**, with **zero** rows pointing into
    `claudeDev\background VIs_COPY\`;
  * the PRISTINE BYTE COPY re-binds **22** calls into `claudeDev\background VIs_COPY\`, loses **8** outright and
    reads 7 rows empty (uid 0, name `''`, path `''`).
So `shutil.copy2(ORIGINAL, claudeDev\…)` produces a SILENTLY RE-BOUND VI, and that — not the save — is why a byte
copy reads `ExecState 0` COLD. **The acceptance reference for every stage gate is therefore the ORIGINAL's own
SubVI table, taken COLD in its own child process; a byte copy is retained as a LOGGED CONTROL only, never as the
pass/fail reference.** Applied here in two places: gate B is RE-SPECIFIED (it is not run by `--phases CD`, but it
must not stay wrong for replay), and phase D gains the new FATAL gate **D5**, which compares the SAVED stage
artefact's cold SubVI table against the ORIGINAL's cold SubVI table directly.

WHY THIS FILE EXISTS, AND WHY IT HAS FOUR PHASES INSTEAD OF ONE
---------------------------------------------------------------
`tools/gscript.py:2056-2071` reaches the COM `SaveInstrument` (`:2070`) only when `exec_state(target) != 0`
(`:2065`); at `ExecState 0` it either diverts to `gui_save` (`allow_broken=True`) or raises. `docs/cycle27-plan.md`
Pre-decided 14a MEASURED that a byte-identical copy of the original reads **ExecState 0 COLD** and **ExecState 1
with the ORIGINAL PRELOADED read-only** (`tools/bench/diag_d1_execstate_preload.log:13`, `:33`, on this very
original, md5 `2a78e17c449cacdaf5da389818526859`). Therefore a stage artefact of this chain can only ever be saved
in an instance where the ORIGINAL IS PRELOADED — there is no other route to a non-diverted `SaveInstrument`.

Pre-decided 16(b) forbade a preload in a step that SAVES, naming two hazards:
  * **MASKING** — a preload can supply subVIs the saved file would not resolve on its own, so a preloaded `1` is
    necessary, never sufficient. ANSWERED HERE by phase D: the saved artefact is re-read COLD **and** PRELOADED in
    a fresh instance, both labelled, and by phase B, which re-reads the saved arm file beside a pristine control.
  * **CROSS-LINKING** — the working copy could link to the in-memory ORIGINAL's subVIs and `g.save()` would write
    that. **NEVER MEASURED.** Phases A and B are that measurement, and nothing else: A saves a copy on which NO
    diagram edit whatsoever was made, B re-reads it beside a byte-copy control that was never opened with the
    original resident. If cross-linking writes something into the file, the arm's bytes move (A5) or the arm's
    (cold, preloaded) `ExecState` pair differs from the control's (gate B).

PRIOR ART — checked before a line was written; everything below is REUSED, nothing is invented
----------------------------------------------------------------------------------------------
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`:
  * **Structure, logging idiom, `gate`/`fact`/`md5` helpers, the `lv_restart.py` fresh-instance pattern, the
    `g.ref_counts()` phase ledger and the prediction-contract header are MODELLED ON and copied from
    `tools/recipes/build_d1_routeb_v7.py`** (`gate` `:518`, `fact` `:526`, `md5` `:531`, the restart at `:2622`,
    the `refs(phase)` ledger at `:2725`, the `finally` md5 re-assert at `:2801`).
  * **The whole C body already exists, measured**: v7 `s1()` `:697-725` (copy → panel → BEFORE census) and
    `s1t()` `:728-751` (the two TIFF deletes with their present-before/gone-after gates, the single
    `remove_bad_wires_scripted`, the count gate, the bare-named-sink gate). It is RE-CUT as a stage script here,
    not re-derived.
  * **The preload is `tools/bench/p2_open_copy.py:22-28` verbatim** (pythoncom + `GetVIReference(path,"",False,0)`,
    no panel on the original, nothing saved), the same pattern v7's `preload_reread()` `:2666-2692` uses.
  * **Phase B does not read anything itself: it CALLS the BUILT helper `tools/bench/diag_d1_execstate_preload.py`,
    once per condition** (`run_condition()` `:155-179` spawning `child()` `:88-151`). That helper already owns the
    child-process-per-condition shape and its reason — "a `Find the VI named …` modal makes GetVIReference block
    with no dialog visible to the caller … the PROCESS-level deadline is the guarantee" (`:26-28`) — its own
    `lv_restart` per child (`:96-97`), its handle accounting and its per-condition JSON. It is IMPORTED, not
    re-implemented (prior-art precedent B2: extend, never author), and its `ORIG`/`ROUTEB_PINNED_MD5` are GATED
    against this file's own (B0a/B0b) rather than assumed to be the same original.
  * **Gate B's re-specification and gate D5 do not read a SubVI table themselves either: they CALL the BUILT
    `tools/bench/s1_subvi_paths.py`** — `run_condition()` (`:183-209`) spawning `child()` (`:110-179`), which does
    its own `lv_restart` (`:123-124`), its own handle accounting, its own per-condition JSON
    (`tools/bench/s1_paths_<tag>.json`) and its own `g.reset()`/`ref_counts` ledger, and enumerates
    `g.report_all(target,"Diagram")` + `g.subvis(target, i, strict=False)` per diagram. That file IS the
    mechanism T1 measured with; it is EXTENDED BY REUSE, never re-authored (prior-art precedent B2), and its
    own `GATE PASS G3 …` lines in this log are ITS counters, not this file's. ONE CONDITION PER CHILD, NO
    PRELOAD in any of them — a second copy of the main VI in one instance would load the very hierarchy the
    next read must resolve on its own (`tools/bench/diag_d1_execstate_preload.py:26-28`).
  * `build_d1_v0`: `TIFF_DELETE` (`:474` — `#22700 SubVI 'IMAQ Write TIFF File 2'`, `#23020 Function 'Build
    Path'`), `bare_named_sinks` (`:482`), `diag_index`, `terms_of`. `bench_prep.labview_handles`.
  * **NO NEW OP VI, NO NEW TOOL, NO NEW DEVICE** is created here (user's standing order, 2026-09-18 08:53).

WHAT IS DELIBERATELY *NOT* IN THIS STAGE
-----------------------------------------
v7's `s1d()` deletes three further subVIs — `#5058 GPU_kernel_v1.vi`, `#48 ASI_adjust focus-subvi.vi`,
`#376 save trace.vi` — which S2 re-drops FRESH. **They are NOT deleted here, by judgement's decision**: deleting a
node whose outputs are consumed leaves the consumers' required inputs BARE, and a VI with bare required inputs is
broken and therefore UNSAVEABLE over COM (`gscript.py:2065-2068`). They move into the stage that re-drops them, so
every stage of this chain ends with a file that can actually be written. v7's own measurement is the evidence:
`s1d()` `:780-782` reports the bared sinks it creates (`#6384`'s error chain via w541, `#12589` t1 via w9113).

PHASE C's CENSUS GATES ARE A DELIBERATE REPLICATION, NOT A DISCOVERY — AND WHAT THAT RUN'S `0` MEANT
-------------------------------------------------------------------------------------------------------
Gates C3/C4/C6/C7 re-measure numbers this project already has: `tools/bench/build_d1_v0_run6.log:19-26` ran this
exact deletion on 2026-09-17 and passed it — `:19` BEFORE `{'SubVI': 98, 'Function': 181, 'Node': 626,
'Wire': 1902}` with 28 bare named sinks, `:20-21` `#22700` and `#23020` GONE, `:22` newly bare `[]`, `:24` AFTER
`{97, 180, 624, 1899}`, `:25-26` `#23175`/`#22703` LEFT STANDING. So a FAIL on C3/C4/C6/C7 means SOMETHING CHANGED
SINCE 2026-09-17, not that anything new was found. They are replicated rather than assumed for one reason: **that
run never produced a saved artefact** — it is an in-memory measurement, and the file it measured is not on disk, so
S1's own copy has to be shown to be the same VI before its save means anything.
The same log's `:23` reads `ExecState unchanged 0 -> 0` ACROSS the deletion. That `0` is **NOT a break**: run 6 took
it COLD, and by Pre-decided 14a a cold reading of a copy of this original measures subVI LINKAGE, not legality
(`tools/bench/diag_d1_execstate_preload.log:13` cold 0 / `:33` preloaded 1 on a BYTE-IDENTICAL copy). It is
therefore the 14a linkage reading, and it is exactly why C8, D1 and D2 in this file read under PRELOAD — and why
`g.save()` can only ever be reached under preload at all (`tools/gscript.py:2065`, `docs/cycle27-plan.md:595-601`).

WHY ONLY TWO OF THE FOUR 2026-09-01 FIXTURE NODES ARE CUT HERE
-----------------------------------------------------------------
The fixture is FOUR nodes, not two: `#22700 IMAQ Write TIFF File 2`, `#22703 Format Into String`,
`#23175 Strip Path`, `#23020 Build Path`, all inside the frame loop, listed with their wiring at
`docs/fixture-recording.md:15-20`. **S1 deletes `#22700` and `#23020` ONLY, and that is decided, not an oversight**
— `docs/cycle27-plan.md` Pre-decided 29(f) (`:623-628`): `#22703`/`#23175` STAY because every pinned count this
chain gates on (SubVI 98→97 · Function 181→180 · Node 626→624 · Wire 1902→1899) is the MEASURED CONTRACT OF THE
TWO-NODE DELETION, and widening the cut would invalidate that contract with no measurement behind it. The two
survivors become dead-but-legal (a source with no sink cannot break a VI — `build_d1_v0_run6.log:25-26`). So this
stage's artefact still carries two of our own 2026-09-01 insertions; removing them is a later stage with its own
contract, recorded as an OPEN item.

HARD CONSTRAINTS THIS FILE HOLDS TO (each is a build failure if violated, not a style note)
--------------------------------------------------------------------------------------------
  * `allow_broken=True` appears NOWHERE. Every save is `g.save(path)` with the default, so the `gui_save` divert
    (`gscript.py:2066-2067`) is impossible BY CONSTRUCTION, not by intention.
  * `gscript.net_map` is BANNED (Pre-decided 17) and is not imported. The ONE `remove_bad_wires_scripted` call is
    C5, a PRE-PASS reaper outside any row loop — the shape Pre-decided 17 explicitly EXONERATES (`:204-207`); this
    file has no row loop at all.
  * Every reference opened is closed: `g.*` calls go through `gscript.vi_ref` (counted), the phase preload holds
    exactly one COM proxy and drops it in its own `finally`, and `g.ref_counts()` is printed at the END OF EVERY
    PHASE (CLAUDE.md §3 reference hygiene).
  * **After EVERY phase, md5(ORIGINAL) is re-asserted against the pin** — rule 1, fatal.
  * The saved-version bytes of every artefact are RECORDED (`19 00 80 00` = LV2019, `26 00 80 00` = LV2026,
    CLAUDE.md §1). The offset is not assumed: the first 64 bytes are logged as hex and every `?? 00 80 00` match
    in them is reported with its offset, beside the ORIGINAL's own header read the same way.
  * Only the files this docstring names are deleted (the phase-B control). No scratch VI outside `claudeDev`.
  * **NOTHING BRANCHES ON A RESULT.** Every gate is FATAL and numbered; the first FAIL stops the chain and leaves
    its artefacts on disk for the next session to open. No measured value chooses a code path anywhere.

PREDICTION CONTRACT
--------------------
 A1  the arm copy on disk is byte-identical to the ORIGINAL (md5 `2a78e17c449cacdaf5da389818526859`).
 A3  `exec_state(arm)` with the ORIGINAL preloaded reads **1** (Pre-decided 14a). Logged, NOT gated — phase A's
     gate is the save, and a different reading here is a fact this chain must report rather than hide.
 A4  `g.save(arm)` returns without raising. If it raises, the route Pre-decided 22 depends on does not exist.
 A5  the arm file's md5/size AFTER the save. **No prediction is offered**: a save of an unedited VI may legally
     rewrite the file (LabVIEW rewrites its compiled-code and modification records), so both outcomes are
     measurements. What it feeds is gate B.
 B   **FOUR READINGS, FOUR CHILD PROCESSES, FOUR FRESH LabVIEW INSTANCES** — B-i arm COLD · B-ii control COLD ·
     B-iii arm PRELOADED · B-iv control PRELOADED, in that order, each spawned through
     `diag_d1_execstate_preload.run_condition()` and each labelled with its condition AND the LabVIEW pid it read
     in. ONE CONDITION PER INSTANCE is the whole point: two copies of this main VI read in one instance
     contaminate each other, because reading the first loads the very subVI hierarchy the second would otherwise
     have had to resolve, and a cold label on the second reading would then be false (`docs/cycle27-plan.md`
     Pre-decided 29(c), `tools/bench/diag_d1_execstate_preload.py:26-28`, `:96-97`). Nothing else is opened in any
     child.
     🔴 **RE-SPECIFIED on measurement, `docs/cycle27-plan.md` Pre-decided 29(g) — see the red section at the top
     of this file.** The four `ExecState` readings are now RECORDED FACTS; the byte-copy control is a LOGGED
     CONTROL, never the pass/fail reference, because T1 measured the byte copy to be the DEFECTIVE side (22 rows
     re-bound into `claudeDev\background VIs_COPY\`, 8 lost, 7 empty — `tools/bench/s1_subvi_paths.log`).
     **Gate `B6` is the acceptance gate: the saved arm's COLD SubVI table — taken in its own child process and
     its own fresh LabVIEW instance via `tools/bench/s1_subvi_paths.run_condition()` — must equal the ORIGINAL's
     COLD SubVI table key-for-key in BOTH name and path (98 rows on each side), with zero rows into
     `claudeDev\background VIs_COPY\` and no empty name or path.** Superseded, kept so the change is legible:
     "the saved arm's (COLD, PRELOADED) pair must be IDENTICAL to the pristine control's pair — predicted (0, 1)
     for both" — that test compared the artefact against the defective side and could only ever fail.
 C1  the S1 working copy is byte-identical to the ORIGINAL.
 C3  BEFORE census = Diagram 170 · Node 626 · Wire 1902 · LoopTunnel 132 · ControlTerminal 114 · WhileLoop 3 ·
     Local 8 · SubVI 98 · Function 181 (v7 `:427-428`).
 C4  `#22700` then `#23020` are present before deletion and gone after (v7 `s1t` `:736`, `:743`).
 C6  SubVI 97 · Function 180 · Node 624 · Wire 1899 (v7 `:745-746`).
 C7  no STAYING node on the frame body is left with a bare named input (v7 `:749`).
 C8  `exec_state(target)` with the ORIGINAL preloaded — logged, not gated (the deletions are predicted harmless,
     but C9 is the test that matters and a cold/preloaded confound must not be gated on twice).
 C9  `g.save(target)` returns without raising ⇒ **`claudeDev\D1_s1_copy.vi` EXISTS ON DISK** with its md5, size
     and version bytes in this log. That file IS the stage artefact (CLAUDE.md §3: a step is not done until it
     has left a file).
 D1  the saved artefact read COLD in a FRESH instance — predicted 0, logged UNREAD as a verdict (14a). RECORDED,
     not gated, and printed beside D2's PRELOADED reading with both explicitly labelled (29(g)'s rider).
 D2  the same artefact read with the ORIGINAL preloaded = **1**. FATAL. This is the stage's pass criterion
     (Pre-decided 22's S1 row: "md5 recorded; ExecState 1 preloaded; node count = original − deletions").
 D5  🆕 **THE ARTEFACT'S SubVI TABLE AGAINST THE ORIGINAL'S, BOTH COLD, ONE CONDITION PER CHILD PROCESS AND PER
     LabVIEW INSTANCE** (Pre-decided 29(g); mechanism reused from `tools/bench/s1_subvi_paths.py`). FATAL, and it
     asserts all three of:
       (a) the S1 table is EXACTLY the ORIGINAL's table MINUS the single key `(diagram 639, node 22700)` — 97
           rows vs 98 — every surviving row identical key-for-key in BOTH name and path. (`#23020 Build Path` is
           a Function, not a SubVI, so it never appears in this table; `#22700 IMAQ Write TIFF File 2` is the one
           SubVI the stage deletes, on the frame body `#639`.)
       (b) ZERO rows of the S1 table point into `claudeDev\background VIs_COPY\` (the byte copy had 22).
       (c) no row has an empty name or an empty path (the byte copy had 7).
     The FULL diff — missing, extra, changed, and any key that should have gone and did not — is logged when it
     fails. Sub-results are reported individually (non-fatal) and the combined verdict is the fatal gate, so a
     failure names all three values rather than only the first.
 D4  md5(ORIGINAL) still equals the pin.
A clean `--phases ABCD` run reads **31 PASS / 0 FAIL**; a clean `--phases CD` run reads **20 PASS / 0 FAIL**
(S0 · C1 · C3 · C4×4 · C6 · C7 · C9 · MD5-C · D2 · D5-i · D5-ii · D5a · D5b · D5c · D5 · MD5-D · S6). The helpers'
own `GATE PASS ... child completed` lines are THEIR counters, not these. Rule 1: the ORIGINAL is only ever COPIED and
opened READ-ONLY, never saved, and its md5 is gated after every phase. Rule 1a: two of the four FIXTURE nodes
inserted by us on 2026-09-01 are removed (see "WHY ONLY TWO" above) and nothing else changes, so the original's
computation is untouched. No VI is run; no motor, ASI or
camera is touched; no GUI action is taken.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402
import build_d1_v0 as D1                                                         # noqa: E402
from build_d1_v0 import bare_named_sinks, diag_index                             # noqa: E402
import s1_subvi_paths as T1                                                     # noqa: E402  (the BUILT census)
import diag_d1_execstate_preload as D1ES                                       # noqa: E402  (the BUILT helper)

# ---------------------------------------------------------------------------- constants, all measured
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"          # v7 `:173`/`:388`
CLAUDEDEV = g.CLAUDEDEV
BENCH = os.path.join(ROOT, "tools", "bench")

ARM = os.path.join(CLAUDEDEV, "D1_s1arm_savetest.vi")    # phase A: the SAVE-ROUTE arm, no diagram edit ever
CTL = os.path.join(CLAUDEDEV, "D1_s1ctl_bytecopy.vi")    # phase B: the pristine linkage control, deleted at B4
TARGET = os.path.join(CLAUDEDEV, "D1_s1_copy.vi")        # phase C: THE STAGE ARTEFACT, kept

OUT_SAVEROUTE = os.path.join(BENCH, "s1_saveroute.json")
OUT_READINGS = os.path.join(BENCH, "s1_stage_readings.json")

FRAME_BODY_UID = 639          # "diagram 43", the frame loop's body (v7 `:422`)
BEFORE = dict(Diagram=170, Node=626, Wire=1902, LoopTunnel=132, ControlTerminal=114, WhileLoop=3, Local=8,
              SubVI=98, Function=181)                                            # v7 `:427-428`
AFTER_S1T = dict(SubVI=97, Function=180, Node=624, Wire=1899)                    # v7 `:745-746`

# --- Pre-decided 29(g): the ACCEPTANCE REFERENCE is the ORIGINAL's SubVI table, never a byte copy.
BG_COPY = os.path.join(CLAUDEDEV, "background VIs_COPY")   # T1's "bait" directory; the byte copy binds 22 rows here
PIN_SUBVI_ROWS = 98                # T1 measured 98 on ARM-cold, CTL-cold and ORIG-cold (tools/bench/s1_subvi_paths.log)
TIFF_SUBVI_KEY = (FRAME_BODY_UID, 22700)   # the ONE SubVI row S1 deletes: #22700 on the frame body #639.
                                           # #23020 'Build Path' is a Function and never appears in a SubVI table.

g._run.__defaults__ = (6.0, 180.0)
passes, fails, facts = [], [], []
READINGS = {"original": {"path": ORIGINAL, "md5_pin": ORIG_MD5}, "A": {}, "B": {}, "C": {}, "D": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    """Every gate in this file is FATAL by default: the first FAIL stops the chain and leaves its artefacts."""
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def labview_pid():
    """The LabVIEW process id, read EXACTLY the way `tools/bench/bench_prep.py:64-70` reads its handle count —
    same PowerShell one-liner, one property further. It only LABELS a reading with the instance it came from
    (phase B); nothing is driven by it, no VI is touched, and no new tool is created."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                           capture_output=True, text=True, timeout=90)
        return int((r.stdout or "").strip() or 0)
    except Exception:                                                             # noqa: BLE001
        return None


def version_bytes(path):
    """CLAUDE.md §1's saved-version audit, WITHOUT assuming an offset: return the first 64 bytes as hex and every
    `?? 00 80 00` run found in them, with its offset. `19 00 80 00` = LV2019, `26 00 80 00` = LV2026."""
    with open(path, "rb") as f:
        head = f.read(64)
    hits = [{"offset": m.start(), "bytes": " ".join("%02x" % b for b in m.group(0))}
            for m in re.finditer(rb"(?s).\x00\x80\x00", head)]
    return {"head64_hex": " ".join("%02x" % b for b in head), "version_candidates": hits}


def file_facts(tag, path):
    """md5 + size + version bytes of one artefact, recorded and logged in one place."""
    rec = {"path": path, "exists": os.path.exists(path)}
    if rec["exists"]:
        rec["md5"] = md5(path)
        rec["size"] = os.path.getsize(path)
        rec.update(version_bytes(path))
        fact(f"{tag}: {os.path.basename(path)} md5 {rec['md5']} size {rec['size']} B; "
             f"version candidates {rec['version_candidates']}")
    else:
        fact(f"{tag}: {os.path.basename(path)} IS NOT ON DISK")
    return rec


def fresh(tag):
    """A FRESH LabVIEW instance (standing restart authority, CLAUDE.md §3), then rebind every cached proxy.
    `gscript.reset()` (`tools/gscript.py:262-269`) is used rather than `_lv = None`: a bare `_lv = None` leaves
    `_cache` pointing at the dead instance and the next call dies with 0x800706BA."""
    g.reset()
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact(f"{tag}: lv_restart rc={rc.returncode}: {(rc.stdout or '').strip().splitlines()[-1:]}")
    except Exception as e:                                                        # noqa: BLE001
        fact(f"{tag}: lv_restart FAILED ({type(e).__name__}: {e}) — every reading in this phase is weaker for it")
    g.reset()
    fact(f"{tag}: LabVIEW handles after the restart: {labview_handles()} (fresh-instance baseline ~31,500)")


class Preload:
    """`tools/bench/p2_open_copy.py:22-28` verbatim: hold the ORIGINAL resident READ-ONLY for the duration of a
    phase, so `ExecState` reads and `SaveInstrument` in that phase are taken under Pre-decided 14a's condition.
    No panel is opened on the original, nothing is run, nothing is saved. The single COM proxy is dropped in
    `__exit__` — the only name that ever holds it (reference hygiene, CLAUDE.md §3)."""

    def __init__(self, tag):
        self.tag = tag
        self.app = None
        self.vi = None

    def __enter__(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        self.app = dynamic.Dispatch("LabVIEW.Application")
        self.vi = self.app.GetVIReference(ORIGINAL, "", False, 0)
        fact(f"{self.tag}: ORIGINAL resident READ-ONLY (LabVIEW {self.app.Version}), its own ExecState "
             f"{int(self.vi.ExecState)}; nothing opened on it, nothing saved")
        return self

    def __exit__(self, *exc):
        self.vi = None
        self.app = None
        fact(f"{self.tag}: preload references released; refs {g.ref_counts()}")
        return False


def dump():
    """Both artefacts are written from the SAME accumulator, and are re-written in `main`'s `finally`, so a fatal
    gate still leaves the readings taken up to that point on disk."""
    with open(OUT_SAVEROUTE, "w", encoding="utf-8") as f:
        json.dump({k: READINGS[k] for k in ("original", "A", "B")}, f, indent=1, default=str)
    with open(OUT_READINGS, "w", encoding="utf-8") as f:
        json.dump(READINGS, f, indent=1, default=str)


def orig_gate(phase):
    """Rule 1, after EVERY phase: the ORIGINAL's md5 still equals the pin. FATAL."""
    m = md5(ORIGINAL)
    READINGS.setdefault("md5_after_phase", {})[phase] = m
    gate(f"MD5-{phase} original md5 unchanged after phase {phase}", m == ORIG_MD5, m)


# ---------------------------------------------------------------------------- Pre-decided 29(g): SubVI tables
def cold_subvi_table(tag, target):
    """ONE COLD SubVI-path census of `target`, in ITS OWN CHILD PROCESS and its OWN fresh LabVIEW instance.

    Nothing is read here: this CALLS the BUILT `tools/bench/s1_subvi_paths.py` `run_condition()` (`:183-209`),
    which spawns that file's `child()` (`:110-179`) — its own `lv_restart`, its own handle accounting, its own
    `g.reset()`/`ref_counts` ledger, its own per-condition JSON `tools/bench/s1_paths_<tag>.json`, and its own
    process-level deadline (`CHILD_TIMEOUT_S`). It is the instrument T1 measured Pre-decided 29(g) with; it is
    EXTENDED BY REUSE, never re-authored. NO PRELOAD in any child, and never two copies of the main VI in one
    instance. `T1.gate`'s own `GATE PASS G3 …` line belongs to T1's counters, not to this file's.
    Returns (keyed table {(diagram_uid, node_uid): (name, path)}, a record of the census)."""
    res = T1.run_condition(tag, target)
    rows = res.get("rows", []) or []
    keyed = {(r["diagram_uid"], r["node_uid"]): (r["name"], r["path"]) for r in rows}
    bg = sorted(k for k, v in keyed.items() if str(v[1]).lower().startswith(BG_COPY.lower()))
    empty = sorted(k for k, v in keyed.items() if not str(v[0]).strip() or not str(v[1]).strip())
    rec = {"tag": tag, "target": target, "status": res.get("status"), "child_rc": res.get("child_rc"),
           "n_rows": len(rows), "n_keys": len(keyed), "n_diagrams": res.get("n_diagrams"),
           "n_diagram_errors": len(res.get("diagram_errors", []) or []),
           "into_background_vis_copy": len(bg), "background_vis_copy_keys": bg[:12],
           "empty_rows": len(empty), "empty_keys": empty[:12],
           "restart_rc": res.get("restart_rc"), "ref_counts": res.get("ref_counts"),
           "handles_after_restart": res.get("handles_after_restart"), "handles_end": res.get("handles_end"),
           "child_json": f"tools/bench/s1_paths_{tag}.json"}
    fact(f"{tag}: COLD SubVI census of {os.path.basename(target)} — status {rec['status']!r} rc {rec['child_rc']!r}; "
         f"{rec['n_rows']} rows / {rec['n_keys']} distinct keys over {rec['n_diagrams']!r} diagrams, "
         f"{rec['n_diagram_errors']} diagram errors; into 'background VIs_COPY' {rec['into_background_vis_copy']}; "
         f"empty name-or-path {rec['empty_rows']}; child refs {rec['ref_counts']!r}; "
         f"handles {rec['handles_after_restart']!r} -> {rec['handles_end']!r}; json {rec['child_json']}")
    return keyed, rec


def compare_subvi_tables(got, reference, expect_missing):
    """`got` must be `reference` MINUS `expect_missing`, key-for-key, in BOTH name and path.

    The ACCEPTANCE REFERENCE IS THE ORIGINAL'S TABLE (Pre-decided 29(g)); a byte copy is never a reference here.
    Returns a dict that is logged in full whenever the comparison fails — missing / extra / changed rows, plus any
    key that was supposed to be deleted and is still present."""
    expected = {k: v for k, v in reference.items() if k not in expect_missing}
    missing = sorted(set(expected) - set(got))
    extra = sorted(set(got) - set(expected))
    changed = sorted(k for k in (set(expected) & set(got)) if got[k] != expected[k])
    not_deleted = sorted(k for k in expect_missing if k in got)
    absent_from_reference = sorted(k for k in expect_missing if k not in reference)
    return {"n_reference": len(reference), "n_expected": len(expected), "n_got": len(got),
            "missing": missing, "extra": extra, "changed": changed, "not_deleted": not_deleted,
            "expected_key_absent_from_reference": absent_from_reference,
            "equal": not (missing or extra or changed or not_deleted or absent_from_reference),
            "changed_detail": [{"key": list(k), "reference": list(expected[k]), "got": list(got[k])}
                               for k in changed],
            "missing_detail": [{"key": list(k), "reference": list(expected[k])} for k in missing],
            "extra_detail": [{"key": list(k), "got": list(got[k])} for k in extra]}


def log_table_diff(label, cmp_):
    """The FULL diff, printed line by line. Called only when a comparison fails — nothing is elided."""
    print(f"  --- {label}: FULL DIFF (reference = the ORIGINAL's COLD SubVI table)", flush=True)
    print(f"      reference rows {cmp_['n_reference']} · expected after the stage deletion {cmp_['n_expected']} · "
          f"got {cmp_['n_got']}", flush=True)
    for k in cmp_["not_deleted"]:
        print(f"      NOT-DELETED   key {k} is still present in the artefact", flush=True)
    for k in cmp_["expected_key_absent_from_reference"]:
        print(f"      BAD-KEY       key {k} does not exist in the ORIGINAL's table at all", flush=True)
    for d in cmp_["missing_detail"]:
        print(f"      MISSING       key {d['key']}  reference name={d['reference'][0]!r} "
              f"path={d['reference'][1]!r}", flush=True)
    for d in cmp_["extra_detail"]:
        print(f"      EXTRA         key {d['key']}  got name={d['got'][0]!r} path={d['got'][1]!r}", flush=True)
    for d in cmp_["changed_detail"]:
        print(f"      CHANGED       key {d['key']}\n"
              f"                      reference name={d['reference'][0]!r} path={d['reference'][1]!r}\n"
              f"                      got       name={d['got'][0]!r} path={d['got'][1]!r}", flush=True)


# ============================================================================== PHASE A — SAVE-ROUTE ARM
def phase_a():
    """NO DIAGRAM EDIT OF ANY KIND. The only question is whether `g.save()` (default `allow_broken`) completes on
    a copy of the original in an instance where the original is preloaded, and whether that save moves bytes."""
    print("\n=== PHASE A: the SAVE-ROUTE ARM — copy, preload, read, save. No edit whatsoever.", flush=True)
    fresh("A0")
    if os.path.exists(ARM):
        os.remove(ARM)
    shutil.copy2(ORIGINAL, ARM)
    READINGS["A"]["before_save"] = file_facts("A1 arm BEFORE the save", ARM)
    gate("A1 the arm copy on disk is byte-identical to the ORIGINAL",
         READINGS["A"]["before_save"].get("md5") == ORIG_MD5, str(READINGS["A"]["before_save"].get("md5")))
    with Preload("A2"):
        g.open_panel(ARM)                       # the edit-ready state; here it only makes the load explicit
        time.sleep(1.0)
        es = g.exec_state(ARM)
        READINGS["A"]["exec_state_preloaded"] = es
        fact(f"A3 exec_state(arm) with the ORIGINAL PRELOADED = {es} (1 = idle/runnable, 0 = broken). "
             f"Pre-decided 14a predicts 1; this reading is LOGGED, not gated.")
        t0 = time.time()
        err = None
        try:
            size = g.save(ARM)                  # DEFAULT allow_broken=False — the gui_save divert cannot happen
        except Exception as e:                                                    # noqa: BLE001
            size, err = None, f"{type(e).__name__}: {e}"
        dt = time.time() - t0
        READINGS["A"]["save"] = {"seconds": round(dt, 2), "returned_bytes": size, "exception": err}
        fact(f"A4 g.save(arm) took {dt:.2f} s and returned {size!r}; exception = {err!r}")
        gate("A4 g.save(arm) returned without raising", err is None, str(err))
        try:
            g.close_panel(ARM)
        except Exception as e:                                                    # noqa: BLE001
            fact(f"A4b close_panel(arm) raised {type(e).__name__}: {e}")
    READINGS["A"]["after_save"] = file_facts("A5 arm AFTER the save", ARM)
    b0, b1 = READINGS["A"]["before_save"], READINGS["A"]["after_save"]
    moved = (b0.get("md5") != b1.get("md5")) or (b0.get("size") != b1.get("size"))
    READINGS["A"]["bytes_moved"] = bool(moved)
    fact(f"A5 THE BYTES {'MOVED' if moved else 'DID NOT MOVE'} across the save: md5 {b0.get('md5')} -> "
         f"{b1.get('md5')}, size {b0.get('size')} -> {b1.get('size')} B. No prediction was offered for this; "
         f"it is the input to gate B, which asks whether whatever was written changed the file's LINKAGE.")
    fact(f"A refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("A")


# ============================================================================== PHASE B — LINKAGE CONTROL
def phase_b():
    """Does the SAVED arm still call exactly the subVIs the ORIGINAL calls?

    🔴 RE-SPECIFIED ON MEASUREMENT — `docs/cycle27-plan.md` Pre-decided 29(g), cycle 46. This phase used to ask
    whether the saved arm's (cold, preloaded) `ExecState` pair matched a PRISTINE BYTE COPY's. T1
    (`tools/bench/s1_subvi_paths.log`, 15/0) measured that **the byte copy is the defective side** — cold, it
    re-binds 22 SubVI calls into `claudeDev\background VIs_COPY\`, loses 8 and reads 7 rows empty, while the
    COM-saved arm matches the ORIGINAL on all 98 rows in name and path. So the four `ExecState` readings are kept
    as RECORDED FACTS, the byte copy is kept as a LOGGED CONTROL, and the acceptance gate is **B6**: the arm's COLD
    SubVI table against **the ORIGINAL's** COLD SubVI table. NOT RUN by `--phases CD`; re-specified so replay is
    correct.

    ONE CONDITION PER CHILD PROCESS, ONE FRESH LabVIEW INSTANCE PER CHILD. This phase reads NOTHING itself: it
    calls the BUILT helper `tools/bench/diag_d1_execstate_preload.py` four times (`run_condition()` `:155-179`,
    which spawns `child()` `:88-151`, each child doing its own `lv_restart` `:96-97`). The earlier version of this
    phase took all four readings in ONE instance, and that instrument manufactures the very finding it is meant to
    detect: `ARM` and `CTL` are byte copies calling the SAME subVIs under the SAME qualified names, so reading the
    arm first loads that hierarchy and the control's "cold" reading is a preloaded one wearing a cold label
    (Pre-decided 14a's own mechanism; `docs/cycle27-plan.md:608-613`). No child opens anything but its own target
    — plus, in the preloaded conditions, the ORIGINAL read-only, which IS the condition. No instance ever holds
    two copies of the main VI."""
    print("\n=== PHASE B: LINKAGE CONTROL — ONE CONDITION PER CHILD PROCESS, FOUR FRESH INSTANCES", flush=True)
    g.reset()                                  # this parent holds no COM proxy at all in phase B
    if os.path.exists(CTL):
        os.remove(CTL)
    shutil.copy2(ORIGINAL, CTL)
    READINGS["B"]["control_file"] = file_facts("B1 control", CTL)
    gate("B1 the control copy on disk is byte-identical to the ORIGINAL",
         READINGS["B"]["control_file"].get("md5") == ORIG_MD5, str(READINGS["B"]["control_file"].get("md5")))
    READINGS["B"]["arm_file"] = file_facts("B1b arm as phase A left it", ARM)

    gate("B0a the reused helper preloads THIS ORIGINAL",
         os.path.normcase(os.path.abspath(D1ES.ORIG)) == os.path.normcase(os.path.abspath(ORIGINAL)),
         f"helper ORIG {D1ES.ORIG!r}")
    gate("B0b the reused helper pins the same ORIGINAL md5", D1ES.ROUTEB_PINNED_MD5 == ORIG_MD5,
         f"{D1ES.ROUTEB_PINNED_MD5} vs {ORIG_MD5}")

    # B-i .. B-iv, IN THIS ORDER. `preload=True` = the child opens the ORIGINAL read-only first (14a's condition).
    conditions = [("B-i", "S1ARM-COLD", ARM, False),
                  ("B-ii", "S1CTL-COLD", CTL, False),
                  ("B-iii", "S1ARM-PRELOAD", ARM, True),
                  ("B-iv", "S1CTL-PRELOAD", CTL, True)]
    READINGS["B"]["readings"] = []
    reads = {}
    for label, tag, target, preload in conditions:
        pid0 = labview_pid()
        res = D1ES.run_condition(tag, target, preload)
        pid1 = labview_pid()
        es = res.get("execstate")
        reads[tag] = es
        rec = {"step": label, "condition": tag, "target": os.path.basename(target), "preload": preload,
               "exec_state": es, "labview_pid_before_child": pid0, "labview_pid_of_the_reading": pid1,
               "restart_rc": res.get("restart_rc"), "vi_name": res.get("name"),
               "handles_after_restart": res.get("handles_after_restart"), "handles_end": res.get("handles_end"),
               "original_execstate_while_preloaded": res.get("orig_execstate"),
               "child_json": f"tools/bench/d1_es_{tag}.json"}
        READINGS["B"]["readings"].append(rec)
        fact(f"{label} {tag}: ExecState {es!r} on {os.path.basename(target)} (preload={preload}) in LabVIEW "
             f"pid {pid1!r}; pid before this child {pid0!r}; lv_restart rc={res.get('restart_rc')!r}; handles "
             f"{res.get('handles_after_restart')!r} -> {res.get('handles_end')!r}; VI.Name {res.get('name')!r}"
             + (f"; ORIGINAL's own ExecState while resident {res.get('orig_execstate')!r}" if preload else ""))
        gate(f"{label} {tag} child completed and returned an integer ExecState", isinstance(es, int), repr(es))
        dump()                                 # each reading is on disk before the next child starts

    pids = [r["labview_pid_of_the_reading"] for r in READINGS["B"]["readings"]]
    READINGS["B"]["reading_pids"] = pids
    gate("B0c each of the four readings came from its OWN LabVIEW instance (four distinct pids)",
         all(pids) and len(set(pids)) == 4, f"pids {pids}", fatal=False)

    arm_pair = [reads["S1ARM-COLD"], reads["S1ARM-PRELOAD"]]
    ctl_pair = [reads["S1CTL-COLD"], reads["S1CTL-PRELOAD"]]
    READINGS["B"]["arm_pair"] = arm_pair
    READINGS["B"]["control_pair"] = ctl_pair
    fact(f"B2/B3 (cold, preloaded) — SAVED ARM {arm_pair} vs BYTE-COPY CONTROL {ctl_pair}. RECORDED, NOT GATED "
         f"(Pre-decided 29(g)): T1 measured the byte copy to be the DEFECTIVE side, so a difference here is the "
         f"byte copy's re-binding, not the arm's. Each of the four was taken in its own instance.")

    # ---- B6: THE ACCEPTANCE GATE, re-specified on measurement (Pre-decided 29(g)).
    # The reference is the ORIGINAL's own COLD SubVI table, taken in its own child process and its own fresh
    # LabVIEW instance. The byte copy is censused too, but ONLY as a logged control — it is never compared against.
    g.reset()
    arm_tbl, arm_rec = cold_subvi_table("B6a-ARM-COLD", ARM)
    orig_tbl, orig_rec = cold_subvi_table("B6b-ORIG-COLD", ORIGINAL)
    ctl_tbl, ctl_rec = cold_subvi_table("B6c-CTL-COLD-CONTROL", CTL)          # LOGGED CONTROL ONLY
    READINGS["B"]["subvi_census"] = {"arm": arm_rec, "original": orig_rec, "byte_copy_control": ctl_rec}
    cmp_b = compare_subvi_tables(arm_tbl, orig_tbl, set())                    # the arm deletes NOTHING
    READINGS["B"]["subvi_compare_arm_vs_original"] = cmp_b
    if not cmp_b["equal"]:
        log_table_diff("B6 arm vs ORIGINAL", cmp_b)
    fact(f"B6 CONTROL (logged, never compared): the byte copy censused {ctl_rec['n_rows']} rows, "
         f"{ctl_rec['into_background_vis_copy']} into 'background VIs_COPY', {ctl_rec['empty_rows']} empty")
    gate(f"B6-i the ORIGINAL's COLD SubVI table has {PIN_SUBVI_ROWS} rows",
         orig_rec["n_rows"] == PIN_SUBVI_ROWS, f"{orig_rec['n_rows']} rows", fatal=False)
    gate("B6 the SAVED ARM's COLD SubVI table equals the ORIGINAL's, key-for-key in name AND path, with zero "
         "rows into 'background VIs_COPY' and no empty row",
         cmp_b["equal"] and arm_rec["into_background_vis_copy"] == 0 and arm_rec["empty_rows"] == 0,
         f"equal={cmp_b['equal']} missing={len(cmp_b['missing'])} extra={len(cmp_b['extra'])} "
         f"changed={len(cmp_b['changed'])} bg_copy={arm_rec['into_background_vis_copy']} "
         f"empty={arm_rec['empty_rows']}")

    g.reset()                                  # drop every proxy before touching the file on disk
    removed, why = False, ""
    try:
        os.remove(CTL)
        removed = True
    except Exception as e:                                                        # noqa: BLE001
        why = f"{type(e).__name__}: {e}"
    READINGS["B"]["control_deleted"] = {"removed": removed, "error": why}
    fact(f"B4 the control file is scratch and is deleted: removed={removed}{(' — ' + why) if why else ''} "
         f"(if it survived, phase C's restart frees it and C0 removes it); the ARM FILE IS KEPT")
    dump()
    fact(f"B5 readings written to {OUT_SAVEROUTE}")
    fact(f"B refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("B")


# ============================================================================== PHASE C — S1 PROPER
def phase_c():
    """The stage itself: a fresh copy of the ORIGINAL, the two FIXTURE TIFF nodes cut, the copy SAVED.
    Body re-cut from `build_d1_routeb_v7.py` `s1()` `:697-725` + `s1t()` `:728-751`."""
    print("\n=== PHASE C: S1 PROPER — cut the fixture TIFF writer from a fresh copy and SAVE it", flush=True)
    fresh("C0")
    if os.path.exists(CTL):                    # B4's delete can lose to a file lock; the restart freed it
        try:
            os.remove(CTL)
            fact("C0 the phase-B control file was still on disk after the restart and is now deleted")
        except Exception as e:                                                    # noqa: BLE001
            fact(f"C0 the phase-B control file could NOT be deleted ({type(e).__name__}: {e})")
    if os.path.exists(TARGET):
        os.remove(TARGET)
    shutil.copy2(ORIGINAL, TARGET)
    READINGS["C"]["copy"] = file_facts("C1 the S1 working copy", TARGET)
    gate("C1 the S1 working copy on disk is byte-identical to the ORIGINAL",
         READINGS["C"]["copy"].get("md5") == ORIG_MD5, str(READINGS["C"]["copy"].get("md5")))

    with Preload("C2"):
        g.open_panel(TARGET)                   # required before ANY scripting edit (skill: `ensure_loaded` note)
        time.sleep(1.0)
        got = {c: g.count(TARGET, c) for c in BEFORE}
        READINGS["C"]["before_census"] = got
        fact(f"C3 BEFORE census: {got}")
        gate("C3 the copy matches the pinned BEFORE census", all(got[c] == BEFORE[c] for c in BEFORE),
             f"{ {c: (BEFORE[c], got[c]) for c in BEFORE if got[c] != BEFORE[c]} } (empty = all match)")

        # ---- C4: delete the two FIXTURE nodes, in this order, with v7 `s1t`'s own gates.
        # Pre-decided 21(d): a traverse INDEX is not a stable key. `report_all` is re-read INSIDE the loop, once
        # per deletion, and no index is carried across a mutation.
        d43 = diag_index(TARGET, FRAME_BODY_UID)
        fact(f"C4 frame body #{FRAME_BODY_UID} reads Traverse index {d43} — re-read here, never cached "
             f"(Pre-decided 21(d): the same uid read 43 and 56 inside ONE instance in run 10)")
        bare0 = bare_named_sinks(TARGET, d43)
        fact(f"C4 bare named sinks on the frame body BEFORE the deletions: {len(bare0)}")
        for uid, cls, label in D1.TIFF_DELETE:
            order = [o["uid"] for o in g.report_all(TARGET, cls)]
            gate(f"C4 #{uid} ({label}) is present as {cls} before deletion", uid in order, f"not among {cls}")
            g.delete_object(TARGET, cls, order.index(uid), verify=False)
            fact(f"C4 deleted #{uid} ({label}) at {cls} index {order.index(uid)}")

        # ---- C5: ONE pre-pass reaper, outside any row loop — the shape Pre-decided 17 `:204-207` exonerates.
        g.remove_bad_wires_scripted(TARGET)
        fact("C5 remove_bad_wires_scripted ran ONCE, as a pre-pass (v7 `:740`); this file has no row loop, and "
             "`gscript.net_map` is neither imported nor called (Pre-decided 17)")

        node_uids = {o["uid"] for o in g.report_all(TARGET, "Node")}
        for uid, _cls, label in D1.TIFF_DELETE:
            gate(f"C4 #{uid} ({label}) is GONE after the deletions", uid not in node_uids)
        c1 = {c: g.count(TARGET, c) for c in AFTER_S1T}
        READINGS["C"]["after_census"] = c1
        gate("C6 counts moved exactly as §11h predicts (SubVI 97 · Function 180 · Node 624 · Wire 1899)",
             c1 == AFTER_S1T, f"{c1}")
        bare1 = bare_named_sinks(TARGET, d43, fresh=True)
        new_bare = {k: v for k, v in bare1.items() if k not in bare0}
        READINGS["C"]["new_bare_named_sinks"] = sorted((u, i, n) for (u, i), n in new_bare.items())
        gate("C7 no STAYING node was left with a bare named input", not new_bare,
             f"newly bare {READINGS['C']['new_bare_named_sinks'][:8]}")

        es = g.exec_state(TARGET)
        READINGS["C"]["exec_state_preloaded"] = es
        fact(f"C8 exec_state(target) with the ORIGINAL PRELOADED = {es} (the deletions are predicted harmless; "
             f"C9 is the test that matters)")
        t0 = time.time()
        err = None
        try:
            size = g.save(TARGET)               # DEFAULT allow_broken=False — no divert to gui_save, by design
        except Exception as e:                                                    # noqa: BLE001
            size, err = None, f"{type(e).__name__}: {e}"
        dt = time.time() - t0
        READINGS["C"]["save"] = {"seconds": round(dt, 2), "returned_bytes": size, "exception": err}
        fact(f"C9 g.save(target) took {dt:.2f} s and returned {size!r}; exception = {err!r}")
        gate("C9 g.save(target) returned without raising", err is None, str(err))
        try:
            g.close_panel(TARGET)
        except Exception as e:                                                    # noqa: BLE001
            fact(f"C9b close_panel(target) raised {type(e).__name__}: {e}")
    READINGS["C"]["artefact"] = file_facts("C9 THE STAGE ARTEFACT", TARGET)
    fact(f"C refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("C")


# ============================================================================== PHASE D — VERIFY
def phase_d():
    """The saved artefact is re-read in a FRESH instance under BOTH conditions. This is the half of Pre-decided
    16(b)'s MASKING hazard that can be answered mechanically: a preloaded 1 beside its own cold reading.

    🆕 D5 (Pre-decided 29(g)) adds the part `ExecState` cannot answer: the artefact's COLD SubVI table against
    the ORIGINAL's COLD SubVI table, each in its own child process and its own fresh LabVIEW instance."""
    print("\n=== PHASE D: VERIFY the saved artefact in a fresh instance, COLD and PRELOADED", flush=True)
    fresh("D0")
    READINGS["D"]["artefact"] = file_facts("D0 the artefact as phase C left it", TARGET)
    cold = g.exec_state(TARGET)
    READINGS["D"]["exec_state_cold"] = cold
    fact(f"D1 COLD exec_state({os.path.basename(TARGET)}) = {cold} — labelled COLD and, by Pre-decided 14a, "
         f"UNREAD as a verdict on legality")
    with Preload("D2"):
        pre = g.exec_state(TARGET)
        READINGS["D"]["exec_state_preloaded"] = pre
        fact(f"D2 PRELOADED exec_state({os.path.basename(TARGET)}) = {pre}")
    gate("D2 the PRELOADED reading of the saved artefact is 1", READINGS["D"].get("exec_state_preloaded") == 1,
         f"cold {cold}, preloaded {READINGS['D'].get('exec_state_preloaded')}")
    fact(f"D2b BOTH ExecState readings of {os.path.basename(TARGET)}, labelled: COLD = "
         f"{READINGS['D'].get('exec_state_cold')!r} (RECORDED, not gated — 14a: a cold read measures subVI "
         f"linkage) · PRELOADED = {READINGS['D'].get('exec_state_preloaded')!r} (gated)")
    dump()

    # ================= D5 — Pre-decided 29(g): THE ARTEFACT'S SubVI TABLE vs THE ORIGINAL'S, BOTH COLD =========
    # The acceptance reference is the ORIGINAL, never a byte copy: T1 (tools/bench/s1_subvi_paths.log, 15/0)
    # measured the byte copy to be the defective side (22 rows re-bound into claudeDev\background VIs_COPY\,
    # 8 lost, 7 empty) while the COM-saved copy matched the ORIGINAL on all 98 rows. Mechanism REUSED from
    # tools/bench/s1_subvi_paths.py: one condition per child process, one fresh LabVIEW instance per child,
    # no preload anywhere. This parent holds no COM proxy across it.
    print("\n=== D5: the SAVED ARTEFACT's COLD SubVI table against the ORIGINAL's COLD SubVI table", flush=True)
    g.reset()
    s1_tbl, s1_rec = cold_subvi_table("D5a-S1COPY-COLD", TARGET)
    orig_tbl, orig_rec = cold_subvi_table("D5b-ORIG-COLD", ORIGINAL)
    cmp_d = compare_subvi_tables(s1_tbl, orig_tbl, {TIFF_SUBVI_KEY})
    READINGS["D"]["subvi_census"] = {"s1_artefact": s1_rec, "original": orig_rec}
    READINGS["D"]["subvi_compare_s1_vs_original"] = cmp_d
    READINGS["D"]["expected_missing_key"] = list(TIFF_SUBVI_KEY)
    fact(f"D5 row counts: S1 artefact {s1_rec['n_rows']} vs ORIGINAL {orig_rec['n_rows']} "
         f"(expected {PIN_SUBVI_ROWS - 1} vs {PIN_SUBVI_ROWS}); the one key the stage removes is "
         f"(diagram {TIFF_SUBVI_KEY[0]}, node {TIFF_SUBVI_KEY[1]}) = #22700 IMAQ Write TIFF File 2")
    if not cmp_d["equal"]:
        log_table_diff("D5 S1 artefact vs ORIGINAL", cmp_d)
    gate(f"D5-i the ORIGINAL's COLD SubVI table has {PIN_SUBVI_ROWS} rows",
         orig_rec["n_rows"] == PIN_SUBVI_ROWS, f"{orig_rec['n_rows']} rows", fatal=False)
    gate(f"D5-ii the S1 artefact's COLD SubVI table has {PIN_SUBVI_ROWS - 1} rows",
         s1_rec["n_rows"] == PIN_SUBVI_ROWS - 1, f"{s1_rec['n_rows']} rows", fatal=False)
    ok_a = cmp_d["equal"]
    ok_b = s1_rec["into_background_vis_copy"] == 0
    ok_c = s1_rec["empty_rows"] == 0
    gate("D5a the S1 table is EXACTLY the ORIGINAL's table minus (639, 22700), every surviving row identical in "
         "BOTH name and path", ok_a,
         f"missing={len(cmp_d['missing'])} extra={len(cmp_d['extra'])} changed={len(cmp_d['changed'])} "
         f"not_deleted={cmp_d['not_deleted']} bad_key={cmp_d['expected_key_absent_from_reference']}", fatal=False)
    gate("D5b ZERO rows of the S1 table point into claudeDev\\background VIs_COPY\\", ok_b,
         f"{s1_rec['into_background_vis_copy']} rows, first keys {s1_rec['background_vis_copy_keys']}", fatal=False)
    gate("D5c no row of the S1 table has an empty name or an empty path", ok_c,
         f"{s1_rec['empty_rows']} rows, first keys {s1_rec['empty_keys']}", fatal=False)
    dump()
    gate("D5 FATAL the saved S1 artefact's SubVI table is accepted against the ORIGINAL (a AND b AND c)",
         ok_a and ok_b and ok_c, f"a={ok_a} b={ok_b} c={ok_c}")
    dump()
    fact(f"D3 every phase's readings, md5s, sizes and version bytes written to {OUT_READINGS}")
    fact(f"D refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("D")                              # D4


# ============================================================================== main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="S1 stage. Phases are selectable; C depends on neither A nor B.")
    ap.add_argument("--phases", default="ABCD",
                    help="any subset of ABCD, run in that fixed order. Default ABCD. Phases A and B ran "
                         "2026-09-19 (tools/bench/stage_d1_s1.log; arm D1_s1arm_savetest.vi md5 "
                         "e0112963cc1b9e3be29d2bb053ba9029, 475141 B) and are not re-run by --phases CD; phase C "
                         "starts from a fresh copy of the ORIGINAL and depends on neither.")
    args = ap.parse_args()
    sel = [ch for ch in "ABCD" if ch in args.phases.upper()]
    if not sel:
        print(f"--phases {args.phases!r} selects nothing (expected a subset of ABCD)", flush=True)
        return 2
    t0 = time.time()
    g.reset()
    print(f"stage_d1_s1: PHASES {''.join(sel)} (of ABCD)", flush=True)
    print(f"stage_d1_s1: ORIGINAL {ORIGINAL}", flush=True)
    READINGS["original"]["file"] = file_facts("S0 the ORIGINAL, read-only", ORIGINAL)
    gate("S0 original md5 BEFORE equals the pin", READINGS["original"]["file"].get("md5") == ORIG_MD5,
         str(READINGS["original"]["file"].get("md5")))
    fact(f"S0 handles at entry: {labview_handles()} (0 = LabVIEW not started yet); refs {g.ref_counts()}")
    try:
        for ch in sel:
            {"A": phase_a, "B": phase_b, "C": phase_c, "D": phase_d}[ch]()
    except Stop as e:
        fact(f"STOP at a fatal gate: {e} — the chain stops here and every artefact written so far STAYS ON DISK")
    except BaseException as e:                                                    # noqa: BLE001
        fact(f"CRASH {type(e).__name__}: {e} — every artefact written so far STAYS ON DISK")
        raise
    finally:
        try:
            dump()
        except Exception as e:                                                    # noqa: BLE001
            fact(f"the JSON artefacts could not be written ({type(e).__name__}: {e})")
        m = md5(ORIGINAL)
        gate("S6 original md5 AFTER the whole run", m == ORIG_MD5, m, fatal=False)
        for tag, p in (("arm", ARM), ("control", CTL), ("ARTEFACT", TARGET)):
            fact(f"FINAL {tag}: {os.path.basename(p)} on disk = {os.path.exists(p)}"
                 + (f", md5 {md5(p)}, {os.path.getsize(p)} B" if os.path.exists(p) else ""))
        fact(f"FINAL refs: {g.ref_counts()} (`live` should be 0); handles {labview_handles()}")
    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== stage_d1_s1 (phases {''.join(sel)}): {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
