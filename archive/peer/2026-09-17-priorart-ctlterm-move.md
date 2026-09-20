# priorart-ctlterm-move

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.9581  in 72 / out 44950 / cache-create 197896 / cache-read 5710105  (627s, 50 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (631s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
r"""probe_move_ctlterm_v0.py - D1's SECOND relocation unknown: can a FRONT-PANEL CONTROL TERMINAL be reparented?

WHY THIS EXISTS, and why it is a separate run rather than a step of the D1 build. Step 0's census
(`tools/bench/diag_d1_step0.log`, `docs/d1-build-plan.md` s0d) measured that at least SIX front-panel objects have
their diagram terminal INSIDE the frame loop body and are read or written by nodes that must move to the new
tracking loop: controls `Auto-Reset` #17472 (w9806 -> #9647), `Reset Tracking` #5605 (w10312 -> #10247), `Z/dZ` #47
(w730 -> #2222), `Correction Factor` #9289 (w6096 -> #2222), and indicators `min value` #17257 (w17287 <- #10969,
read back by the implicit property #17289) and `Force (pN) vs Extension (nm) ` #8038 (w10908 <- #11261).

A panel object has EXACTLY ONE diagram terminal (`fp_labels` 114 == `report("ControlTerminal")` 114,
docs/toolkit-capabilities.md:511), and these terminals are inside `Diagram#639` on purpose: a Boolean wired in
from OUTSIDE a loop is read ONCE, which is NI's infinite-loop mistake (docs/stage2-plan.md:90-94, cited by
d1-build-plan s3). So routing `Reset Tracking` into the new loop through a tunnel would change WHEN it is read,
and the user flips it during a run - a computation change, not scheduling (rule 1a).

`docs/d1-build-plan.md` decision 4 says a never-run relocation route is PROBED FIRST and never inside the D1
build. `GObject.Move` is proven for a plain node and for a CaseStructure-with-contents (phase P, 12/0,
`tools/bench/probe_move_into_v0.log`); it is UNMEASURED for class `ControlTerminal`. This probe measures exactly
that, and nothing else. It takes no decision: if the answer is no, which of the three routes D1 uses is a
judgement call (s0d), not this file's.

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "before creating any new op/tool/recipe"):
  * `OpMoveIn_v0.vi` is BUILT and its contract is recorded (STATUS OPEN 19b: ExecState 1, UID control label
    `'UID 3'`); `move_in()` below is `tools/recipes/probe_move_into_v0.py:488-503` with the canonical op path.
  * `OpOwnerChain_v1` / `read_owner` - any uid -> its owner. Imported verbatim, no new op.
  * `g.report_all("ControlTerminal")` returns all 114 in ONE run; `g.panel_wiring()` gives label -> connected
    wire for all 114 in one run; `g.loop_in("while", ...)` creates the destination loop; `g.new_since()` gives the
    created object AND the index the creating op reported (docs/NAMES.md:511-534 - never a re-derived index).
  * `grep -n "ctl\|terminal" tools/gscript.py`: `connect_ctl` WIRES a node terminal to a panel object's terminal;
    `create_control` creates a control FROM a node terminal. Neither relocates an existing terminal, and there is
    no Local creator (`toolkit-capabilities.md:254`). So no existing helper answers this.
  * `ls tools/recipes | grep -i move`: build_opmove / build_opmovebyindex / build_opmoveout / probe_move_into_v0 -
    none touches ControlTerminal.

IDENTIFICATION, BY EFFECT RATHER THAN BY A LOOKUP. There is no reader from a `ControlTerminal` uid to its panel
object. But phase P measured that a move CUTS the wires that crossed the old border (Wire 1902 -> 1895), so the
control whose `panel_wiring` row loses its wire IS the one whose terminal moved. That is the identification, and
it is also the proof that the object moved was a real panel terminal.

PREDICTION CONTRACT
  Q0a/Q0b  the original's md5 is 2a78e17c449cacdaf5da389818526859 before AND after.
  Q1   `report_all(MAIN, 'ControlTerminal')` returns 114 objects (toolkit-capabilities.md:511) and
       `panel_wiring(MAIN)` returns 114 rows.
  Q1b  the owner-chain census finds at least one ControlTerminal whose owner is `Diagram#639` (the frame loop
       body) - step 0 measured six panel objects wired to nodes on that diagram, so 0 would falsify step 0.
       What class a ControlTerminal's OWNER is, is reported, not predicted.
  Q2a  a While loop is created on `Diagram#686` (the holder of #637): +1 Diagram, +1 WhileLoop.
  Q2   CONTROL ARM - `#8885 Multiply` reparents into the new body diagram, exactly as phase P's P2 did. A failure
       here makes the run INVALID and it STOPS; nothing is concluded about ControlTerminal.
  Q3   THE QUESTION - the chosen `ControlTerminal` reparents: `ownerchain(term)` -> the new body diagram, and the
       VI's total `ControlTerminal` count is UNCHANGED at 114 (the terminal was moved, not destroyed).
  Q4   `panel_wiring` still returns 114 rows and every label is still present - the panel object survived; the
       row whose wire changed names WHICH object was moved (reported, not predicted).
  Q5   Node count == before + 1 (the new While loop) after the junk Invokes are purged. ExecState 0 afterwards is
       EXPECTED (the move cuts wires) and is reported, not gated.
  Q6   the scratch copy is deleted in the same run; handle count before and after.

A failure of Q3 is a real answer, not a defect: it says route (i) of d1-build-plan s0d is closed, and the choice
between (ii) and (iii) goes to the judgement session. No repair pass, no second construction.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/probe_move_ctlterm_v0.log \
      -- py -u tools/recipes/probe_move_ctlterm_v0.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
from build_opownerchain_v1 import MAIN, read_owner  # noqa: E402
from build_opownerchain_v1 import OP as OP_OWNER  # noqa: E402

ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = g.CLAUDEDEV
OPIN = os.path.join(CLAUDEDEV, "OpMoveIn_v0.vi")
UID_LABEL = "UID 3"                      # STATUS OPEN 19b, measured when OpMoveIn_v0 was built
LABELS = os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json")
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_d1ctlterm_{int(time.time())}.vi")
OUT = os.path.join(ROOT, "tools", "bench", "ctlterm_owners.json")

FRAME_BODY_UID = 639       # Diagram owned by WhileLoop #637
SIBLING_DIAG_UID = 686     # the FlatSequenceFrame diagram that holds #637 itself
PLAIN_NODE = 8885          # the control arm, exactly as phase P used it
N_PANEL = 114

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
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


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip() or 0)
    except ValueError:
        return 0


def move_in(target, uid, dest_diagram_index, position):
    """tools/recipes/probe_move_into_v0.py:488-503, with the canonical op path. The Move returns NO reference to
    the object at its new home (archive/peer/2026-08-28-copy-nodes-between-vis.md:51), so every check afterwards
    is a uid-addressed re-read."""
    g.ensure_loaded(target)
    vi = g.op(OPIN)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", int(dest_diagram_index))
    vi.SetControlValue("index 2", 0)
    vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, ""))
    vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", "")
    vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue(UID_LABEL, int(uid))
    vi.SetControlValue("position", tuple(int(v) for v in position))
    g._run(vi)
    return int(vi.GetControlValue("UID"))


_OL = None


def owner_of(target, uid, strict=True):
    """(owner class, owner uid) with the identity echo checked - a read whose `uid_back` is not the uid asked
    about is NOT an answer and is raised rather than returned as 0
    (archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29)."""
    global _OL
    if _OL is None:
        with open(LABELS, encoding="utf-8") as f:
            _OL = json.load(f)
    vi = g.op(OP_OWNER)
    saved = MAIN
    try:
        import build_opownerchain_v1 as B
        B.MAIN = target
        r = read_owner(vi, _OL, uid)
    finally:
        try:
            B.MAIN = saved
        except Exception:
            pass
    if strict and (r["uid_back"] != int(uid) or r["errs"]):
        raise RuntimeError(f"owner_of({uid}) is not an answer: echoed {r['cls_back']!r}#{r['uid_back']}, "
                           f"errors {r['errs'][:120]!r}")
    return r["ownercls"], r["owner_uid"], r


def diag_index(target, uid):
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    m0 = md5(MAIN)
    gate("Q0a original md5 before", m0 == ORIG_MD5, m0)
    if m0 != ORIG_MD5:
        return 1
    if not os.path.exists(OPIN):
        gate("Q1 OpMoveIn_v0 exists", False, OPIN)
        return 1
    h0 = handles()
    print(f"  handles before: {h0}", flush=True)

    shutil.copy2(MAIN, SCRATCH)
    chosen, panel_before, owners = None, [], {}
    try:
        g.open_panel(SCRATCH)
        inv0 = g.uids(SCRATCH, "Invoke")
        n_before = g.count(SCRATCH, "Node")
        ct_before = g.count(SCRATCH, "ControlTerminal")
        d_before = g.count(SCRATCH, "Diagram")
        panel_before = g.panel_wiring(SCRATCH)
        fact(f"scratch: Node {n_before}, ControlTerminal {ct_before}, Diagram {d_before}, "
             f"panel rows {len(panel_before)}")
        gate("Q1 114 ControlTerminals and 114 panel rows",
             ct_before == N_PANEL and len(panel_before) == N_PANEL,
             f"ControlTerminal {ct_before}, panel {len(panel_before)}")

        # --- Q1b: which ControlTerminals sit inside the frame loop body? -----------------
        cts = g.report_all(SCRATCH, "ControlTerminal")
        fact(f"report_all('ControlTerminal') returned {len(cts)} objects; owner classes "
             f"{sorted({c.get('owner', '') for c in cts})}")
        t0 = time.time()
        inside = []
        for c in cts:
            if time.time() - t0 > 420:
                fact(f"owner census budget reached after {len(owners)} of {len(cts)}")
                break
            try:
                ocls, ouid, raw = owner_of(SCRATCH, c["uid"], strict=False)
            except Exception as e:
                owners[c["uid"]] = {"error": str(e)[:80]}
                continue
            owners[c["uid"]] = {"owner_class": ocls, "owner_uid": ouid, "pos": c.get("pos"),
                                "self_class": raw.get("cls_back"), "echo": raw.get("uid_back")}
            if ouid == FRAME_BODY_UID:
                inside.append(c["uid"])
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump({"md5": m0, "owners": {str(k): v for k, v in owners.items()}}, f, indent=1, default=str)
        oclasses = sorted({str(v.get("owner_class")) for v in owners.values() if "owner_class" in v})
        fact(f"a ControlTerminal's OWNER class(es), measured: {oclasses}")
        fact(f"{len(inside)} ControlTerminal(s) are owned by Diagram#{FRAME_BODY_UID} (the frame loop body): "
             f"{inside[:20]}")
        if not gate("Q1b at least one ControlTerminal sits inside the frame loop body", bool(inside),
                    f"{len(inside)} found; owner census covered {len(owners)}/{len(cts)}"):
            return 1
        chosen = inside[0]

        # --- Q2a: the destination loop ---------------------------------------------------
        sib_i = diag_index(SCRATCH, SIBLING_DIAG_UID)
        dg0, wl0 = g.uids(SCRATCH, "Diagram"), g.uids(SCRATCH, "WhileLoop")
        g.loop_in("while", SCRATCH, sib_i, (2600, 2600))
        new_dg, new_wl = g.new_since(SCRATCH, "Diagram", dg0), g.new_since(SCRATCH, "WhileLoop", wl0)
        if not gate("Q2a a While loop was created on the sibling diagram",
                    len(new_dg) == 1 and len(new_wl) == 1,
                    f"+{len(new_dg)} diagrams, +{len(new_wl)} while loops"):
            return 1
        body_uid, loop_uid = new_dg[0]["uid"], new_wl[0]["uid"]
        body_i = new_dg[0].get("i", diag_index(SCRATCH, body_uid))
        fact(f"new WhileLoop #{loop_uid}, body Diagram #{body_uid} at Traverse index {body_i}")

        # --- Q2: the CONTROL ARM ---------------------------------------------------------
        move_in(SCRATCH, PLAIN_NODE, body_i, (60, 60))
        try:
            oc, ou, _ = owner_of(SCRATCH, PLAIN_NODE)
            oc2, ou2, _ = owner_of(SCRATCH, ou) if ou else (None, None, None)
            ok = gate("Q2 CONTROL ARM: a plain node reparents into the new loop body",
                      ou == body_uid and ou2 == loop_uid,
                      f"owner({PLAIN_NODE}) = {oc}#{ou} (want Diagram#{body_uid}); owner(owner) = {oc2}#{ou2}")
        except Exception as e:
            ok = gate("Q2 CONTROL ARM: a plain node reparents into the new loop body", False,
                      f"UNRESOLVED READ: {str(e)[:200]}")
        if not ok:
            print("\nSTOP: the CONTROL ARM failed, so this run is INVALID - Q3 is not attempted and nothing is "
                  "concluded about ControlTerminal.", flush=True)
            return 1

        # --- Q3: THE QUESTION ------------------------------------------------------------
        fact(f"moving ControlTerminal #{chosen} (owner was Diagram#{FRAME_BODY_UID}) into Diagram#{body_uid}")
        r2 = move_in(SCRATCH, chosen, body_i, (60, 400))
        ct_after = g.count(SCRATCH, "ControlTerminal")
        try:
            oc3, ou3, raw3 = owner_of(SCRATCH, chosen, strict=False)
            gate("Q3 a ControlTerminal reparents into the new loop body",
                 ou3 == body_uid and ct_after == ct_before,
                 f"move returned {r2}; owner({chosen}) = {oc3}#{ou3} (want Diagram#{body_uid}); "
                 f"ControlTerminal {ct_before} -> {ct_after}; self-echo {raw3.get('cls_back')!r}"
                 f"#{raw3.get('uid_back')}")
        except Exception as e:
            gate("Q3 a ControlTerminal reparents into the new loop body", False,
                 f"UNRESOLVED READ: {str(e)[:200]}; ControlTerminal {ct_before} -> {ct_after}")

        # --- Q4: the panel object survived, and WHICH one it was --------------------------
        panel_after = g.panel_wiring(SCRATCH)
        before_by = {(r["uid"], r["label"]): r["wire"] for r in panel_before}
        after_by = {(r["uid"], r["label"]): r["wire"] for r in panel_after}
        changed = [(k, before_by[k], after_by.get(k)) for k in before_by if after_by.get(k) != before_by[k]]
        gate("Q4 the panel still has 114 objects and every label survives",
             len(panel_after) == N_PANEL and set(before_by) == set(after_by),
             f"{len(panel_after)} rows; labels lost {sorted(set(before_by) - set(after_by))[:5]}")
        fact(f"panel rows whose connected wire changed (this NAMES the object whose terminal moved): {changed}")

        # --- Q5: nothing lost -------------------------------------------------------------
        junk = g.new_since(SCRATCH, "Invoke", inv0)
        for o in junk:
            ids = [x["uid"] for x in g.report(SCRATCH, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(SCRATCH, "Invoke", ids.index(o["uid"]), verify=False)
        fact(f"purged {len(junk)} junk Invoke(s) left by the two move_in runs: {[o['uid'] for o in junk]}")
        g.remove_bad_wires_scripted(SCRATCH)
        n_after, es = g.count(SCRATCH, "Node"), g.exec_state(SCRATCH)
        gate("Q5 no node lost by the two moves", n_after == n_before + 1,
             f"Node {n_before} -> {n_after}; ExecState now {es} (0 expected: wires were cut)")
        fact(f"ExecState after the moves and Remove Bad Wires: {es}; "
             f"Diagram {d_before} -> {g.count(SCRATCH, 'Diagram')}")
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("  scratch deleted", flush=True)
            except Exception as e:
                print(f"  scratch NOT deleted: {e}", flush=True)
        m1 = md5(MAIN)
        gate("Q0b original md5 after", m1 == ORIG_MD5, m1)
        print(f"  handles after: {handles()} (before {h0})", flush=True)

    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== probe_move_ctlterm_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Narrative relocated **verbatim** (rule 4): cycle 11??3 ??`archive/2026-09-16-status-cycles-11-13-narrative.md`;
D0 + GPU + lock history ??`archive/2026-09-17-status-d0-and-gpu-narrative.md`; **cycle 15's OPEN 1??1 long forms ??
`archive/2026-09-17-status-cycle15-narrative.md`** (STATUS was 165 lines). Open one only when a line here is
ambiguous. ?좑툘 **ONE SESSION AT A TIME** ??**re-read `CLAUDE.md` and this from disk.**

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; current cycle plan
   `docs/cycle15-plan.md`; **the build plan under review is `docs/d1-build-plan.md` REV 3**.
2. ??Prior-art gate live (`REFUTED:` / `FIXED:`); **`premature_build` (b) now exempts a RE-RUN** ??see OPEN 22.
3. ??Retrospectives 10??4 done; `retrospective.py` **v2**.
4. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
5. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??use a unique working-copy filename per
   run (peer `2026-09-17-moveinto-stale-in-memory-vi.md`, adopted).

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-build
  since: 2026-09-17 (D1 STEP 0)
  purpose: read-only step-0 census on the ORIGINAL (tunnels / shift regs / panel / OpWireSource_v5); LabVIEW
           restarted first (OPEN 23, 51,530 handles). No writes, no GUI, no hardware.
# 2026-09-17 05:1x-05:3x material/cycle15-movein-rev3: RELEASED. probe_move_into_v0 rev 7c 12 pass / 0 fail; one
# peer (moveinto-stale-in-memory-vi, ANSWERED, disposed). Original md5 2a78e17c449... asserted before AND after;
# scratch SCRATCH_d1move_* and OpMoveIn_v0_<epoch>.vi created+deleted in the same run; OpMoveIn_v0.vi kept as the
# finished op. No GUI, no hardware. ?좑툘 HANDLES 30,849 -> 51,530 in 14 s ??restart before the next batch (OPEN 23).
# Earlier holders and their md5/scratch records: the two 2026-09-17 archives, then the 2026-09-16 one.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change**; never infer one, never
ask per incident inside a declared state. Instruments: rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024,
offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure**, so the
acquisition loop applies the contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**;
fixture work unaffected (10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand

**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi` 162/162. **Say it exactly:**
bit-identical to the reference for the **first 10,018 frames only**, and both are **replay** artefacts (recorded
TIFFs, `FOR` loops, no acquisition, no stop protocol). **THE GAP (outcome review):** 168 op VIs, 116 recipes, 218
peer exchanges ??two replay VIs, **zero runnable experimental VIs**; cycle 15 is meant to end that.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`

1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated (`ForLoop#1359`) 쨌 autofocus CLOSED
   (`#10407` every 25 frames ??3.6 Hz) 쨌 27 undisposed peer archives 쨌 startup drives instruments (blocker at
   assembly) 쨌 A2 54/54, A3 112/170 (the 57 `FlatSequenceFrame` diagrams need ONE new op) 쨌 doc lint 2/4/3 쨌
   **the original writes a 1.3 MB TIFF per frame, ~118 MB/s at 90 Hz ??bound it or the disk fills in minutes**.
13. ??**CLOSED ??the frame loop's stop is MEASURED**: `#637` conditional terminal **uid 648 ??wire 3457 ??
   `CompoundArithmetic #11639`**; `stop (end) 2` #19587 ??#17883 ??`Tunnel#22085` of `CaseStructure#22082` is a
   SEPARATE path. `OpLoopEndRef_v0.vi`, 16/16. ??`docs/main-vi-stop-and-save.md` 짠1; archive 짠1.
14. ?뵶 The cycle-15 prior-art review is only PARTLY disposed ??A7/B3 block on purpose. **Judgement only.** ??짠2.
15. ??`bgrun.py --detach` built. 15b. ?뵶 its deadline kill misses an ORPHANED grandchild ??judgement. ??짠3.
16. ?뵶 **GPU whole-fixture divergence is OUTSIDE `decisions.md:38`** (bead 4, 10 frames of the all-beads-lost tail;
   1 flip at k1679). First 10,018 frames: **0 exceedances**. **Acceptability is a JUDGEMENT call.** ??짠4.
17. ??D0 CLOSED, 16/0. 17b. ?뵶 v3's R11 scored the *restart*, not the stop ??"stop works" is UNPROVEN. ??짠5.
19. ??**D1 REV 3 IS WRITTEN** (`docs/d1-build-plan.md`): the five spec decisions, the measured stop, phase P's
   result, `GPU_kernel_v1`'s six extra pane inputs and their values, the stream+accumulate writer, the minimal 1.5
   focus loop, node-by-node at the seam, and gates S1?밪6 / N1 / F1 / F2. ?뵶 **Its prior-art review is NOT
   dispatched and the build has NOT started ??judgement reads rev 3 first.** Its rev-2 findings ??짠6.
19b. ??**PHASE P ANSWERED, 12 pass / 0 fail, 14 s** (`tools/bench/probe_move_into_v0.log`, rev 7c).
   **`GObject.Move` with a wired `owner` reparents `CaseStructure #12589` WITH ITS CONTENTS** into a new While
   loop's body on Diagram 19 ??owner `Diagram#1170` ??`WhileLoop#1133`, **Diagram count 171 ??171**, Node 626 ??
   627, control arm `#8885` likewise. So the `Make Selection`/`Copy Selection`/`Paste` op family is **NOT needed**
   (it would also have required a GObject-ref array constructor the fleet does not have). ?좑툘 **The move CUTS the
   border wires** (Wire 1902 ??1895, LoopTunnel 132 ??130), so D1 must re-wire afterwards and `ExecState` is
   meaningful only at the end. `OpMoveIn_v0.vi` is BUILT (ExecState 1, UID control `'UID 3'`). Runs 1?? ??짠7.
20/21. ?뵶 Cycle 14's retrospective left two slugs DUE; ??both round-5 devices built. ??짠8.
22. ??**NEW ??`guard_cycle.premature_build` (b) now applies only to a recipe's FIRST run after its review.** If a
   build log `tools/bench/<recipe-stem>*.log` is newer than the newest prior-art archive, a re-run is allowed; a
   failed prediction is `guard_peer`'s gate, not this one. With **no** prior-art review archived it still blocks.
   Self-test `tools/bench/selftest_guard_cycle_rerun.log` **4/4** (first-run?뭨efused 쨌 re-run?뭓llowed 쨌
   no-review?뭨efused 쨌 regression review-newer?뭓llowed). `_rel()` added so a cross-drive path cannot crash the hook.
23. ?윞 **NEW ??handle count jumped 30,849 ??51,530 in one 14 s probe run** (baseline ??1,500). Restart LabVIEW
   before the next batch; attribution is a one-run `tools/bench/handle_audit.py` job, not a build item.

## NEXT

?뵶 **JUDGEMENT, in order:** (1) **read `docs/d1-build-plan.md` REV 3** and decide its five OPEN items ??chiefly
**#1 the GPU divergence (OPEN 16)** and **#2 the re-wiring list after a move**; (2) the two DUE slugs of OPEN 20
(`py tools/violations.py --due`); (3) authorise the build order, which is when the plan's prior-art review is
dispatched. ?윟 Then MATERIAL: the D1 build recipe ??one script, S1?밪6 ??N1 ??F1 ??F2, on a copy in claudeDev.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
`docs/d1-build-plan.md` **the build under review** 쨌 `docs/restructure-plan-4.6.md` target 쨌
`docs/pre-rig-master-plan.md` the plan 쨌 `docs/diagram-hierarchy.md` A2/A3 쨌 `docs/gpu-backend.md` GPU 쨌
narrative: the three status archives 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled in this session, so the review is below in full. Read-only: no lock taken, nothing run, no project file touched.

# PRIOR-ART REVIEW — `tools/recipes/probe_move_ctlterm_v0.py` (trigger: new-op)

## PART A — THE DIRECTION

### A1 SETTLED ALREADY — no. The central question is genuinely unmeasured.
A `632A400` / `GObject.Move` sweep across `docs/`, `archive/` and `tools/bench/` finds no run, log or exchange that moves an object of class `ControlTerminal` to a different owner. The nearest measurements are `tools/bench/probe_move_into_v0.log` / `docs/d1-build-plan.md:205-223` (classes `Function` and `CaseStructure` only) and `docs/toolkit-capabilities.md:525` (a panel-less Move "did not move" — the `ensure_loaded` decline, which this file covers via `g.open_panel` and `move_in`'s `ensure_loaded`). **Not slugged.**

### A2 REFUTED ALREADY — no.
`docs/decisions.md:19` and `docs/restructure-plan-4.6.md:79-81` declare `GObject.Move` "not needed", but `tools/recipes/probe_relocate_route.py:10-15` scopes that to plain primitives and subVI calls built fresh in the destination, and `docs/d1-build-plan.md:40-44` already overturned it for structures on measurement. Nothing argues against relocating a terminal. **Not slugged.**

### A3 CONTRADICTED — two, both quotable.

**(i) "no Local creator" is not what the cited line says, and other files say otherwise.**
The docstring ("WHAT ALREADY EXISTS") and `docs/d1-build-plan.md:155-156` dismiss route (ii) with *"no Local creator (`toolkit-capabilities.md:254`)"*. `docs/toolkit-capabilities.md:254` reads:

> "creating front-panel objects from nothing | no op. `create_control` / `create_indicator` work **from a node terminal**; a free-standing control needs `New VI Object` with a control style from the ring, never built"

That is about front-panel objects, not `Local` nodes. Against it, in our own files:
- `docs/toolkit-capabilities.md:263` — `Local` is a **valid** Traverse class, 8 objects in this VI.
- `docs/NAMES.md:246` — "`Local`: `Control` 6355403, **`Control Name` 6355400**"; `archive/peer/2026-09-14-implicit-property-node-linked-object.md:28-29` records `Control Name` as **read/write** — a Local's binding is re-pointable given a typed reference.
- `docs/restructure-plan-4.6.md:242-243` — the recorded route for a node the fleet cannot create is **copy it from a donor** (same mechanism as `docs/toolkit-capabilities.md:122`).
- `docs/restructure-plan-4.6.md:225-226` — *"adopted as an unconditional design rule for stage 1: inside the frame path, front-panel access uses **local variables**, never `Value` property nodes."*

Route (ii) is **unmeasured, not impossible**, and the project's own design rule points at it. This does not touch the probe's measurement of route (i) — it is load-bearing only for the judgement the probe explicitly hands off (`docs/d1-build-plan.md:153-158`), which is exactly where a false "impossible" does damage. Disposal is one sentence.

**(ii) Is every `ControlTerminal` a `panel_wiring` row? Two records disagree, and Q4 rests on the answer.**
- `docs/toolkit-capabilities.md:511-512` (cited by the probe): "fp_labels returns 114 and `report("ControlTerminal")` returns 114 — every front-panel object has exactly one diagram terminal in this VI."
- `archive/peer/2026-09-16-stop-condterm-panel-fail2.md:128-131`, an **accepted** disposition: "`panel_wiring` is NOT recursive … the unmatched second sink of wire 3457 is fully explained by an ordinary front-panel `ControlTerminal` belonging to a **tab-page-nested** control" — i.e. a ControlTerminal with no panel row.
- `tools/gscript.py:640` — "Not recursive: tab pages / cluster elements are not rows"; `fp_labels` walks the same `Panel.Controls[]` (`tools/gscript.py:2233-2235`), so 114 = 114 is two **non-recursive** counts agreeing, not a proven bijection.
- The newer resolution exists: `docs/d1-build-plan.md:259-263` — that second sink is **`#637`'s conditional terminal uid 648**, measured 2026-09-17 by `OpLoopEndRef_v0`. The tab-page explanation is superseded and the archive entry still reads as accepted.

Q4's claim that the changed row "NAMES which object moved" and "is the proof that the object moved was a real panel terminal" holds only if the chosen terminal has a row. Cite the 2026-09-17 resolution, or report Q4 rather than gate on it.

### A4 UNREAD EVIDENCE — `docs/stage2-plan.md:92-94` already names this exact route; only its first half is quoted.
The probe and `docs/d1-build-plan.md:148-151` cite `stage2-plan.md:90-94` for the read-once rule. The same sentence continues:

> "the stage-2 VI stops its loops from a Boolean read every iteration — **a local variable of `Stop` inside each loop, or the control's terminal moved into one loop and locals in the others**"

So "move the terminal into the loop" is not a candidate invented at `d1-build-plan.md:153`; it is the project's own written mechanism, paired with locals precisely because one terminal serves only one loop. Citing it costs a line and changes the framing from "three unsettled candidates" to "the planned mechanism, never measured".

## PART B — THE ARTIFACT

### B1 ALREADY BUILT — no new op is created. Clean.
`OpMoveIn_v0.vi` exists and is class-agnostic (uid → `UID to GObject Reference.vi` → `Move.reference`); `OpOwnerChain_v1`/`read_owner` is imported, not re-written; `ls tools/recipes | grep -i move` is `build_opmove` / `build_opmovebyindex` / `build_opmoveout` / `probe_move_into_v0`, none touching this class. `UID_LABEL = "UID 3"` matches STATUS OPEN 19b and `docs/d1-build-plan.md:216`.

### B2 ALREADY FAILED — no.
The sister probe's three deaths were all in the *build* of `OpMoveIn_v0` (`docs/d1-build-plan.md:190-194`), and this file does not rebuild it. The habit that killed run 3 — a fixed op path served from LabVIEW's memory (`STATUS.md` START-HERE 5) — applies to **editing** a VI at a fixed path; here the op is only run. Cleared.

### B3 HELPER EXISTS — two, both hand-rolled.

**(i) The 114-uid owner census re-derives what `report_all` returns in one run.** `report_all()` returns an `owner` field per object (`tools/gscript.py:291,:322`, from `report()`'s `Class Name 3` at `:281`), and the measured output shows it populated per ControlTerminal: `tools/bench/census_opwiresource_v5.log:24-43` — `class=ControlTerminal owner=TopLevelDiagram`. Terminals on the VI's top-level diagram report `TopLevelDiagram`; only rows whose owner class is `Diagram` can be inside a loop body. The probe fetches that field, prints it as a FACT, then still runs 114 op runs.

Consequence, not just cost: every op run against a main-VI-sized target carries ~0.99 s of fixed overhead (`docs/toolkit-capabilities.md:313-325`, "one bare op run, the MAIN VI 960.8 ms"), and the census has a **420 s budget with a `break`**. If truncation lands before the first `Diagram#639`-owned terminal, `inside` is empty, Q1b fails, and the run `return 1`s **without ever asking Q3** — the failure mode the sister probe spent two rounds eliminating. The pre-filter is free.

**(ii) `handles()` duplicates `tools/bench/bench_prep.py:64-71 labview_handles()`** byte for byte (same PowerShell string, same `int(... or 0)` fallback). This substitution was raised and accepted on the sister file (rev-4 finding B3, quoted in `tools/recipes/probe_move_into_v0.py`'s own `handles()` docstring; `archive/peer/2026-09-17-priorart-priorart-moveinto-rev6.md`), and the policy that reads the number sits beside it (`HANDLE_LIMIT` `:61`, restart `:74-79`). With STATUS OPEN 23 open at **51,530 handles**, the number this run reports should come from the reader the limit is stated against. One import line.

### B4 ALREADY MEASURED — Q1 only, and the probe cites it. Not slugged.
`ControlTerminal` 114: `tools/bench/probe_local_class.log:22` (2026-09-13) and `docs/toolkit-capabilities.md:511`. `panel_wiring` 114 rows: `tools/bench/diag_d1_step0.log:17` (G5). Two op runs on a fresh scratch copy is a legitimate re-assert. The **question** (Q3) is unmeasured.

## Checked and cleared — so the next round does not re-derive it

1. **The class is addressable and mutable by the generic op family, measured:** `tools/bench/diag_delete_matrix.log:115,:118` — `ControlTerminal open_panel=True 38 → 37 REMOVED ONE, err=(False,0,'')` — and `docs/toolkit-capabilities.md:531` says "Delete and Move behave identically" for the panel-open decline. Worth citing as the premise's support; it does not answer reparenting, so **not** a blocking slug.
2. **No reader maps a panel object to its `ControlTerminal` uid — the claim is correct.** `panel_wiring` returns the control's uid and the wire's uid, never the terminal's (`tools/gscript.py:637-639,:665-668`); `OpWireSource_v5`'s `read_terminal` returns each terminal's **owner** class/uid, not its own (`tools/recipes/build_opwiresource_v5.py:167-171`). Identification by effect is the right shape.
3. **`ControlTerminal` is a `Terminal`, not a `Node`** (`archive/peer/2026-09-14-dispI-controlterminal-route.md:22`), which is why the diagram tree and `net_map` cannot see it (`docs/toolkit-capabilities.md:494,:506-509`) and why an owner read is the right instrument.
4. **`archive/peer/2026-08-28-copy-nodes-between-vis.md:160`** ("do not assume copying only the terminal gives predictable front-panel placement") is about **cross-VI copy with `Duplicate?`**, not within-VI reparenting. Adjacent, not a refutation.
5. Invoke purge, `new_since`'s own index, identity echo, md5 before/after, scratch deleted in-run — all present in the shape the sister probe's rounds settled.

## Residual, deliberately NOT slugged (plan merit, not prior art)

`chosen = inside[0]` takes whatever the census finds first. If that terminal is **bare** (wire 0 before and after), Q4's `changed` list is empty and the run yields no identification while Q3 still passes — yet the docstring promises identification as the proof. `docs/d1-build-plan.md:139-145` already names six terminals known to be wired (`Auto-Reset` w9806, `Reset Tracking` w10312, `Z/dZ` w730, `Correction Factor` w6096, `min value` w17287, `Force … Extension` w10908); preferring an `inside` candidate whose panel row carries a wire costs nothing.

```
tools/recipes/probe_move_ctlterm_v0.py
PRIOR-ART: contradicted    (A3-i — docs/toolkit-capabilities.md:254 vs :263, docs/NAMES.md:246, archive/peer/2026-09-14-implicit-property-node-linked-object.md:28-29, docs/restructure-plan-4.6.md:225-226,:242-243 — covers ONLY the "no Local creator" parenthetical and d1-build-plan §0d route (ii))
PRIOR-ART: contradicted    (A3-ii — docs/toolkit-capabilities.md:511-512 vs archive/peer/2026-09-16-stop-condterm-panel-fail2.md:128-131 and tools/gscript.py:640, resolved by docs/d1-build-plan.md:259-263 — covers Q4's identification premise)
PRIOR-ART: unread-evidence (A4 — docs/stage2-plan.md:92-94 names "the control's terminal moved into one loop and locals in the others"; only :90-91 is quoted)
PRIOR-ART: helper-exists   (B3-i — tools/gscript.py:291,:322,:281 + tools/bench/census_opwiresource_v5.log:24-43: report_all already returns each ControlTerminal's OWNER CLASS in one run; the 114-run census under a 420 s break can end the run at Q1b without asking Q3)
PRIOR-ART: helper-exists   (B3-ii — tools/bench/bench_prep.py:64-71,:61: handles() duplicates labview_handles(), the reader STATUS OPEN 23's 51,530 is stated against)
```

None of the five stops the *measurement* — Q3 as written still answers whether `GObject.Move` reparents a `ControlTerminal`. Four are one-line disposals (a citation, a filter, an import); A3-ii is the one that changes what Q4 may claim.

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-17 by the MATERIAL session `cycle15-d1-build`. **5 findings, 0 novel — ALL FIVE ACCEPTED AND
FIXED in the same turn; none refuted, none escalated.** The reviewer's own summary holds: *"none of the five stops
the measurement"*, so the probe still asks the question it was written for. Files edited:
`tools/recipes/probe_move_ctlterm_v0.py` (now **REV 2**) and `docs/d1-build-plan.md` §0d.

**FIXED: `A4` `unread-evidence` — the most valuable finding, and it changes the framing rather than the code.**
Rev 1 quoted only `docs/stage2-plan.md:90-91`. The same sentence continues at `:92-94`: *"a local variable of
`Stop` inside each loop, **or the control's terminal moved into one loop and locals in the others**."* So moving
the terminal is **this project's own written mechanism, never measured**, not a candidate invented for D1. Both
the probe's docstring and §0d now say that and cite `:92-94`.

**FIXED: `A3-i` `contradicted` — a false "impossible" that I wrote, caught exactly where CLAUDE.md says to look
for one.** Rev 1 and §0d dismissed route (ii) with *"no Local creator (`toolkit-capabilities.md:254`)"*. That line
is about creating **front-panel objects**, not `Local` NODES. The citation is **withdrawn** in both files and
replaced by what our own files actually say: `toolkit-capabilities.md:263` (`Local` is a valid Traverse class, 8
in this VI), `NAMES.md:246` (`Local.Control Name` **6355400**) with `archive/peer/2026-09-14-implicit-property-
node-linked-object.md:28-29` recording it **read/write**, `restructure-plan-4.6.md:242-243` (copy from a donor is
the route for a node the fleet cannot create), and — decisively — `restructure-plan-4.6.md:225-226`, which already
**adopts** locals for front-panel access inside the frame path. §0d now reads "UNMEASURED, NOT IMPOSSIBLE".

**FIXED: `A3-ii` `contradicted` — Q4 no longer gates on identification.** "Every `ControlTerminal` is a
`panel_wiring` row" is two **non-recursive** counts agreeing (`tools/gscript.py:640`: tab pages and cluster
elements are not rows), so a chosen terminal may have no row. Q4 now **reports** which object moved instead of
gating on it, the probe moves **up to three** `Diagram#639` terminals so a changed row is likely rather than
assumed, and "no row changed" is printed as a fact. The same caveat is recorded in §0d. (The reviewer is also
right that `archive/peer/2026-09-16-stop-condterm-panel-fail2.md`'s tab-page explanation is **superseded** by the
2026-09-17 `OpLoopEndRef_v0` measurement — that unmatched sink is `#637`'s conditional terminal uid 648. Noted
here; editing that older archive entry is not this disposition's business.)

**FIXED: `B3-i` `helper-exists` — and it was a latent run-killer, not just waste.** `report_all()` already returns
each object's OWNER CLASS in one run (`tools/gscript.py:281,:291,:322`; measured per ControlTerminal in
`tools/bench/census_opwiresource_v5.log:24-43` as `owner=TopLevelDiagram`). Rev 2 pre-filters on that field for
free and runs the ~1 s owner-chain reads only on non-`TopLevelDiagram` rows. The consequence the reviewer names is
the real reason: at ~0.99 s fixed overhead per op run on a main-VI-sized target, rev 1's 420 s budget could
truncate before the first `Diagram#639` hit, fail Q1b and `return 1` **without ever asking Q3**.

**FIXED: `B3-ii` `helper-exists`.** `handles()` now imports `bench_prep.labview_handles()` instead of repeating
its PowerShell string, so the number comes from the reader `HANDLE_LIMIT` and STATUS OPEN 23 are stated against.

**Also folded in from "checked and cleared"** (not slugs, but they support the premise and save the next round):
`tools/bench/diag_delete_matrix.log:115,:118` — a `ControlTerminal` was **deleted by index** with the panel open,
38 → 37, and `toolkit-capabilities.md:531` records Delete and Move behaving identically; and the confirmation that
no reader maps a panel object to its terminal uid, which is why identification is by effect.

**Residual, accepted as stated:** the reviewer flagged (without slugging it) that `chosen = inside[0]` might pick
a bare terminal and yield no identification. That is exactly what the up-to-three-candidate loop above addresses.

FIXED: contradicted - docs/d1-build-plan.md:153 - A3-i: the "no Local creator (`toolkit-capabilities.md:254`)" citation is WITHDRAWN and route (ii) now reads "UNMEASURED, NOT IMPOSSIBLE", citing `:263`, `NAMES.md:246` and `restructure-plan-4.6.md:225-226,:242-243`.
FIXED: contradicted - tools/recipes/probe_move_ctlterm_v0.py:124 - A3-ii: Q4 no longer GATES on identification - it reports which object moved, moves up to three candidates so a changed panel row is likely, and records the non-recursive `Panel.Controls[]` caveat (`gscript.py:640`).
FIXED: unread-evidence - docs/d1-build-plan.md:147 - A4: `docs/stage2-plan.md:92-94` is now quoted in full ("or the control's terminal moved into one loop and locals in the others"), so this is the project's own written mechanism, never measured, rather than three invented candidates.
FIXED: helper-exists - tools/recipes/probe_move_ctlterm_v0.py:259 - B3-i: the 114-run owner census is replaced by `report_all`'s free owner-CLASS pre-filter, so the ~1 s owner-chain reads run only on non-`TopLevelDiagram` rows and the 420 s budget can no longer truncate before Q3 is asked.
FIXED: helper-exists - tools/recipes/probe_move_ctlterm_v0.py:176 - B3-ii: `handles()` now imports `bench_prep.labview_handles()` instead of repeating its PowerShell string, so the number comes from the reader `HANDLE_LIMIT` is stated against.
