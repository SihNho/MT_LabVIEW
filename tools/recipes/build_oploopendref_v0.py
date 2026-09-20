r"""build_oploopendref_v0.py - OpLoopEndRef_v0.vi: a While loop's CONDITIONAL TERMINAL, read from the machine.

THE DEVICE FOR `repeated-failure-class`, round 5 (docs/violation-decisions.md 2026-09-17 03:38, 7 occurrences):
"how does WhileLoop #637 stop" was diagnosed by INFERENCE twice - `diag_stop_condterm_panel`,
`diag_stop_save_seam` - and both were refuted, because no reader exists. CLAUDE.md: "the second time a class of
failure is explained by inference rather than read from the machine, the next build is the READER for it".

ORDERING, STATED CORRECTLY (prior-art A3-i). `docs/main-vi-stop-and-save.md:72-74` and `STATUS.md:78-79` name this
reader as **step (2) of two**: first a RECURSIVE front-panel `ControlTerminal` census against wire 3457, and "only
if that finds no second carrier" the `Loop End Ref` reader. Both external peers said the same
(`tools/bench/peer_stopterm.log:39`, `peer_stopterm2.log:58`). That ordering is SUPERSEDED by the later, dated
decision `docs/violation-decisions.md:281-290` (2026-09-17 03:38), which makes this reader the due device by name
and by ID; step (1) would itself need a new terminal-by-UID reader (`panel_wiring` is documented non-recursive,
`tools/gscript.py:640`, and `OpWireSource_v5` returns a terminal's OWNER, not its own UID). Recorded because the
first draft of this file claimed those two documents mandated this step directly, and they do not.
Bearing on the skipped step (1) and previously unread (prior-art A4): `docs/toolkit-capabilities.md:510-511` -
"`fp_labels` returns 114 objects and `report('ControlTerminal')` returns 114 - every front-panel object has exactly
one diagram terminal in this VI" - direct, though not conclusive, evidence against a 115th tab-page-nested control
terminal being wire 3457's second carrier.

WHAT ALREADY EXISTS - checked before writing a line (CLAUDE.md "before creating any new op"):
  * `OpWhileCast_v0.vi` + `gscript.loop_cast(target, index, 'WhileLoop')` (gscript.py:432,
    docs/toolkit-capabilities.md:33) ALREADY produces a **WhileLoop-TYPED reference** to the index-th While loop of
    any VI, addressed exactly as this task needs (vi path + Traverse class + index), and already reports the loop's
    UID. Measured on this very VI: "3/3 While loops of the main VI, frame loop = 14 shift registers"
    (`tools/bench/test_oploopcast.log`). IT IS THE DONOR, and the build below is purely ADDITIVE - nothing in it is
    deleted, so the donor's measured behaviour cannot regress.
  * The whole downstream half is also already built and functionally verified: `OpWireSource_v5.vi` reads a
    **Terminal**'s `Is Source?` 634A003 and `Connected Wire` 634A000 and a wire's SOURCE NODE (class + uid) -
    docs/toolkit-capabilities.md:48, INDEX row 43, 12/12. This recipe therefore does NOT re-implement wire->source:
    it CALLS `read_terminal()` from `build_opwiresource_v5` verbatim (the same driver `diag_9775_direction.py:73`
    uses). `node_labels(MAIN, 43)` (gscript.py:393) supplies the source node's label.
  * `OpOwnerChain_v1` gives owner-of-object; it does NOT reach a loop's conditional terminal (the terminal is not
    reachable from any node's `Terminals[]` - that is exactly why two inference attempts failed;
    `archive/peer/2026-09-16-stop-condterm-panel-fail2.md`).
  * `grep -n "^def " tools/gscript.py` has no loop-terminal helper; `ls tools/recipes | grep -i loop` shows
    build_oploopcast_v0/v1, build_oploopin, build_opwhileloop, build_opexitwhile, build_oploopkernel - none reads
    `Loop End Ref`. `ls claudeDev | grep -i Op` has no OpLoopEndRef.
  * `tools/recipes/build_opcaseframes_v0.py:48-59` `prop_node()` and `:62-71` `add_indicator()` already do the two
    things this build needs done CORRECTLY (prior-art B3-ii), so they are IMPORTED and called, not re-written -
    the module parameterises them by a module-global `OP`, so the one adaptation is rebinding that global.
  * The ONE genuinely new thing is the single property **`WhileLoop.Loop End Ref` 0x06362C00** (docs/NAMES.md:246,
    corroborated externally twice - `tools/bench/peer_stopterm.log:32-37`, `peer_stopterm2.log:49`, both citing
    labviewwiki's WhileLoop property table and the NI forum thread "VI Scripting: locate loop iteration and
    conditional terminals"). No new capability class, no new addressing scheme.

CONSTRUCTION (all of it is the idiom `build_oploopcast_v0.py:285-300` already uses on this donor lineage):
    TMSC out (WhileLoop-typed, existing) --branch--> PN_LER  WhileLoop['Loop End Ref' 6362C00]
                                                       |-> PN_TUID GObject[UID 632A813]      -> CondTermUID
                                                       |-> PN_IS   Terminal['Is Source?' 634A003] -> IsSource
                                                       `-> PN_CW   Terminal['Connected Wire' 634A000]
                                                              `-> PN_WUID GObject[UID]       -> CondWireUID
One property per node, each with its own error indicator (the design rule from
docs/toolkit-capabilities.md: "a failing row silently defaults the rows below it on the same node").

PRIOR-ART REVIEW OF THIS RECIPE: `archive/peer/2026-09-17-priorart-priorart-loopendref.md` (claude/opus, 533 s,
7 verdicts, **0 novel-blocking**: B1 says the artifact IS novel). All seven are accepted and implemented above -
A3-i the ordering claim, A3-ii the zero branch, A3-iii the Abort citation, A4 the 114==114 evidence, B3-i the
census-not-1077 gate, B3-ii the two imported helpers, B4 "confirms test_oploopcast.log:84". B2 is a warning, not a
finding: `OpCaseFrames_v0` run 5 failed in the SAME SHAPE as gate L4 (property attached, census passed, VI still
ExecState 0 with the seed wired - build_opcaseframes_v0.log:120-127). That construction was mid-surgery on a
retargeted donor and this one is additive, but L4 is exactly where it would show, and the response is to stop
without saving - which is what the code does.

PREDICTION CONTRACT (every value is asserted in the run)
  L0  MAIN md5 2a78e17c449cacdaf5da389818526859 before AND after; the main VI is only ever READ.
  L1  the copy of OpWhileCast_v0.vi opens at ExecState 1.
  L2  its TMSC is found by terminal names ('target class' + 'specific class reference').
  L3  each of the five property nodes is CREATED **and its DATA TERMINAL is censused** - exactly one data SOURCE
      terminal, whose short name is printed and then used. "No error 1077" is explicitly NOT the verdict
      (prior-art B3-i): `docs/toolkit-capabilities.md:234-238` measured a VALID id on the WRONG class
      (`Control.Value` 633200D) creating a node with no data terminal AND NO ERROR AT ALL, and states that any
      "does property X exist on class Y?" test must use the data-terminal-name census of
      `build_opcaseframes_v0.py:49-58`. This build IS such a test: `docs/NAMES.md:241-247` marks the whole
      Loop/ForLoop/WhileLoop id block "not yet verified on this machine".
  L4  after wiring TMSC -> PN_LER the VI is still ExecState 1. THIS IS THE REAL STRUCTURAL GATE: a
      WhileLoop-class property node accepts the cast output only if the seed genuinely typed the TMSC, and it is
      the same gate that proved the ForLoop chain (build_oploopcast_v0.py:276-279).
  L5  ExecState 1 after every remaining wire, and before the single save.
  L6  after `fresh()` (kill LabVIEW, COM-preflight, cold reload - `g.reset()` would only test memory,
      build_opownerchain_v1.py:456-460) the SAVED op is still ExecState 1.
  L7  FUNCTIONAL, read-only on the main VI: scanning Traverse indices of class WhileLoop, exactly one index
      returns LoopUID 637 - CONFIRMING `tools/bench/test_oploopcast.log:84` ("WhileLoop[1] uid 637"), not
      discovering it (prior-art B4) - and for it the op returns a conditional-terminal UID != 0 with no error.
  L8  the conditional terminal's `Connected Wire`: reported, NOT predicted. The live hypotheses -
        wire 3457  => the source is `CompoundArithmetic` #11639  (stop (end) uid 7 OR-ed;  main-vi-stop-and-save.md:48)
        wire 15229 => the source is `CompoundArithmetic` #17883  (stop (end) 2 uid 19587)
        0          => **INCONCLUSIVE, READER SUSPECT - NOT "the loop has no Boolean stop"** (prior-art A3-ii).
                      That reading is already refuted FUNCTIONALLY: `tools/bench/drive_original_copy_v3.log:80-81`
                      stopped a running copy through its own `stop (end)` control ("idle after 2s") and
                      `save N xyz traces.vi` #6384 - which sits on diagram 19 AFTER the frame loop
                      (main-vi-stop-and-save.md:80) - then wrote `tra001-000`, so #637 terminated normally from a
                      Boolean rather than by Abort. A zero here would mean the addressing or the property is
                      wrong, and the run says so instead of concluding anything about the VI.
        anything else is a third answer and is reported as such.
      No branch of L8 is a failure; the gate is only that ONE source terminal resolves (OpWireSource_v5's own
      contract) when the wire is non-zero.
      (`docs/frame-ownership-design.md`'s Abort sentence is at **:105**, not :92-97 - those lines are the
      superseded camera-overload paragraph. `docs/main-vi-stop-and-save.md:75` carries the same wrong citation and
      is corrected in the same pass. Prior-art A3-iii.)
  L9  scratch discipline: the only new artefact is OpLoopEndRef_v0.vi under claudeDev (save authority, rule 3).
      No original is written. No hardware. No GUI.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/build_oploopendref_v0.log \
      -- py -u tools/recipes/build_oploopendref_v0.py
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
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402
from build_opwiresource_v5 import OP as OP_WS, MAP_OUT as MAP_WS, read_terminal  # noqa: E402
import build_opcaseframes_v0 as CF  # noqa: E402  - prior-art B3-ii: its prop_node/add_indicator ARE the helpers

DONOR = os.path.join(g.CLAUDEDEV, "OpWhileCast_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpLoopEndRef_v0.vi")
# The two helpers are written against a module-global target, so reuse means rebinding that global - the whole
# adaptation. prop_node() censuses the new node's single data SOURCE terminal (never guessing a short name);
# add_indicator() asserts one new panel object, that it IS an indicator, and that its label is UNIQUE, which is
# what keeps the label map this op is later driven by from being silently mis-keyed.
CF.OP = OP
DONOR_MAP = os.path.join(ROOT, "tools", "bench", "opwhilecast_labels.json")
MAP_OUT = os.path.join(ROOT, "tools", "bench", "oploopendref_labels.json")
OUT_JSON = os.path.join(ROOT, "tools", "bench", "loopendref_637.json")

ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
FRAME_LOOP = 637          # WhileLoop #637, owner of Diagram#639 = diagram 43 (main-vi-stop-and-save.md s0)
FRAME_DIAGRAM = 43        # Traverse 'Diagram' index of Diagram#639

P_LOOPENDREF = "6362C00"  # WhileLoop.Loop End Ref   (docs/NAMES.md:246)
P_UID = "632A813"         # GObject.UID              (build_oploopcast_v0.py:63)
P_ISSOURCE = "634A003"    # Terminal.Is Source?      (docs/toolkit-capabilities.md:48)
P_CONNW = "634A000"       # Terminal.Connected Wire  (build_oploopcast_v0.py:63)
T_CAST_OUT = "specific class reference"

g._run.__defaults__ = (6.0, 120.0)
passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def snap(tag=""):
    return (f"{tag} Property={len(g.report_all(OP, 'Property'))} Wire={len(g.report_all(OP, 'Wire'))} "
            f"ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def node_terms_of(uid, diagram=0):
    for cand in range(80):
        nu, rows = g.node_terms_uid(OP, diagram, cand)
        if not nu:
            return None, None
        if nu == uid:
            return cand, rows
    return None, None


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    m0 = md5(MAIN)
    gate("L0a MAIN md5 before", m0 == ORIG_MD5, m0)
    if m0 != ORIG_MD5:
        return 1
    if not os.path.exists(DONOR):
        gate("L1 donor present", False, DONOR)
        return 1

    # ---------------------------------------------------------------- build
    try:
        g.close_panel(OP)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(OP):
        os.remove(OP)
    donor_md5 = md5(DONOR)
    shutil.copyfile(DONOR, OP)
    time.sleep(0.3)
    g.open_panel(OP)
    time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        """OpBuildPN/OpConnect carry the erdosmiller creator, which drops ONE untyped Invoke on the target per
        call (docs/keystone-op-spec.md:565-573 s33; build_opownerchain_v1.py:231-243)."""
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", i, verify=False)

    st0 = g.exec_state(OP)
    print(f"  {snap('start:')}", flush=True)
    if not gate("L1 the donor copy starts legal", st0 == 1, f"ExecState {st0}"):
        return 1

    purge()
    nodes, _nets = g.net_map(OP, 0, max_nodes=60, max_terms=24)
    tmsc = next(((u, terms) for _n, (u, _l, terms) in nodes.items()
                 if any(t == "target class" for _ti, t, _w in terms)
                 and any(t == T_CAST_OUT for _ti, t, _w in terms)), None)
    if not gate("L2 the WhileLoop TMSC is on the donor", tmsc is not None):
        return 1
    tmsc_uid = tmsc[0]
    fact(f"TMSC uid {tmsc_uid}; its output terminal {T_CAST_OUT!r} is the WhileLoop-typed reference")

    def pn(cls, pid, label, pos):
        """prior-art B3-i/B3-ii: the verdict is the DATA-TERMINAL CENSUS, not the absence of error 1077 -
        a valid id on the wrong class creates a terminal-less node with no error at all
        (docs/toolkit-capabilities.md:234-238). build_opcaseframes_v0.prop_node does exactly that census."""
        r = CF.prop_node(cls, pid, label, pos)
        purge()
        return r

    # PN_LER - the ONE new property. Its class must be WhileLoop: `Loop End Ref` is a WhileLoop property, not a
    # Loop one (docs/NAMES.md:246 lists it under WhileLoop; 6362002 under the For-loop table is a DIFFERENT id).
    try:
        u_LER, t_ler = pn("VI Server:WhileLoop", P_LOOPENDREF, "Loop End Ref", (900, 1150))
    except Exception as e:
        gate("L3a PN_LER WhileLoop['Loop End Ref'] created AND censused to one data terminal", False,
             f"{type(e).__name__} {str(e)[:200]}")
        return 1
    gate("L3a PN_LER WhileLoop['Loop End Ref'] created AND censused to one data terminal", True,
         f"uid {u_LER}, data terminal {t_ler!r}")
    g.wire(OP, "Function", idx("Function", tmsc_uid), T_CAST_OUT,
           "Property", idx("Property", u_LER), "reference", branch=True)
    purge()
    es = g.exec_state(OP)
    if not gate("L4 the WhileLoop-class property node ACCEPTS the cast output", es == 1,
                f"ExecState {es} - if 0, the TMSC is not WhileLoop-typed or the property is not on this class"):
        print("STOP: nothing is saved (failure budget - no repair pass).", flush=True)
        return 1
    fact(f"PN_LER data terminal name {t_ler!r}  (WhileLoop.Loop End Ref {P_LOOPENDREF} IS on this class)")

    built = [("L3a", u_LER, t_ler)]
    try:
        u_TUID, t_tuid = pn("VI Server:GObject", P_UID, "UID(term)", (1250, 1100))
        g.wire(OP, "Property", idx("Property", u_LER), t_ler,
               "Property", idx("Property", u_TUID), "reference")
        purge()
        built.append(("L3b", u_TUID, t_tuid))
        u_IS, t_is = pn("VI Server:Terminal", P_ISSOURCE, "Is Source?", (1250, 1250))
        g.wire(OP, "Property", idx("Property", u_LER), t_ler,
               "Property", idx("Property", u_IS), "reference", branch=True)
        purge()
        built.append(("L3c", u_IS, t_is))
        u_CW, t_cw = pn("VI Server:Terminal", P_CONNW, "Connected Wire", (1250, 1400))
        g.wire(OP, "Property", idx("Property", u_LER), t_ler,
               "Property", idx("Property", u_CW), "reference", branch=True)
        purge()
        built.append(("L3d", u_CW, t_cw))
        u_WUID, t_wuid = pn("VI Server:GObject", P_UID, "UID(wire)", (1600, 1400))
        g.wire(OP, "Property", idx("Property", u_CW), t_cw,
               "Property", idx("Property", u_WUID), "reference")
        purge()
        built.append(("L3e", u_WUID, t_wuid))
    except Exception as e:
        gate("L3 all five property nodes built, censused and wired", False,
             f"{type(e).__name__} {str(e)[:220]}; built {built}")
        print("STOP: nothing is saved (failure budget - no repair pass).", flush=True)
        return 1
    gate("L3 all five property nodes built, censused and wired", True, str(built))
    es = g.exec_state(OP)
    print(f"  {snap('assembled:')}", flush=True)
    if not gate("L5 the assembled op is legal", es == 1, f"ExecState {es}"):
        print("STOP: not saving a broken VI.", flush=True)
        return 1

    # ---- indicators + label map ----------------------------------------------------------------
    with open(DONOR_MAP, encoding="utf-8") as f:
        label_map = json.load(f)          # label -> meaning, inherited from OpWhileCast_v0
    wanted = [(u_TUID, t_tuid, "CondTermUID"), (u_WUID, t_wuid, "CondWireUID"), (u_IS, t_is, "IsSource"),
              (u_LER, "error out", "LoopEndRefErr"), (u_IS, "error out", "IsSourceErr"),
              (u_CW, "error out", "ConnWireErr"), (u_WUID, "error out", "WireUIDErr")]
    by_key = {}
    for uid, term_name, meaning in wanted:
        try:
            CF.add_indicator(uid, term_name, meaning, by_key)   # asserts: 1 new object, IS an indicator, label UNIQUE
            label_map[by_key[meaning]] = meaning
        except Exception as e:
            print(f"  indicator {meaning}: {type(e).__name__} {str(e)[:160]}", flush=True)
    purge()
    g.set_auto_error_handling(OP, False)
    es = g.exec_state(OP)
    print(f"  label map: {json.dumps(label_map)}", flush=True)
    have = {v for v in label_map.values()}
    missing = [m for _u, _t, m in wanted if m not in have]
    if not gate("L5b every indicator landed and the op is still legal", es == 1 and not missing,
                f"ExecState {es}, missing {missing}"):
        print("STOP: not saving.", flush=True)
        return 1
    size = g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    fact(f"saved {size} bytes; label map -> {os.path.basename(MAP_OUT)}")
    gate("L9 the donor OpWhileCast_v0.vi is byte-identical", md5(DONOR) == donor_md5)

    # ---- L6: cold reload ------------------------------------------------------------------------
    fresh()
    es2 = g.exec_state(OP)
    gate("L6 the SAVED op is still legal in a fresh LabVIEW", es2 == 1, f"ExecState {es2}")
    if es2 != 1:
        print(f"MAIN md5 after: {md5(MAIN)}", flush=True)
        return 1

    # ---- L7/L8: FUNCTIONAL, read-only on the main VI --------------------------------------------
    lab = {v: k for k, v in label_map.items()}
    vi = g.op(OP)
    n_while = len(g.report_all(MAIN, "WhileLoop"))
    fact(f"the main VI has {n_while} objects of Traverse class WhileLoop")
    rows, hit = [], None
    for i in range(n_while):
        for k in ("CondTermUID", "CondWireUID", "LoopUID"):
            vi.SetControlValue(lab[k], 0)
        vi.SetControlValue(lab["IsSource"], False)
        for k in ("LoopEndRefErr", "IsSourceErr", "ConnWireErr", "WireUIDErr"):
            try:
                vi.SetControlValue(lab[k], (False, 0, ""))
            except Exception:
                pass
        vi.SetControlValue("vi path", MAIN)
        vi.SetControlValue("Class Name", "WhileLoop")
        vi.SetControlValue("index", i)
        err = ""
        try:
            g._run(vi)
            err = g._err(vi, "error out") or ""
        except Exception as e:
            err = f"EXC {str(e)[:100]}"
        errs = " ".join(x for x in (g._err(vi, lab[k]) or ""
                                    for k in ("LoopEndRefErr", "IsSourceErr", "ConnWireErr", "WireUIDErr")) if x)
        r = dict(index=i, loop_uid=int(vi.GetControlValue(lab["LoopUID"])),
                 cond_term_uid=int(vi.GetControlValue(lab["CondTermUID"])),
                 is_source=bool(vi.GetControlValue(lab["IsSource"])),
                 cond_wire_uid=int(vi.GetControlValue(lab["CondWireUID"])), err=err, errs=errs)
        rows.append(r)
        print(f"  OBSERVED WhileLoop[{i}] uid {r['loop_uid']}: cond terminal uid {r['cond_term_uid']}, "
              f"Is Source? {r['is_source']}, Connected Wire {r['cond_wire_uid']} | {err[:40]} {errs[:70]}",
              flush=True)
        if r["loop_uid"] == FRAME_LOOP:
            hit = r
    ok7 = hit is not None and hit["cond_term_uid"] != 0 and not hit["errs"]
    gate(f"L7 WhileLoop #{FRAME_LOOP} resolves to a conditional terminal", ok7,
         f"{hit}" if hit else f"uid {FRAME_LOOP} not among {[r['loop_uid'] for r in rows]}")

    out = {"main_md5_before": m0, "rows": rows, "frame_loop": hit}
    if ok7:
        w = hit["cond_wire_uid"]
        fact(f"WhileLoop#{FRAME_LOOP} conditional terminal = uid {hit['cond_term_uid']}, "
             f"Is Source? {hit['is_source']}, Connected Wire uid {w}")
        if w == 0:
            # prior-art A3-ii: a zero here is NOT a fact about the VI. drive_original_copy_v3.log:80-81 stopped a
            # running copy through `stop (end)` ("idle after 2s") and save N xyz traces.vi #6384 - which sits AFTER
            # the frame loop, on diagram 19 - then wrote tra001-000, so #637 does terminate from a Boolean.
            fact(f"`Connected Wire` on #{FRAME_LOOP}'s conditional terminal read 0 - INCONCLUSIVE, reader suspect")
            out["source"] = None
            out["verdict"] = ("INCONCLUSIVE - READER SUSPECT: Connected Wire came back 0. That cannot mean #637 "
                              "has no Boolean stop: drive_original_copy_v3.log:80-81 stopped a running copy with "
                              "`stop (end)` (idle after 2 s) and `save N xyz traces.vi` #6384, AFTER the loop on "
                              "diagram 19, wrote tra001-000. So the addressing or the property read is wrong. "
                              "Nothing about the VI is concluded here.")
        else:
            with open(MAP_WS, encoding="utf-8") as f:
                wslab = json.load(f)
            ws = g.op(OP_WS)
            trows = []
            for i in range(8):
                rr = read_terminal(ws, wslab, w, i)
                if rr["errs"] and rr["owner_uid"] == 0 and not rr["is_source"]:
                    break
                trows.append(rr)
            srcs = [t for t in trows if t["is_source"] and t["recip_wire"] == w]
            gate("L8 the conditional terminal's wire resolves to exactly ONE source",
                 len(srcs) == 1, f"{len(srcs)} source terminal(s) among {len(trows)}")
            if len(srcs) == 1:
                sc, su = srcs[0]["owner_class"], srcs[0]["owner_uid"]
                label = ""
                try:
                    label = next((r["label"] for r in g.node_labels(MAIN, FRAME_DIAGRAM) if r["uid"] == su), "")
                except Exception as e:
                    label = f"<node_labels: {str(e)[:60]}>"
                known = {11639: "CompoundArithmetic #11639 - `stop (end)` uid 7 OR-ed (main-vi-stop-and-save.md:48)",
                         17883: "CompoundArithmetic #17883 - `stop (end) 2` uid 19587 OR-ed",
                         22082: "CaseStructure #22082",
                         22085: "Tunnel #22085 of CaseStructure #22082"}
                out["source"] = dict(wire=w, cls=sc, uid=su, label=label)
                out["verdict"] = (f"wire {w} is driven by {sc} #{su} (label {label!r}) = "
                                  f"{known.get(su, 'NONE of the three hypotheses - a fourth answer')}")
                fact(f"SOURCE of the conditional wire {w}: {sc} #{su}, label {label!r}")
                fact(f"VERDICT {out['verdict']}")
                sinks = [(t["owner_class"], t["owner_uid"]) for t in trows if not t["is_source"]]
                fact(f"the same wire's SINK terminals: {sinks}")
                out["sinks"] = sinks
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)

    m1 = md5(MAIN)
    out["main_md5_after"] = m1
    gate("L0b MAIN md5 after", m1 == ORIG_MD5, m1)
    g._lv = None
    print("\n--- FACTS ---", flush=True)
    for line in facts:
        print("  " + line, flush=True)
    print(f"\n=== OpLoopEndRef_v0 build: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
