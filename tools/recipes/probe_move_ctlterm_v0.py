r"""probe_move_ctlterm_v0.py - D1's SECOND relocation unknown: can a FRONT-PANEL CONTROL TERMINAL be reparented?

WHY THIS EXISTS, and why it is a separate run rather than a step of the D1 build. Step 0's census
(`tools/bench/diag_d1_step0.log`, `docs/d1-build-plan.md` s0d) measured that at least SIX front-panel objects have
their diagram terminal INSIDE the frame loop body and are read or written by nodes that must move to the new
tracking loop: controls `Auto-Reset` #17472 (w9806 -> #9647), `Reset Tracking` #5605 (w10312 -> #10247), `Z/dZ` #47
(w730 -> #2222), `Correction Factor` #9289 (w6096 -> #2222), and indicators `min value` #17257 (w17287 <- #10969,
read back by the implicit property #17289) and `Force (pN) vs Extension (nm) ` #8038 (w10908 <- #11261).

These terminals are inside `Diagram#639` on purpose: a Boolean wired in from OUTSIDE a loop is read ONCE, which
is NI's infinite-loop mistake. So routing `Reset Tracking` into the new loop through a tunnel would change WHEN
it is read, and the user flips it during a run - a computation change, not scheduling (rule 1a).

REV 2, after `archive/peer/2026-09-17-priorart-ctlterm-move.md` (5 findings, 0 novel; "none of the five stops the
measurement"). All five are folded in here:

  * **A4 - THIS IS THE PROJECT'S OWN WRITTEN MECHANISM, not a candidate invented for D1.** Rev 1 quoted only the
    first half of `docs/stage2-plan.md:90-94`. The same sentence continues: *"the stage-2 VI stops its loops from
    a Boolean read every iteration - a local variable of `Stop` inside each loop, **or the control's terminal
    moved into one loop and locals in the others**"*. So the framing is "the planned mechanism, never measured",
    and that is exactly what this file measures.
  * **A3-i - the "no Local creator" dismissal was WRONG and is withdrawn.** `docs/toolkit-capabilities.md:254` is
    about creating *front-panel objects*, not `Local` NODES. Against it: `:263` lists `Local` as a valid Traverse
    class (8 in this VI); `docs/NAMES.md:246` gives `Local.Control Name` **6355400**, recorded **read/write** in
    `archive/peer/2026-09-14-implicit-property-node-linked-object.md:28-29`; `docs/restructure-plan-4.6.md:242-243`
    records copy-from-a-donor as the route for a node the fleet cannot create; and `:225-226` adopts
    *"inside the frame path, front-panel access uses **local variables**, never `Value` property nodes"* as an
    unconditional design rule. Route (ii) is **UNMEASURED, NOT IMPOSSIBLE** — the exact kind of false "impossible"
    CLAUDE.md's trigger sentence exists to stop.
  * **A3-ii - Q4 may no longer GATE on identification.** "Every ControlTerminal is a `panel_wiring` row" rests on
    two **non-recursive** counts agreeing (`tools/gscript.py:640`: tab pages and cluster elements are not rows),
    so a chosen terminal may have no panel row. Q4 is therefore **reported, not gated**, and the run tries up to
    three candidates so identification is likely rather than assumed.
  * **B3-i - the 114-run owner census is replaced by a free pre-filter.** `report_all()` already returns each
    object's OWNER CLASS in one run (`tools/gscript.py:281,:291,:322`; measured per ControlTerminal in
    `tools/bench/census_opwiresource_v5.log:24-43`, `owner=TopLevelDiagram`). Only rows whose owner class is
    `Diagram` can be inside a loop body, so the owner-chain reads run on those alone. This is not just cost: at
    ~0.99 s of fixed overhead per op run on a main-VI-sized target (`toolkit-capabilities.md:313-325`), rev 1's
    420 s budget could truncate before the first `Diagram#639` hit, fail Q1b and `return 1` **without ever asking
    Q3** — the failure mode the sister probe spent two rounds eliminating.
  * **B3-ii - `handles()` is `bench_prep.labview_handles()`**, imported rather than re-typed, so the number is
    read by the reader `HANDLE_LIMIT` and STATUS OPEN 23 are stated against (`tools/bench/bench_prep.py:61,:64-71`).

Also cited, from the review's "checked and cleared": the class is addressable by this op family — a
`ControlTerminal` was DELETED by index with the panel open, `38 -> 37`, `tools/bench/diag_delete_matrix.log:115,:118`,
and `toolkit-capabilities.md:531` records Delete and Move behaving identically. That supports the premise; it does
not answer reparenting.

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
object - confirmed by the review: `panel_wiring` returns the CONTROL's uid and the WIRE's uid, never the
terminal's (`tools/gscript.py:637-639,:665-668`), and `OpWireSource_v5`'s `read_terminal` returns each terminal's
OWNER, not its own uid (`build_opwiresource_v5.py:167-171`). But phase P measured that a move CUTS the wires that
crossed the old border (Wire 1902 -> 1895), so the control whose `panel_wiring` row loses its wire IS the one
whose terminal moved. ⚠️ **That identification is REPORTED, never gated** (rev-2 finding A3-ii): a chosen terminal
may have no panel row at all, since `panel_wiring` and `fp_labels` walk the same NON-recursive `Panel.Controls[]`
(`gscript.py:640`), so "114 == 114" is two non-recursive counts agreeing rather than a proven bijection.

PREDICTION CONTRACT
  Q0a/Q0b  the original's md5 is 2a78e17c449cacdaf5da389818526859 before AND after.
  Q1   `report_all(MAIN, 'ControlTerminal')` returns 114 objects (toolkit-capabilities.md:511) and
       `panel_wiring(MAIN)` returns 114 rows.
  Q1b  after the free `report_all` owner-CLASS pre-filter, the owner-chain reads find at least one ControlTerminal
       whose owner is `Diagram#639` (the frame loop body) - step 0 measured six panel objects wired to nodes on
       that diagram, so 0 would falsify step 0. The owner-class distribution is reported, not predicted.
  Q2a  a While loop is created on `Diagram#686` (the holder of #637): +1 Diagram, +1 WhileLoop.
  Q2   CONTROL ARM - `#8885 Multiply` reparents into the new body diagram, exactly as phase P's P2 did. A failure
       here makes the run INVALID and it STOPS; nothing is concluded about ControlTerminal.
  Q3   THE QUESTION - the chosen `ControlTerminal` reparents: `ownerchain(term)` -> the new body diagram, and the
       VI's total `ControlTerminal` count is UNCHANGED at 114 (the terminal was moved, not destroyed).
  Q4   `panel_wiring` still returns 114 rows and every label is still present - the panel object SURVIVED. Which
       object moved is **reported, not gated** (A3-ii): up to three `Diagram#639` terminals are moved so that a
       changed row is likely, and "no row changed" is printed as a fact, not scored as a failure.
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
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
from bench_prep import labview_handles  # noqa: E402  - rev2 B3-ii: the reader HANDLE_LIMIT is stated against
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
    """rev2 B3-ii: `bench_prep.labview_handles()` verbatim rather than a second copy of the same PowerShell
    string - it is the reader `HANDLE_LIMIT` (bench_prep.py:61) and STATUS OPEN 23's 51,530 are stated against."""
    return labview_handles()


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
        from collections import Counter
        dist = Counter(str(c.get("owner", "")) for c in cts)
        fact(f"report_all('ControlTerminal') returned {len(cts)} objects; owner-class distribution {dict(dist)}")
        # rev2 B3-i: the FREE pre-filter. `report_all` already carries each object's owner CLASS, and a terminal
        # on the VI's top-level diagram reports `TopLevelDiagram` (measured, census_opwiresource_v5.log:24-43).
        # Only a `Diagram` owner can be a loop body, so the ~1 s/row owner-chain reads run on those alone -
        # which is also what stops the 420 s budget from truncating before the first hit and failing Q1b
        # without ever asking Q3.
        cand = [c for c in cts if str(c.get("owner", "")) not in ("TopLevelDiagram", "")]
        fact(f"pre-filter: {len(cand)} of {len(cts)} ControlTerminals have a non-TopLevelDiagram owner class - "
             f"only these get an owner-chain read")
        t0 = time.time()
        inside = []
        for c in cand:
            if time.time() - t0 > 420:
                fact(f"owner census budget reached after {len(owners)} of {len(cand)}")
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
        fact(f"a ControlTerminal's OWNER class(es), measured by owner chain: {oclasses}")
        fact(f"{len(inside)} ControlTerminal(s) are owned by Diagram#{FRAME_BODY_UID} (the frame loop body): "
             f"{inside[:20]}")
        if not gate("Q1b at least one ControlTerminal sits inside the frame loop body", bool(inside),
                    f"{len(inside)} found; owner-chain reads covered {len(owners)}/{len(cand)} candidates"):
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

        # --- Q4: the panel object survived; WHICH one moved is REPORTED, not gated (A3-ii) ---
        # Up to three candidates are moved so a changed row is LIKELY: a chosen terminal can legitimately be bare,
        # or belong to a tab-page-nested control that `panel_wiring` does not list at all (gscript.py:640), and in
        # either case no row changes while Q3's answer about the CLASS is unaffected.
        before_by = {(r["uid"], r["label"]): r["wire"] for r in panel_before}
        moved = [chosen]
        panel_after = g.panel_wiring(SCRATCH)
        after_by = {(r["uid"], r["label"]): r["wire"] for r in panel_after}
        changed = [(k, before_by[k], after_by.get(k)) for k in before_by if after_by.get(k) != before_by[k]]
        for extra in inside[1:3]:
            if changed:
                break
            fact(f"no panel row changed yet - moving a second/third candidate ControlTerminal #{extra} "
                 f"(identification only; Q3 is already answered)")
            move_in(SCRATCH, extra, body_i, (60, 600 + 120 * len(moved)))
            moved.append(extra)
            panel_after = g.panel_wiring(SCRATCH)
            after_by = {(r["uid"], r["label"]): r["wire"] for r in panel_after}
            changed = [(k, before_by[k], after_by.get(k)) for k in before_by if after_by.get(k) != before_by[k]]
        gate("Q4 the panel still has 114 objects and every label survives",
             len(panel_after) == N_PANEL and set(before_by) == set(after_by),
             f"{len(panel_after)} rows; labels lost {sorted(set(before_by) - set(after_by))[:5]}")
        fact(f"moved ControlTerminal uid(s) {moved}; panel rows whose connected wire changed "
             f"(this NAMES the object(s) whose terminal moved, or is EMPTY if they are bare / tab-nested): "
             f"{changed}")

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
