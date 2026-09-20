r"""diag_d1_full_route.py - the ONE thing PHASE "full" is actually blocked on, measured.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/diag_d1_full_route.log \
        -- py -u tools/recipes/diag_d1_full_route.py

REWRITTEN 2026-09-17 after its own prior-art review, `archive/peer/2026-09-17-priorart-d1-full-route.md`
(ANSWERED, 6 findings, 0 novel, ALL ACCEPTED, none refuted; disposition in that file). The first draft asked
three questions this project had already answered and missed the one it had not:

  * A3-i CONTRADICTED my load-bearing sentence "`wire()` is the only fleet writer that reaches a nested diagram,
    and it addresses terminals BY NAME". WITHDRAWN. `wire_sr` addresses `Terminals[term_index]` of
    `Nodes[node_index]` INSIDE the loop body by INDEX (`tools/gscript.py:523-528`, "indices, never names" -
    `docs/toolkit-capabilities.md:42`), and so does `OpStopFromNode_v0` (`:51`, `index 3` = body `Nodes[]`,
    `index 4` = `Terminals[]`). `connect2`'s SINK side reaches any diagram by index (`gscript.py:2429-2431`).
  * B3 HELPER-EXISTS: the 19 empty-named cut terminals are NOT an addressing problem. `build_d1_v0.json` already
    stores `[node_uid, term_index, name, is_source, wire]`, so the INDEX is in the record, and the project's own
    rule already says to use it (`archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md:129`). `#5540`'s nine
    "duplicate" names are outer/inner PAIRS disambiguated by `is_source` (`docs/frame-loop-wire-graph.md:17`).
  * B4 ALREADY-MEASURED: an unnamed terminal has been wired by this fleet TWICE
    (`docs/toolkit-capabilities.md:35`, wire 346 both ends, ExecState 0->1; `docs/keystone-op-spec.md:577-586`,
    `connect2` onto Decimate's unnamed outputs INSIDE the P=4 loop). The old R3 is DELETED. So is T5sep: it
    re-derives a standing rule, `docs/NAMES.md:788` "Never gate on ExecState while a required input is still
    unwired - it cannot discriminate". T6sep is KEPT, as a CONTROL only, which B4's own scope note releases
    (`docs/toolkit-capabilities.md:213`).
  * A1 SETTLED-ALREADY: the wire->source join already exists and PASSED - `tools/bench/diag_d1_step0.py:357-358,
    :440-457,:631` -> `d1_step0_census.json.resolved_boundary` (91/91, `diag_d1_step0.log:18,:59`), which stores
    the driving object AND every sink. The old R1 is DELETED as new code; P1 below is the remainder A1's scope
    note leaves open - JOINING that stored resolution to the post-run-5 82-wire cut set.
  * A3-ii CONTRADICTED "PHASE 'full' is not executable as written". WITHDRAWN: `build_d1_v0.py:37-39` records
    that the re-wiring's ops all EXIST and are verified (pattern `build_track_v6_queue.py`, 162/162) and are
    merely UNWRITTEN. The RECORDED blocker is elsewhere, and this run goes there instead.

THE RECORDED BLOCKER, and the run it buys (P2)
-----------------------------------------------
`archive/2026-09-17-status-d1-phase-full-narrative.md:141-147` = STATUS OPEN 28: the end-of-stream sentinel test
needs a COMPARISON PRIMITIVE and the LITERALS beside it INSIDE each new loop body. The original already contains
`Equal?` (#10019, #22284) and the donor constants (`opconstvaluen_scan.json`: 0 x69, 1 x36, 20 x2, -1 x1 = uid
4609, 25 x1), so the route is `copy_by_index` + `move_in`.

REV 3, after the SECOND prior-art review (`archive/peer/2026-09-17-priorart-d1-full-route-rev2.md`, ANSWERED, 8
findings, 0 novel, ALL ACCEPTED - disposition in that file). It dismantled three premises of REV 2:

  * A3: "`copy_*` from vi.lib / an NI example is a recorded crash" - WITHDRAWN. The recorded prohibition is
    **vi.lib only** (`docs/keystone-op-spec.md:136-143`, about an Erdos Miller file); an NI-EXAMPLE donor is
    recorded WORKING twice through `copy_by_index` itself (`build_opconstvalue_v1.py:39,:169,:199`,
    `build_opconstvalue_v1.log:21-25,:45-49`). So donor==target was never forced.
  * B2: **`donor == target` is dropped.** A second, separately named copy of the original is an ordinary
    claudeDev donor (rule 1: copies are always fine), keeps `copy_by_index` in its recorded shape, and clears its
    only same-file guard trivially (`gscript.py:1313-1314` refuses identical PATHS).
  * A4: "s11f.2 AUTHORISES exactly this" - WITHDRAWN. s11f.2 (`docs/d1-build-plan.md:652-654`) authorises the
    OBJECTIVE and orders "`OpConstValue`/`build_case` FIRST, additive builds only where those cannot produce the
    node". **That first clause is DISCHARGED IN WRITING here**, as the review required: `OpConstValue_v1` and
    `OpConstValueN_v1` are READERS of `Constant.Value` 634AC00 and create nothing
    (`docs/toolkit-capabilities.md:46-47`); `build_case` creates a Case on the TOP-LEVEL diagram from a
    front-panel selector by NAME (`gscript.py:2616-2625`). Neither can produce a comparison primitive or a
    diagram constant inside a loop body, so the fallback clause is reached on the record. **Which fallback to
    take is still JUDGEMENT**, and `copy_by_index` is not an "additive build" - so P2 below runs it as a
    MEASUREMENT, never as a build commitment.
  * A5: `restore_move_fixtures()` in a `finally` - REMOVED. `gscript.py:1268-1272` forbids it outright
    ("never in a finally while a VI may still be in memory"); `copy_by_index` already restores at the START of
    every call (`:1320`), which is the sanctioned placement.

WHAT ALREADY EXISTS - checked before a line was written, and widened by review finding A4
------------------------------------------------------------------------------------------
  * `tools/bench/diag_d1_step0.py` (+ `--offline`) - the script that PRODUCED `.resolved_boundary`; its stored
    value is the driving object PLUS every sink (`:454-456`). A4.1.
  * `tools/bench/wiregraph_frame_loop.py:57-63` - the same join per diagram, already gating one-source-per-wire
    (`:68`) and already documenting the unresolved-half-edge gap (`:66-67`). A4.2.
  * `docs/d1-build-plan.md:496-511` (`#5058`'s 16 terminals WITH the other end AND its D1 carrier), `:377-389`
    (all 14 shift registers), `:402-410` (the control terminals), `:537-556` (the queues). A4.3 - and its point
    that matters most: for most cut nets the D1 carrier is a QUEUE or a NEW TUNNEL, not the original's source.
  * `tools/recipes/build_track_v6_queue.py` (162/162) - named at `build_d1_v0.py:39` as the pattern for the
    re-wiring. A4.4.
  * `copy_by_index` = `OpMoveByIndex_v0` (`gscript.py:1282-1361`), `move_in` = `probe_move_ctlterm_v0.py:160-178`
    (12/0, 9/0), `wire_source` = `build_opstopfromnode_v0.py:350-388`, `OpStopFromNode_v0`
    (`toolkit-capabilities.md:51`, 20/2), `build_track_v6_core.walk`. All imported or re-used verbatim.

PREDICTION CONTRACT
-------------------
 P0  original md5 2a78e17c449cacdaf5da389818526859 BEFORE; OpMoveIn_v0 / OpWireSource_v5 / OpStopFromNode_v0 /
     OpMoveByIndex_v0 present; handles recorded.
 P1  OFFLINE, no new join: `d1_step0_census.json.resolved_boundary` is joined to the 82 cut wires of
     `build_d1_v0.json`. Reported: how many of the 82 the EXISTING resolution already covers, and which it does
     not. Not a pass/fail - the two sets were never claimed identical (A1's scope note).
 P1b **DELETED (rev3 A1/A2).** w3268 was resolved from the machine on 2026-09-16 with THIS SAME op, on the
     original, read-only, md5 unchanged - `tools/bench/diag_autofocus_border.log:19-26`, published at
     `docs/camera-acquisition-facts.md:225-230`:
         wire 3268 driven by ('Diagram', 639); sinks [Function 2136, SelectorTunnel 3045, LoopTunnel 2213,
         Function 10068, SubVI 1114]
     So the re-wire source map is COMPLETE at **82/82 with no LabVIEW run at all** (81 from P1's offline join +
     this). My prediction was backwards on BOTH halves: there IS a source terminal, and its owner is
     **`Diagram` 639**, not `WhileLoop #637` - so the rule-1a hazard I was carrying ("`#376`'s `frame index` is
     the frame loop's iteration terminal `i`, and 1.7's own `i` counts WRITER iterations") is **REFUTED before
     it was tested**. A `Diagram`-owned source terminal is the CONTROL-TERMINAL signature and a constant on the
     same diagram looks identical, so the label comes from `panel_wiring`
     (`docs/camera-acquisition-facts.md:235-237`). Two cheap remainders A1's scope note releases, NOT done here:
     (a) which diagram-owned object drives w3268 - one `panel_wiring` label read;
     (b) a re-run at `max_terms=8` - `diag_autofocus_border.py:62` read only `range(6)` while
         `docs/frame-loop-wire-graph.md:151` names six sinks, so the sink list is incomplete, not the source.
 T6  CONTROL for that same reader: `wire_source(copy, 10850)` must reproduce its published answer - exactly one
     source, owner `DigitalNumericConstant #10739` (`toolkit-capabilities.md:48`, `diag_d1_step0.log:21-22`).
     If the control fails, P1b concludes NOTHING (`toolkit-capabilities.md:213`).
 P2  THE THREE THINGS THE TWO REVIEWS LEFT GENUINELY UNRECORDED. Everything else they showed was already on file.
     P2a  **THE DISCRIMINATOR** (rev2 A1's "one line of code ... the measurement this run should buy"). The
          precondition `copy_by_index` needs (`gscript.py:1351-1354`: the Target must be ExecState 1) is on
          record BOTH ways, on a byte-copy of this same original on the same morning - **1** in
          `drive_original_copy_v3.log:9-12` (GetVIReference -> OpenFrontPanel(False,1) -> ~1.3 s -> read) and
          **0** in `build_d1_v0_run5.log:13-16` (`open_panel` then `exec_state` six lines later). Rev2 A2 also
          withdrew the word meant to explain it: `d1-build-plan.md:203` says "reads ExecState 0 when opened
          HEADLESSLY", but `build_d1_v0.py:413` HAD THE PANEL OPEN. So ONE copy is read at THREE points - after
          `GetVIReference`, immediately after `OpenFrontPanel(False)`, and after a settle. Three numbers are
          reported; the gate is only that all three reads completed.
     P2b  `copy_by_index(donor=A SECOND, SEPARATELY NAMED COPY, 'DigitalNumericConstant', idx(4609),
          target=copy, expect_uid=4609)` - the -1 sentinel literal, the half with NO required inputs (rev2 B2:
          donor==target is dropped; a second copy is an ordinary claudeDev donor). Predicted: exactly one new
          GObject; `DigitalNumericConstant` 180 -> 181; no panel object.
     P2c  one new While loop on Diagram#686, and `move_in` of the COPIED constant into its body. ⚠️ Rev2 B1: the
          owner-chain half is ALREADY MEASURED - run 5 did it three times for `#3529`/`#3560`/`#3447`
          (`build_d1_v0_run5.log:100-109`), with `ControlTerminal` still 114. **The only untested variable is
          PROVENANCE** - a freshly COPIED constant rather than one the VI already owned - and the gate says so.
     P2d  the COMPARISON half is NOT attempted, and per rev2 B3 this is a RESTATEMENT of
          `build_d1_v0.py:40-47,:844-847`, not a discovery: a comparison primitive has two REQUIRED inputs,
          `copy_by_index` will not save a broken Target, `create_control` ADDS A PANEL CONTROL (breaking the
          plan's own "ControlTerminal still 114"), and `Terminal.Create Constant` 6349C00 is catalogued only.
          Two routes rev2 B3 adds are recorded as ROUTES TO PRICE, NOT BUILDS TO START (both are new/additive
          ops; `cycle15-plan.md:104`'s freeze governs): (1) `Constant.Terminal` **634AC04** + `Terminal.Connect
          Wire` **6349C03** - a copied constant feeding a copied primitive's required input, creating NO panel
          object; (2) the erdosmiller `Create Equal.vi` / `Create Constant.vi` creators, already censused
          terminal by terminal (`archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:9-10`), wrapped by
          the `queue_node` pattern (`gscript.py:928-934`, "places one queue primitive on any diagram", 162/162).
          Choosing among them is JUDGEMENT -> OPEN, not taken here (CLAUDE.md s3).
 P3  original md5 unchanged AFTER; every working copy deleted in this same run; handles after.

FAILURE BUDGET 2 (CLAUDE.md s3). No repair pass inside the run.
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
import gscript as g                                      # noqa: E402
import build_track_v6_core as B                          # noqa: E402
from bench_prep import labview_handles                   # noqa: E402
from build_opownerchain_v1 import read_owner             # noqa: E402
from build_opownerchain_v1 import OP as OP_OWNER         # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = g.CLAUDEDEV
RUN_STAMP = time.strftime("%H%M%S")
# A UNIQUE working-copy name PER STAGE. `copy_by_index` OVERWRITES its `target` file from MOVE_DST
# (gscript.py:1360) while LabVIEW may still hold the old path resident - the project's recorded
# stale-in-memory-VI failure class (`archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md`, STATUS "START
# HERE" 4). Each stage therefore continues on a FRESH filename and the previous one is never opened again.
T0 = os.path.join(CLAUDEDEV, f"D1_route_{RUN_STAMP}_a.vi")
T1 = os.path.join(CLAUDEDEV, f"D1_route_{RUN_STAMP}_b.vi")
# rev2 B2: the DONOR is a second, separately named copy of the original - an ordinary claudeDev donor (CLAUDE.md
# rule 1: copies are always fine). This keeps `copy_by_index` in its recorded shape and clears its only same-file
# guard trivially (`gscript.py:1313-1314` refuses identical PATHS, not identical contents).
TDONOR = os.path.join(CLAUDEDEV, f"D1_route_{RUN_STAMP}_donor.vi")
STAGES = [T0, T1, TDONOR]
OPIN = os.path.join(CLAUDEDEV, "OpMoveIn_v0.vi")
OPWSRC = os.path.join(CLAUDEDEV, "OpWireSource_v5.vi")
OPSTOP = os.path.join(CLAUDEDEV, "OpStopFromNode_v0.vi")
OPMBI = os.path.join(CLAUDEDEV, "OpMoveByIndex_v0.vi")
UID_LABEL = "UID 3"
LABELS = os.path.join(BENCH, "opwiresource_v5_labels.json")
OUT = os.path.join(BENCH, "diag_d1_full_route.json")

# rev3 B1 (`already-failed`): a `copy_by_index` session MUST start on a fresh LabVIEW instance, or it hits the
# recorded Errno 22 (`build_track_v6_queue.py:105-114`, `gscript.py:1304-1307`). This flag is the mechanical
# refusal: P2 stops unless a restart has actually happened in THIS process. Set it where lv_restart.py is called.
FRESH_INSTANCE_DONE = False

SIBLING_DIAG_UID = 686          # the FlatSequenceFrame diagram that HOLDS WhileLoop #637
CONST_MINUS1_UID = 4609         # CONST_DONORS[-1] in build_d1_v0.py, from opconstvaluen_scan.json
EQUAL_UID = 10019               # `x = y?` on the stop path (d1-build-plan.md s4)
BEFORE_COUNTS = dict(DigitalNumericConstant=180, ControlTerminal=114, Local=8, WhileLoop=3, Diagram=170)

passes, fails, facts = [], [], []
_OL = None
_WSRC_LABELS = None


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


def jload(name):
    with open(os.path.join(BENCH, name), encoding="utf-8") as f:
        return json.load(f)


def move_in(target, uid, dest_diagram_index, position):
    """probe_move_ctlterm_v0.py:160-178 verbatim (build_d1_v0.py carries the same copy)."""
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


def owner_of(target, uid):
    global _OL
    if _OL is None:
        with open(LABELS, encoding="utf-8") as f:
            _OL = json.load(f)
    import build_opownerchain_v1 as OB
    vi = g.op(OP_OWNER)
    saved = OB.MAIN
    try:
        OB.MAIN = target
        r = read_owner(vi, _OL, uid)
    finally:
        OB.MAIN = saved
    return r["ownercls"], r["owner_uid"]


def wire_source(target, wire_uid, max_terms=8):
    """build_opstopfromnode_v0.py:350-388 verbatim."""
    global _WSRC_LABELS
    if _WSRC_LABELS is None:
        with open(LABELS, encoding="utf-8") as f:
            _WSRC_LABELS = json.load(f)
    lab = _WSRC_LABELS
    wires = [o["uid"] for o in g.report_all(target, "Wire")]
    if wire_uid not in wires:
        return [], "wire uid not in report_all('Wire')"
    wi = wires.index(wire_uid)
    vi = g.op(OPWSRC)
    out, stop = [], ""
    for t in range(max_terms):
        vi.SetControlValue(lab["owner_uid"], 0)
        vi.SetControlValue(lab["is_source"], False)
        vi.SetControlValue(lab["recip_wire"], 0)
        vi.SetControlValue(lab["cls_back"], "POISON")
        vi.SetControlValue("vi path", target)
        vi.SetControlValue("Class Name", "Wire")
        vi.SetControlValue("index", int(wi))
        vi.SetControlValue(lab["term_index"], int(t))
        try:
            g._run(vi)
        except Exception as e:
            stop = f"EXC at t{t}: {str(e)[:80]}"
            break
        errs = " ".join(x for x in (g._err(vi, lab[k]) or "" for k in ("errS", "errWU", "errG")) if x)
        if errs:
            stop = f"error column at t{t}: {errs[:90]}"
            break
        out.append(dict(term=t, is_source=bool(vi.GetControlValue(lab["is_source"])),
                        recip=int(vi.GetControlValue(lab["recip_wire"])),
                        owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                        owner_cls=vi.GetControlValue(lab["cls_back"])))
    return out, stop


def diag_index(target, uid):
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


def traverse_index(target, uid, candidates=("DigitalNumericConstant", "Comparison", "Function", "CaseStructure",
                                            "SubVI", "IndexArray", "ForLoop", "Node")):
    # `Comparison` added after rev2 B3: it is the class our own files record for `x=y?` / `x<y?`
    # (`docs/toolkit-capabilities.md:48`, "sink `Comparison` 10950"). Without it P2d would have reported
    # None[None] for `Equal?` #10019 and a LOOKUP FAILURE would have been read as a design finding.
    for cls in candidates:
        try:
            order = [o["uid"] for o in g.report_all(target, cls)]
        except Exception:
            continue
        if uid in order:
            return cls, order.index(uid)
    return None, None


# ============================================================================== P1 (offline) - a JOIN, not a join
def p1():
    print("\n=== P1: join the EXISTING resolution (`d1_step0_census.json.resolved_boundary`) to the 82 cut wires",
          flush=True)
    cut = jload("build_d1_v0.json")["cut"]
    cut_wires = sorted({c[4] for c in cut})
    cen = jload("d1_step0_census.json")
    rb = {int(k): v for k, v in cen.get("resolved_boundary", {}).items()}
    fact(f"the stored resolution covers {len(rb)} boundary wires (diag_d1_step0.log:18 recorded 91/91 on the "
         f"step-0 subject set); the post-run-5 cut set is {len(cut_wires)} wires")
    covered = [w for w in cut_wires if w in rb]
    missing = [w for w in cut_wires if w not in rb]
    kinds = {}
    for w in covered:
        k = rb[w].get("kind", "?")
        kinds[k] = kinds.get(k, 0) + 1
    fact(f"P1 covered {len(covered)}/{len(cut_wires)} by kind: {kinds}")
    fact(f"P1 NOT covered by the stored resolution ({len(missing)}): {missing}")
    # B3: the addressing MODE of each cut terminal, from the record's own term_index + is_source.
    by_mode = dict(name=0, index=0)
    idx_rows = []
    terms_by_uid = {}
    for _di, rec in jload("main_vi_nodeterms.json")["diagrams"].items():
        for n in rec.get("nodes", []):
            terms_by_uid[n.get("uid")] = n.get("terms", [])
    for uid, i, nm, src, w in cut:
        same = [t for t in terms_by_uid.get(uid, []) if t.get("name") == nm]
        if nm == "" or len(same) > 1:
            by_mode["index"] += 1
            idx_rows.append((uid, i, nm, src, w))
        else:
            by_mode["name"] += 1
    fact(f"P1-B3 addressing mode of the 109 cut terminals: {by_mode} - the INDEX rows are addressable because "
         f"build_d1_v0.json already stores [node_uid, term_index, name, is_source, wire] "
         f"(review B3; stage2-a3-wire-shiftreg-plan.md:129)")
    fact(f"P1-B3 the {len(idx_rows)} index-addressed rows: {idx_rows}")
    return cut_wires, missing, idx_rows


# ============================================================================== P1b / T6 / P2
def p2(missing):
    # rev3 A5: this banner still said "donor == target", which rev2 B2 removed everywhere else in the file - and
    # the banner is what lands in the log the retrospective and the next session read.
    print("\n=== P2: `copy_by_index` from a SEPARATELY NAMED donor copy, then `move_in` - OPEN 28's route",
          flush=True)
    if not FRESH_INSTANCE_DONE:
        gate("P2-B1 a copy_by_index session starts on a FRESH LabVIEW instance", False,
             "NOT restarted. `build_track_v6_queue.py:105-109` records Errno 22 when copy_by_index substituted "
             "the Move-example Target while LabVIEW still had it loaded, and `gscript.py:1304-1307` states the "
             "rule: 'the caller restarts LabVIEW before a copy_by_index session'. `g._lv = None` clears the "
             "Python COM handle, NOT LabVIEW's loaded VIs. Set FRESH_INSTANCE_DONE only after tools/lv_restart.py "
             "has run in this process.")
        return {}       # RUN 1 CRASHED HERE: `return res` before `res = {}` -> UnboundLocalError, so the refusal
                        # took the whole run down with a traceback instead of reporting P3 and the md5.
    res = {}
    shutil.copy2(ORIGINAL, T0)
    m = md5(T0)
    if not gate("P2z the working copy on DISK is byte-identical to the original", m == ORIG_MD5, m):
        return res
    # --- P2a THE DISCRIMINATOR (rev2 A1). Three reads on ONE copy, in the order drive_original_copy_v2.py used.
    es_ref = es_panel = es_settle = None
    try:
        _vref = g.lv().GetVIReference(T0, "", False, 0)
        es_ref = int(_vref.ExecState)
    except Exception as e:
        es_ref = f"<{str(e)[:60]}>"
    g.open_panel(T0)
    try:
        es_panel = g.exec_state(T0)
    except Exception as e:
        es_panel = f"<{str(e)[:60]}>"
    time.sleep(2.0)
    try:
        es_settle = g.exec_state(T0)
    except Exception as e:
        es_settle = f"<{str(e)[:60]}>"
    fact(f"P2a ExecState of ONE fresh copy: after GetVIReference={es_ref}; immediately after "
         f"OpenFrontPanel(False)={es_panel}; after a 2 s settle={es_settle}. "
         f"⚠️ rev3 A3: this is NOT the number `copy_by_index` gates on - `gscript.py:1351` reads "
         f"`exec_state(MOVE_DST)`, the Move-example FIXTURE (gscript.py:55) that the target's BYTES are copied "
         f"onto at :1321, after the Move and after the finish hook. Every recorded caller gates its own op "
         f"instead (build_opconstvalue_v1.py:166). "
         f"⚠️ rev3 A4: the discriminator is PRELOAD, not elapsed time. `drive_original_copy_v3.log:7` preloads "
         f"the ORIGINAL hierarchy before opening the copy; the record splits 3-3 with no exceptions (1 = "
         f"preloaded: v3:7-12, v2:8-13, d0_clickprobe:7-12; 0 = not: build_d1_v0_run5:13-16, run4:18, "
         f"probe_move_into_v0:217), and the ~1.3 s gap is present in ALL THREE of the 1s, so time is fully "
         f"confounded. Varying only the settle CANNOT separate them - the controlled pair (same instance, one "
         f"copy read with the original resident and one without) is the measurement still worth buying. "
         f"d1-build-plan.md:203's word 'headlessly' is WITHDRAWN (rev2 A2) - that run had the panel open.")
    gate("P2a all three ExecState reads completed (the gate is the MEASUREMENT, not a particular number)",
         all(isinstance(x, int) for x in (es_ref, es_panel, es_settle)),
         f"{(es_ref, es_panel, es_settle)}")
    res["execstate_discriminator"] = dict(after_getviref=es_ref, after_panel=es_panel, after_settle=es_settle)
    es_open = es_settle
    counts = {c: g.count(T0, c) for c in BEFORE_COUNTS}
    fact(f"P2a BEFORE counts: {counts}")
    gate("P2a the copy matches the recorded BEFORE census",
         all(counts[c] == BEFORE_COUNTS[c] for c in BEFORE_COUNTS),
         f"{ {c: (BEFORE_COUNTS[c], counts[c]) for c in BEFORE_COUNTS if counts[c] != BEFORE_COUNTS[c]} }")

    # ---- T6 CONTROL, then P1b, both on the untouched copy (the moves below would cut wires)
    ws, stop = wire_source(T0, 10850)
    src = [r for r in ws if r["is_source"]]
    fact(f"T6 control wire_source(10850) -> {len(ws)} terminals, stop={stop!r}, rows={ws}")
    ctrl_ok = gate("T6 CONTROL OpWireSource_v5 reproduces its published answer (w10850 source = constant #10739)",
                   len(src) == 1 and src[0]["owner_uid"] == 10739, f"sources {src}")
    res["t6_control"] = dict(rows=ws, stop=stop, ok=ctrl_ok)
    # rev3 A1/A2: w3268's SOURCE is already on record (diag_autofocus_border.log:19-26). This loop is kept only
    # as the mechanism for A1's released remainder - completing the SINK enumeration at max_terms=8 - and is a
    # no-op whenever `missing` is empty, which the offline join predicts it will be for the source question.
    res["p1b"] = {}
    for w in missing:
        rows, st = wire_source(T0, w)
        s = [r for r in rows if r["is_source"]]
        res["p1b"][str(w)] = dict(rows=rows, stop=st)
        fact(f"P1b w{w}: {len(rows)} terminals, source(s) {s}, stop={st!r}")
    if ctrl_ok:
        gate("P1b every wire the stored resolution does not cover gets a source from the machine",
             all(any(r["is_source"] for r in v["rows"]) for v in res["p1b"].values()) if res["p1b"] else True,
             f"{ {k: [r for r in v['rows'] if r['is_source']] for k, v in res['p1b'].items()} }")
    else:
        print("  SKIPPED-INVALID  P1b: the control did not reproduce its published answer, so nothing may be "
              "concluded from this reader in this run (toolkit-capabilities.md:213)", flush=True)

    # ---- P2b: the LITERAL half - copy the -1 donor constant, donor == target
    cls, idx = traverse_index(T0, CONST_MINUS1_UID)
    fact(f"P2b the -1 donor constant #{CONST_MINUS1_UID} is {cls}[{idx}] in the working copy")
    if not gate("P2b the -1 donor constant resolves to a Traverse class+index", cls is not None, f"{cls}"):
        return res
    try:
        g.close_panel(T0)
    except Exception:
        pass
    g._loaded.discard(os.path.normcase(os.path.abspath(T0)))
    shutil.copy2(ORIGINAL, TDONOR)          # rev2 B2: a SEPARATELY NAMED donor, not donor == target
    added, sel = None, None
    err = ""
    try:
        added, sel = g.copy_by_index(TDONOR, cls, idx, T0, expect_uid=CONST_MINUS1_UID)
    except Exception as e:
        err = str(e)[:400]
    fact(f"P2b copy_by_index(donor={os.path.basename(TDONOR)}, {cls}[{idx}] -> {os.path.basename(T0)}) "
         f"-> added {added}, selected {sel}, error {err!r}")
    if not gate("P2b the -1 literal is copied in from a separately named copy of the original (rev2 B2)",
                bool(added) and not err, f"added {added}, err {err!r}"):
        res["p2b_error"] = err
        return res
    # continue on a FRESH filename: copy_by_index just rewrote T0 from MOVE_DST on disk
    shutil.copy2(T0, T1)
    g._loaded.discard(os.path.normcase(os.path.abspath(T1)))
    g.open_panel(T1)
    new_const = added[0]["uid"] if isinstance(added[0], dict) else added[0]
    after_counts = {c: g.count(T1, c) for c in BEFORE_COUNTS}
    fact(f"P2b AFTER counts: {after_counts}; the new constant is uid {new_const}")
    gate("P2b exactly one DigitalNumericConstant was added and NO panel object was created",
         after_counts["DigitalNumericConstant"] == BEFORE_COUNTS["DigitalNumericConstant"] + 1
         and after_counts["ControlTerminal"] == BEFORE_COUNTS["ControlTerminal"]
         and after_counts["Local"] == BEFORE_COUNTS["Local"],
         f"{after_counts}")
    res["new_const"] = new_const

    # ---- P2c: a While loop on Diagram#686 and move_in of the copied literal into its body
    sib_i = diag_index(T1, SIBLING_DIAG_UID)
    dg0, wl0 = g.uids(T1, "Diagram"), g.uids(T1, "WhileLoop")
    g.loop_in("while", T1, sib_i, (2600, 2600))
    new_dg, new_wl = g.new_since(T1, "Diagram", dg0), g.new_since(T1, "WhileLoop", wl0)
    if not gate("P2c one new While loop on Diagram#686", len(new_dg) == 1 and len(new_wl) == 1,
                f"+{len(new_dg)} diagrams, +{len(new_wl)} loops"):
        return res
    body_uid, loop_uid = new_dg[0]["uid"], new_wl[0]["uid"]
    fact(f"P2c test loop: WhileLoop #{loop_uid}, body Diagram #{body_uid}")
    move_in(T1, new_const, diag_index(T1, body_uid), (120, 120))
    try:
        oc, ou = owner_of(T1, new_const)
    except Exception as e:
        oc, ou = f"<{str(e)[:60]}>", None
    try:
        oc2, ou2 = owner_of(T1, ou) if ou else (None, None)
    except Exception as e:
        oc2, ou2 = f"<{str(e)[:60]}>", None
    gate("P2c a COPIED constant (provenance is the only untested variable - rev2 B1: run 5 already did this "
         "three times for constants the VI already owned) lands inside the new loop body",
         ou == body_uid and ou2 == loop_uid,
         f"owner {oc}#{ou} (want Diagram#{body_uid}); owner(owner) {oc2}#{ou2} (want WhileLoop#{loop_uid})")
    final = {c: g.count(T1, c) for c in BEFORE_COUNTS}
    fact(f"P2c counts after the move: {final}")
    gate("P2c the move created no panel object", final["ControlTerminal"] == BEFORE_COUNTS["ControlTerminal"]
         and final["Local"] == BEFORE_COUNTS["Local"], f"{final}")
    res["p2c"] = dict(loop=loop_uid, body=body_uid, owner=(oc, ou), owner2=(oc2, ou2), counts=final)

    # ---- P2d: the COMPARISON half. The stop is PREDICTED, in the docstring, before the run.
    ccls, cidx = traverse_index(T1, EQUAL_UID)
    fact(f"P2d the comparison donor `Equal?` #{EQUAL_UID} is {ccls}[{cidx}]")
    fact("P2d NOT ATTEMPTED IN THIS RUN, and the reason is arithmetic, not a result: a comparison primitive has "
         "TWO REQUIRED inputs; `copy_by_index` refuses to save a Target that is not ExecState 1 "
         "(gscript.py:1351-1354); and the only fleet feeders at top level are `create_control` - which ADDS A "
         "PANEL CONTROL and breaks the plan's own 'ControlTerminal still 114' (d1-build-plan.md s10 S3c/S4s) - "
         "or another TOP-LEVEL node's output, and a Constant is not a `Nodes[]` member "
         "(toolkit-capabilities.md:494). Which way out to take is a DESIGN call -> OPEN, not taken here.")
    res["p2d"] = dict(cls=ccls, index=cidx, attempted=False)
    return res


# ============================================================================== main
def main():
    # THE RESTART IS THIS RUN'S JOB, NOT THE CALLER'S (fixed 2026-09-17 after run 1). P2's gate demands that
    # `tools/lv_restart.py` has run IN THIS PROCESS, and nothing in the file ever ran it - so the gate could only
    # ever refuse, whatever the caller exported. An environment variable is not a restart; `g._lv = None` clears
    # the Python COM handle, not LabVIEW's loaded VIs (`gscript.py:1304-1307`). Standing restart permission,
    # CLAUDE.md §3 ("재시작 항상 오케이"). SKIP_LV_RESTART=1 is for a caller that has JUST restarted.
    global FRESH_INSTANCE_DONE
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if os.environ.get("SKIP_LV_RESTART") == "1":
        FRESH_INSTANCE_DONE = True
        print("=== P0r: restart SKIPPED by SKIP_LV_RESTART=1 (the caller asserts a fresh instance)", flush=True)
    else:
        print("=== P0r: restarting LabVIEW so copy_by_index starts on a fresh instance", flush=True)
        import subprocess
        rc = subprocess.call([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")])
        FRESH_INSTANCE_DONE = (rc == 0)
        print(f"=== P0r: lv_restart.py rc={rc} -> FRESH_INSTANCE_DONE={FRESH_INSTANCE_DONE}", flush=True)
    g._lv = None
    t0 = time.time()
    result = {}
    print("=== P0: preconditions", flush=True)
    m0 = md5(ORIGINAL)
    if not gate("P0a original md5 BEFORE", m0 == ORIG_MD5, m0):
        return 2
    for nm, p in (("OpMoveIn_v0", OPIN), ("OpWireSource_v5", OPWSRC), ("OpStopFromNode_v0", OPSTOP),
                  ("OpMoveByIndex_v0", OPMBI)):
        if not gate(f"P0b {nm} present", os.path.exists(p), p):
            return 2
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")

    try:
        cut_wires, missing, idx_rows = p1()
        result.update(cut_wires=len(cut_wires), p1_missing=missing, index_addressed=len(idx_rows))
        result["p2"] = p2(missing)
    finally:
        for p in STAGES:
            try:
                if os.path.exists(p):
                    g.close_panel(p)
            except Exception:
                pass
            try:
                if os.path.exists(p):
                    os.remove(p)
                    fact(f"working copy deleted: {p}")
            except Exception as e:
                fact(f"working copy NOT deleted ({str(e)[:60]}): {p}")
        # NO `restore_move_fixtures()` HERE. rev2 A5 (`refuted-already`): `gscript.py:1268-1272` forbids it -
        # "never in a finally while a VI may still be in memory" - and the exchange that established it
        # (`archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:75,:81`) calls an unconditional
        # disk restore in `finally` "the PRIMARY PROTOCOL DEFECT": it rewrites fixture bytes under a loaded,
        # dirty MOVE_DST and creates the changed-on-disk split-brain that needs a LabVIEW restart. `copy_by_index`
        # already restores at the START of every call (`:1320`), which is the sanctioned placement, so a failed
        # copy here correctly leaves the fixtures as they are for the next call's restore.
        g._lv = None
        m1 = md5(ORIGINAL)
        gate("P3 original md5 AFTER", m1 == ORIG_MD5, m1)
        try:
            fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
        except Exception as e:
            fact(f"handles after: unreadable ({str(e)[:60]})")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)
        fact(f"wrote {OUT}")

    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== diag_d1_full_route: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
