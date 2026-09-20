# priorart-priorart-loopendref-rev2

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $6.4735  in 64 / out 49388 / cache-create 223962 / cache-read 5997729  (724s, 46 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (728s)
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
TWO RECIPES ARE UNDER REVIEW IN ONE PASS. Both were edited AFTER an earlier review, which re-armed
guard_cycle's premature-build gate, so both are re-submitted together.

(1) tools/recipes/build_oploopendref_v0.py - REV 2. Round 1 is archive/peer/2026-09-17-priorart-priorart-loopendref.md
    (7 verdicts, B1 = genuinely novel). ALL SEVEN were accepted and are implemented in the text below; the
    disposition is written in that file under '## What was done with it'. Judge the CURRENT text: did the
    fixes land, and did they introduce a new prior-art problem?

(2) tools/recipes/probe_move_into_v0.py - REV 3. Run 1 (tools/bench/probe_move_into_v0.log) stopped at gate P1,
    in the probe's own harness, before reaching the question. Cause MEASURED in tools/bench/diag_u2g_terminals.log.
    Only phase 1's terminal resolution changed.

===================== FILE 1: tools/recipes/build_oploopendref_v0.py =====================
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

===================== FILE 2: tools/recipes/probe_move_into_v0.py =====================
r"""probe_move_into_v0.py - D1 phase P: CAN AN EXISTING NODE BE REPARENTED INTO ANOTHER DIAGRAM BY SCRIPT?

THIS IS THE ONE FACT D1 TURNS ON, AND IT HAS NEVER BEEN MEASURED (docs/d1-build-plan.md s1).

REV 3, 2026-09-17: run 1 stopped at gate P1 - not on the question, on the probe's own harness. `net_map` returned
only the FIRST FOUR of `UID to GObject Reference.vi`'s TWELVE terminals, and the VI-reference input is named
**'Owning VI'**, which the name test could never match (log:78-80). MEASURED, not guessed, by
`tools/bench/diag_u2g_terminals.py` (conpane of the VI file + node_terms_uid of the dropped instance, 5/5). Phase 1
now resolves every terminal through `node_terms_uid` by exact name, and finds the VI reference by following the
wire that already feeds the Traverse node's 'VI Refnum'. Nothing about phases 2-4 changed: the question P2/P3 ask
is untouched, and run 1 never reached it.

REV 2 after archive/peer/2026-09-17-priorart-priorart-d1-build.md (findings A1, A6, B1, B2). Rev 1 claimed the
whole relocation question was unexercised. It is not: `tools/recipes/probe_relocate_route.py:10-15` asked it in
2026-09-15 and DELIBERATELY excluded `GObject.Move` with an owner, because `create the loop -> drop the subVI in
it -> wire across the border -> delete the original` works and is now the project's settled method
(docs/decisions.md:19, docs/restructure-plan-4.6.md:79-81 - "GObject.Move is not needed"). That route covers
plain primitives and subVI calls. It does NOT cover a STRUCTURE WITH ITS CONTENTS, and the frame loop's forward
slice contains six of those (#5540 #2222 #12589 #10407 #1359 #29874), for which the fresh-build route is
OpCaseFrames_v0 - which failed five times and must not be retried. THAT, and only that, is what this probe is for.

The documented route for a wired fragment is `Make Selection` 0x6349002 -> `Copy Selection` 0x6349003 ->
`AbstractDiagram.Paste` 0x6375400 onto the SUBDIAGRAM reference (.claude/skills/labview-automation/references/
vi-scripting.md:323-325; archive/peer/2026-09-13-scripted-diagram-selection.md:143,:162,:166-172, whose forum
citation says explicitly "including contents of a structure frame"). It is a new op family and a separate cycle.
This probe measures the CHEAPER route first because our own `move_out` already contradicts that exchange's
general claim ("GObject.Move is not a cross-VI reparenting method") for the WITHIN-VI case.

WHAT ALREADY EXISTS - checked before writing a line (CLAUDE.md "before creating any new op"):
  * `gscript.move_out()` / `OpMoveOut_v0.vi` (gscript.py:2469, tools/recipes/build_opmoveout.py) already proves
    `GObject.Move` 632A400 with a wired `owner` reparents a node from a NESTED diagram to the VI's TOP-LEVEL
    diagram. Its `owner` is hard-wired to a `VI.Block Diagram` (23C) Property node, which is why it can only ever
    reach the top level. It is the DONOR here, not the answer.
  * `gscript.move_object()` / `OpMove_v0` (gscript.py:2094) moves by POSITION with `owner` UNWIRED = same diagram.
    docs/toolkit-capabilities.md:363-392 records a probe that believed position alone reparented a node and was
    then CORRECTED - "ExecState was already 0 immediately after for_loop". So position-only reparenting is
    unproven and is not assumed here.
  * `copy_by_index()` (gscript.py:1282) copies an object into a target's TOP-LEVEL diagram through the NI Move
    example fixtures and requires the target to be runnable before it saves - it cannot place into a nested
    diagram and cannot relocate inside one VI. Not a route.
  * `UID to GObject Reference.vi` (C:\...\vi.lib\VIServer\) is already used as node 990 of `OpWireSource_v5` and
    by `OpOwnerChain_v1` (tools/recipes/build_opownerchain_v1.py:170) - that is where the UID-addressing comes
    from; nothing is hand-rolled.
  * readers used: report/report_all/net_map/subvis/exec_state/ownerchain via `OpOwnerChain_v1`, delete_object,
    connect2, wire, drop_subvi, create_control, remove_bad_wires_scripted, loop_in - all in
    docs/toolkit-capabilities.md.
  * `grep -n "move" tools/gscript.py` shows no *move-into-a-diagram* helper. `ls tools/recipes | grep -i move`
    shows build_opmove.py / build_opmovebyindex.py / build_opmoveout.py only.

WHY IT DECIDES D1. The tracking kernel's FORWARD SLICE is 14 nodes (docs/frame-loop-wire-graph.md:45), five of
them structures, plus the reseed case #5540 and two shift registers. D1 rows 1.2/1.7 put those on NEW loops. The
fleet can CREATE a loop inside an existing VI and DROP a subVI in it (probe_migrate_v2 3/3, probe_migrate_v3 5/5)
- it has never MOVED existing code into one. If P2/P3 fail, D1 as specified is not buildable with today's fleet
and that is a judgement-session decision, not a third attempt.

PREDICTION CONTRACT
  P0  the original's md5 is 2a78e17c449cacdaf5da389818526859 before AND after; no original is opened for writing.
  P1  OpMoveIn_v0.vi builds from OpMoveOut_v0.vi (reference <- a UID-addressed GObject; owner <- the existing
      Traverse-"Diagram"[index] cast, i.e. the DESTINATION diagram) and reads ExecState 1.
  P2  on a scratch copy of the original: a PLAIN node (#8885 Multiply, on Diagram 43) moves into the body diagram
      of a While loop freshly created on Diagram 19 - afterwards OpOwnerChain_v1 reads
      8885 -> <new body diagram> -> <new WhileLoop>.
  P3  a STRUCTURE (#12589 CaseStructure, on Diagram 43) moves the same way AND ITS CONTENTS COME WITH IT:
      ownerchain(12589) -> <new body diagram>, and the VI's total Diagram count is unchanged by the move
      (a frame diagram destroyed or orphaned would change it).
  P4  no node is lost: total Node count after both moves == before. ExecState is expected to be 0 (wires were
      cut by the move) and that is NOT a failure; it is reported.
  P5  the scratch copy is deleted in the same run; LabVIEW handle count is recorded before and after.

Any of P1/P2/P3 failing stops the run and reports - no repair pass, no second construction (failure budget).

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/probe_move_into_v0.log \
        -- py -u tools/recipes/probe_move_into_v0.py
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = g.CLAUDEDEV
DONOR_OP = os.path.join(CLAUDEDEV, "OpMoveOut_v0.vi")
OPIN = os.path.join(CLAUDEDEV, "OpMoveIn_v0.vi")
U2G = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_d1move_{int(time.time())}.vi")

FRAME_BODY_UID = 639        # Diagram owned by WhileLoop #637 - the frame loop body
SIBLING_DIAG_UID = 686      # the FlatSequenceFrame diagram that holds #637 itself (main-vi-stop-and-save.md s0)
PLAIN_NODE = 8885           # Multiply, in the kernel's forward slice
STRUCT_NODE = 12589         # CaseStructure, in the kernel's forward slice

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
    try:
        import subprocess
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
        return out.strip()[:120]
    except Exception as e:
        return f"unavailable ({e})"


# ---------------------------------------------------------------- phase 1: build OpMoveIn_v0
def census(target, diagram=0, max_nodes=60):
    nodes, nets = g.net_map(target, diagram_index=diagram, max_nodes=max_nodes, max_terms=24)
    return nodes, nets


def find_term(nodes, want_names):
    """-> (node_index, uid, {name: (term_index, wire_uid)}) for the first node carrying ALL of want_names."""
    for n, (uid, _lbl, terms) in nodes.items():
        names = {nm: (ti, w) for ti, nm, w in terms}
        if all(x in names for x in want_names):
            return n, uid, names
    return None, None, None


def cls_index(target, uid):
    """(class_name, index-within-that-class) for an object uid, from report_all('Node')."""
    for o in g.report_all(target, "Node"):
        if o["uid"] == uid:
            cls = o.get("class") or o.get("Class Name") or ""
            same = [x["uid"] for x in g.report(target, cls)]
            return cls, same.index(uid)
    return None, None


def build_opmovein():
    print("\n=== PHASE 1: build OpMoveIn_v0 from OpMoveOut_v0", flush=True)
    if not os.path.exists(DONOR_OP):
        gate("P1 OpMoveIn_v0 builds", False, f"donor missing: {DONOR_OP}")
        return False
    if os.path.exists(OPIN):
        os.remove(OPIN)
    shutil.copyfile(DONOR_OP, OPIN)
    g.open_panel(OPIN)
    time.sleep(0.5)
    print(f"  donor copy ExecState {g.exec_state(OPIN)}  nodes {g.count(OPIN, 'Node')} "
          f"wires {g.count(OPIN, 'Wire')}", flush=True)

    nodes, nets = census(OPIN)
    for n, (uid, _l, terms) in sorted(nodes.items()):
        print(f"    node[{n}] uid {uid}: " + ", ".join(f"{ti}:{nm!r}=w{w}" for ti, nm, w in terms), flush=True)

    mv_n, mv_uid, mv_terms = find_term(nodes, ("reference", "owner"))
    if mv_n is None:
        gate("P1 OpMoveIn_v0 builds", False, "no node carries both 'reference' and 'owner' (the Move Invoke)")
        return False
    fact(f"Move Invoke = node[{mv_n}] uid {mv_uid}; owner term {mv_terms['owner']}, reference term {mv_terms['reference']}")

    owner_wire = mv_terms["owner"][1]
    ref_wire = mv_terms["reference"][1]

    # the node that DRIVES `owner` today is the VI.Block Diagram (23C) property node - delete it
    owner_src = [(n, t, nm) for n, t, nm in nets.get(owner_wire, []) if n != mv_n]
    fact(f"owner wire {owner_wire} also touches {owner_src}")
    # the Diagram-typed source we WANT is whatever drives the `Nodes[]` property node's `reference`
    nodes_n, nodes_uid, nodes_terms = find_term(nodes, ("Nodes",))
    if nodes_n is None:
        for n, (uid, _l, terms) in nodes.items():
            if any(nm.startswith("Nodes") for _ti, nm, _w in terms):
                nodes_n, nodes_uid = n, uid
                nodes_terms = {nm: (ti, w) for ti, nm, w in terms}
                break
    if nodes_n is None:
        gate("P1 OpMoveIn_v0 builds", False, "cannot find the Nodes[] property node")
        return False
    diag_wire = nodes_terms.get("reference", (None, 0))[1]
    diag_src = [(n, t, nm) for n, t, nm in nets.get(diag_wire, []) if n != nodes_n]
    fact(f"Nodes[] node[{nodes_n}] uid {nodes_uid}; its reference wire {diag_wire} driven by {diag_src}")
    if not diag_src:
        gate("P1 OpMoveIn_v0 builds", False, "cannot find the Diagram-typed cast that feeds Nodes[]")
        return False
    tmsc_n, tmsc_t, tmsc_name = diag_src[0]
    tmsc_uid = nodes[tmsc_n][0]

    # 1) cut the wire that feeds `reference` today (IA_n.element -> Move.reference)
    wl = [o["uid"] for o in g.report_all(OPIN, "Wire")]
    if ref_wire in wl:
        g.delete_object(OPIN, "Wire", wl.index(ref_wire))
        fact(f"deleted wire {ref_wire} (old Move.reference source)")
    # 2) delete the VI.Block Diagram property node that feeds `owner`
    for n, _t, _nm in owner_src:
        u = nodes[n][0]
        c, i = cls_index(OPIN, u)
        if c:
            g.delete_object(OPIN, c, i)
            fact(f"deleted {c}[{i}] uid {u} (old Move.owner source)")
    g.remove_bad_wires_scripted(OPIN)

    # 3) branch the Diagram cast into `owner`
    c, i = cls_index(OPIN, tmsc_uid)
    fact(f"Diagram cast uid {tmsc_uid} is {c}[{i}], output terminal {tmsc_t}:{tmsc_name!r}")
    mc, mi = cls_index(OPIN, mv_uid)
    try:
        g.wire(OPIN, c, i, tmsc_name, mc, mi, "owner", branch=True)
        fact("wired Diagram cast -> Move.owner (branch)")
    except Exception as e:
        gate("P1 OpMoveIn_v0 builds", False, f"cast -> owner wire raised: {str(e)[:160]}")
        return False

    # 4) drop UID to GObject Reference.vi, feed it the VI reference + a UID control, wire it into `reference`
    sv0 = g.uids(OPIN, "SubVI")
    g.drop_subvi(OPIN, U2G, 0, (300, 1000))
    new_sub = g.new_since(OPIN, "SubVI", sv0)
    if len(new_sub) != 1:
        gate("P1 OpMoveIn_v0 builds", False, f"drop_subvi added {len(new_sub)} subVIs")
        return False
    # REV 3, 2026-09-17, after run 1 failed here (tools/bench/probe_move_into_v0.log:78-80). MEASURED cause, not
    # inferred - tools/bench/diag_u2g_terminals.log: `UID to GObject Reference.vi` has TWELVE connector-pane
    # terminals (`conpane()` on the file itself: 0 'error out', 2 'GObject', 3 'dup Owning VI', 8 'error in (no
    # error)', 10 'UID', 11 'Owning VI'), and `node_terms_uid` on the dropped instance returns all twelve - while
    # `net_map` returned only the FIRST FOUR, which is why the name search found no input at all. The VI-reference
    # input is called **'Owning VI'**, so the old "'vi' and 'ref' in the name" test could never have matched it.
    # Every terminal below is therefore resolved through node_terms_uid, by EXACT name, never through net_map.
    def all_terms(node_uid, diagram=0):
        for cand in range(60):
            nu, rows = g.node_terms_uid(OPIN, diagram, cand)
            if not nu:
                return None, None
            if nu == node_uid:
                return cand, rows
        return None, None

    u2g_n, u2g_rows = all_terms(new_sub[0]["uid"])
    if u2g_rows is None:
        gate("P1 OpMoveIn_v0 builds", False, "the dropped UID->GObject VI is not visible to node_terms_uid")
        return False
    print(f"    U2G node[{u2g_n}] terminals: "
          + ", ".join(f"[{r['i']}]{r['name']!r}{'>' if r['is_source'] else '<'}" for r in u2g_rows), flush=True)
    byname = {r["name"]: r for r in u2g_rows}
    need = ("Owning VI", "UID", "GObject")
    fact(f"U2G terminals (node_terms_uid): {[(r['i'], r['name'], r['is_source']) for r in u2g_rows]}")
    if any(k not in byname for k in need):
        gate("P1 OpMoveIn_v0 builds", False,
             f"U2G lacks one of {need}; has {sorted(byname)} (diag_u2g_terminals.log said it has all three)")
        return False
    uid_term = byname["UID"]["i"]

    # The VI-reference SOURCE is found by following the wire that already feeds the Traverse node's 'VI Refnum'
    # input (measured: wire 467 on node uid 124, diag_u2g_terminals.log part C) rather than by guessing a node
    # name - the donor's own Open VI Reference is whatever object sources that wire.
    src = None
    for cand in range(60):
        nu, rows = g.node_terms_uid(OPIN, 0, cand)
        if not nu:
            break
        for r in rows:
            if r["name"] == "VI Refnum" and not r["is_source"] and r["wire"]:
                src = ("sink", nu, r["wire"])
    if src is None:
        gate("P1 OpMoveIn_v0 builds", False, "no node has a wired 'VI Refnum' input - cannot find the VI reference")
        return False
    vi_ref_wire = src[2]
    holder = None
    for cand in range(60):
        nu, rows = g.node_terms_uid(OPIN, 0, cand)
        if not nu:
            break
        for r in rows:
            if r["wire"] == vi_ref_wire and r["is_source"]:
                holder = (nu, r["name"])
    if holder is None:
        gate("P1 OpMoveIn_v0 builds", False, f"no SOURCE terminal carries the VI-reference wire {vi_ref_wire}")
        return False
    fact(f"VI reference wire {vi_ref_wire}; its source terminal is {holder[1]!r} of node uid {holder[0]}")
    oc, oi = cls_index(OPIN, holder[0])
    uc, ui = cls_index(OPIN, new_sub[0]["uid"])
    try:
        g.wire(OPIN, oc, oi, holder[1], uc, ui, "Owning VI", branch=True)
        fact("wired the VI reference -> U2G 'Owning VI' (branch)")
    except Exception as e:
        gate("P1 OpMoveIn_v0 builds", False, f"VI reference -> U2G wire raised: {str(e)[:160]}")
        return False
    new_ctl, lab = g.create_control(OPIN, u2g_n, uid_term)
    fact(f"UID control created: {lab!r} ({[o['uid'] for o in new_ctl]})")
    try:
        g.wire(OPIN, uc, ui, "GObject", mc, mi, "reference")
        fact("wired U2G 'GObject' -> Move.reference")
    except Exception as e:
        gate("P1 OpMoveIn_v0 builds", False, f"U2G -> Move.reference wire raised: {str(e)[:160]}")
        return False

    g.set_auto_error_handling(OPIN, False)
    es = g.exec_state(OPIN)
    if es != 1:
        g.remove_bad_wires_scripted(OPIN)
        es = g.exec_state(OPIN)
    if not gate("P1 OpMoveIn_v0 builds and is runnable", es == 1, f"ExecState {es}"):
        return False
    g.save(OPIN)
    fact(f"OpMoveIn_v0 saved; UID control label {lab!r}")
    return lab


# ---------------------------------------------------------------- the op wrapper
def move_in(target, node_uid, dest_diagram_index, position, uid_label):
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
    vi.SetControlValue(uid_label, int(node_uid))
    vi.SetControlValue("position", tuple(int(v) for v in position))
    g._run(vi)
    return int(vi.GetControlValue("UID"))


def diag_index(target, uid):
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


OWNER_OP = os.path.join(CLAUDEDEV, "OpOwnerChain_v1.vi")
OWNER_LABELS = os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json")
_OL = None


def owner_of(target, uid):
    """(owner class, owner uid) via OpOwnerChain_v1 - the reader built for exactly this question
    (docs/toolkit-capabilities.md:49). Driving code mirrors `read_owner()` of
    tools/recipes/build_opownerchain_v1.py:246 VERBATIM except that the target path is a parameter there it is
    hard-wired to MAIN - outputs are POISONED first so a property read that never ran cannot pass for an answer."""
    global _OL
    if _OL is None:
        import json
        with open(OWNER_LABELS, encoding="utf-8") as f:
            _OL = json.load(f)
    lab = _OL
    vi = g.op(OWNER_OP)
    for k in (lab["ownercls"], "Class Name 3", lab["cast_class"]):
        try:
            vi.SetControlValue(k, "POISON")
        except Exception:
            pass
    vi.SetControlValue(lab["owner_uid"], 0)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", 0)
    vi.SetControlValue(lab["uid_in"], int(uid))
    vi.SetControlValue(lab["term_index"], 0)
    g._run(vi)
    return vi.GetControlValue(lab["ownercls"]), int(vi.GetControlValue(lab["owner_uid"]))


# ---------------------------------------------------------------- phase 2: the real question
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    m0 = md5(ORIGINAL)
    gate("P0a original md5 before", m0 == ORIG_MD5, m0)
    if m0 != ORIG_MD5:
        return 1
    print(f"  handles/tasklist before: {handles()}", flush=True)

    uid_label = build_opmovein()
    if not uid_label:
        print("\nSTOP after phase 1 (failure budget: no repair pass).", flush=True)
        return 1

    print("\n=== PHASE 2: move real nodes of the frame loop into a new sibling While loop", flush=True)
    shutil.copy2(ORIGINAL, SCRATCH)
    try:
        g.open_panel(SCRATCH)
        n_before = g.count(SCRATCH, "Node")
        d_before = g.count(SCRATCH, "Diagram")
        es0 = g.exec_state(SCRATCH)
        fact(f"scratch copy: Node {n_before}, Diagram {d_before}, ExecState {es0}")

        sib_i = diag_index(SCRATCH, SIBLING_DIAG_UID)
        fact(f"Diagram#{SIBLING_DIAG_UID} (holder of WhileLoop#637) is Traverse index {sib_i}")
        dg0 = g.uids(SCRATCH, "Diagram")
        wl0 = g.uids(SCRATCH, "WhileLoop")
        g.loop_in("while", SCRATCH, sib_i, (2600, 2600))
        new_dg = g.new_since(SCRATCH, "Diagram", dg0)
        new_wl = g.new_since(SCRATCH, "WhileLoop", wl0)
        if not gate("P2a a While loop was created on the sibling diagram",
                    len(new_dg) == 1 and len(new_wl) == 1,
                    f"+{len(new_dg)} diagrams, +{len(new_wl)} while loops"):
            return 1
        body_uid = new_dg[0]["uid"]
        loop_uid = new_wl[0]["uid"]
        body_i = diag_index(SCRATCH, body_uid)
        fact(f"new WhileLoop uid {loop_uid}, body Diagram uid {body_uid} at Traverse index {body_i}")

        # ---- P2: a plain node (CONTROL ARM - the settled route already covers this; a failure here means the
        #      probe is broken, not the capability. docs/toolkit-capabilities.md:200-214.)
        body_i = diag_index(SCRATCH, body_uid)          # RE-RESOLVE by uid before every mutation (finding B2)
        r = move_in(SCRATCH, PLAIN_NODE, body_i, (60, 60), uid_label)
        oc, ou = owner_of(SCRATCH, PLAIN_NODE)
        oc2, ou2 = owner_of(SCRATCH, ou) if ou else (None, None)
        gate("P2 a PLAIN node reparents into the new loop body",
             ou == body_uid and ou2 == loop_uid,
             f"move returned {r}; owner({PLAIN_NODE}) = {oc}#{ou} (want Diagram#{body_uid}); "
             f"owner(owner) = {oc2}#{ou2} (want WhileLoop#{loop_uid})")

        # ---- P3: a structure, with its contents  <- THE QUESTION
        d_mid = g.count(SCRATCH, "Diagram")
        body_i = diag_index(SCRATCH, body_uid)          # RE-RESOLVE by uid again (finding B2)
        r2 = move_in(SCRATCH, STRUCT_NODE, body_i, (60, 400), uid_label)
        oc3, ou3 = owner_of(SCRATCH, STRUCT_NODE)
        d_after = g.count(SCRATCH, "Diagram")
        gate("P3 a STRUCTURE reparents AND keeps its frame diagrams",
             ou3 == body_uid and d_after == d_mid,
             f"move returned {r2}; owner({STRUCT_NODE}) = {oc3}#{ou3} (want Diagram#{body_uid}); "
             f"Diagram count {d_mid} -> {d_after}")

        # ---- P4: nothing lost
        g.remove_bad_wires_scripted(SCRATCH)
        n_after = g.count(SCRATCH, "Node")
        es1 = g.exec_state(SCRATCH)
        gate("P4 no node lost by the two moves", n_after == n_before + 1,   # +1 = the new While loop node
             f"Node {n_before} -> {n_after}; ExecState now {es1} (0 expected: wires were cut)")
        fact(f"ExecState after the moves and Remove Bad Wires: {es1}")
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("  scratch deleted", flush=True)
            except Exception as e:
                print(f"  scratch NOT deleted: {e}", flush=True)
        m1 = md5(ORIGINAL)
        gate("P0b original md5 after", m1 == ORIG_MD5, m1)
        print(f"  handles/tasklist after: {handles()}", flush=True)

    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== probe_move_into_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())

===================== EVIDENCE: tools/bench/diag_u2g_terminals.log =====================
BGRUN START 2026-09-17 04:03:01 limit 10.0 min: py -u tools/bench/diag_u2g_terminals.py
  PASS  D0a original md5 before  2a78e17c449cacdaf5da389818526859

=== A: the connector pane of the U2G VI itself (authoritative index -> label)
    conpane[0] = 'error out'
    conpane[1] = None
    conpane[2] = 'GObject'
    conpane[3] = 'dup Owning VI'
    conpane[4] = None
    conpane[5] = None
    conpane[6] = None
    conpane[7] = None
    conpane[8] = 'error in (no error)'
    conpane[9] = None
    conpane[10] = 'UID'
    conpane[11] = 'Owning VI'
  PASS  D1 conpane(U2G) returned a non-empty map  12 terminals

=== B: the U2G VI's own front-panel labels
    [(0, 'Owning VI', False), (1, 'UID', False), (2, 'error out', True), (3, 'error in (no error)', False), (4, 'dup Owning VI', True), (5, 'GObject', True)]

=== C: the DROPPED instance in OpMoveIn_v0.vi (left by the failed probe run)
    SubVI objects: [(464, None), (399, None), (243, None), (124, None)]
    node[1] uid 124 (12 terminals):
        [0] 'error out'  is_source=True  wire=0
        [1] '# of Refs'  is_source=True  wire=0
        [2] 'References'  is_source=True  wire=600
        [3] 'dup VI Refnum'  is_source=True  wire=0
        [4] ''  is_source=False  wire=0
        [5] 'Other Refnum'  is_source=False  wire=0
        [6] 'Traverse Generated Code (F)'  is_source=False  wire=0
        [7] 'Traverse Target'  is_source=False  wire=415
        [8] 'error in (no error)'  is_source=False  wire=0
        [9] ''  is_source=False  wire=0
        [10] 'Class Name'  is_source=False  wire=373
        [11] 'VI Refnum'  is_source=False  wire=467
    node[4] uid 243 (16 terminals):
        [0] 'Diagram in'  is_source=False  wire=0
        [1] 'ID String'  is_source=False  wire=312
        [2] 'location (0, 0)'  is_source=False  wire=742
        [3] ''  is_source=False  wire=0
        [4] 'Diagram out'  is_source=True  wire=0
        [5] 'reference'  is_source=False  wire=0
        [6] 'reference out'  is_source=True  wire=0
        [7] 'Inputs'  is_source=False  wire=0
        [8] 'Outputs'  is_source=True  wire=0
        [9] 'error in'  is_source=False  wire=771
        [10] 'error out'  is_source=True  wire=0
        [11] 'error in (no error)'  is_source=False  wire=0
        [12] 'Class Name'  is_source=False  wire=336
        [13] ''  is_source=False  wire=0
        [14] ''  is_source=False  wire=0
        [15] 'error out'  is_source=True  wire=0
    node[12] uid 399 (8 terminals):
        [0] 'error out'  is_source=True  wire=0
        [1] ''  is_source=False  wire=0
        [2] ''  is_source=False  wire=0
        [3] 'specific error cleared?'  is_source=True  wire=0
        [4] 'error in (no error)'  is_source=False  wire=739
        [5] ''  is_source=False  wire=0
        [6] ''  is_source=False  wire=0
        [7] 'specific error code to clear (0: all)'  is_source=False  wire=0
    node[15] uid 464 (12 terminals):
        [0] 'error out'  is_source=True  wire=0
        [1] ''  is_source=False  wire=0
        [2] 'GObject'  is_source=True  wire=0
        [3] 'dup Owning VI'  is_source=True  wire=0
        [4] ''  is_source=False  wire=0
        [5] ''  is_source=False  wire=0
        [6] ''  is_source=False  wire=0
        [7] ''  is_source=False  wire=0
        [8] 'error in (no error)'  is_source=False  wire=0
        [9] ''  is_source=False  wire=0
        [10] 'UID'  is_source=False  wire=0
        [11] 'Owning VI'  is_source=False  wire=0
  PASS  D2 node_terms sees the dropped U2G with its terminals  [(1, 124, 12), (4, 243, 16), (12, 399, 8), (15, 464, 12)]
  PASS  D2b node_terms reports MORE terminals than net_map's four  16 terminals
  PASS  D0b original md5 after  2a78e17c449cacdaf5da389818526859

=== diag_u2g_terminals: 5 pass, 0 fail ===
BGRUN END rc=0 after 58s


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Narrative relocated **verbatim** (rule 4): cycle 11??3 ??`archive/2026-09-16-status-cycles-11-13-narrative.md`;
D0 (15??8), the GPU numbers, the lock history and the long OPEN forms ??**`archive/2026-09-17-status-d0-and-gpu-narrative.md`** (STATUS was 268 lines). Open one only when a line here is ambiguous.
?좑툘 **ONE SESSION AT A TIME** (two ran concurrently on 2026-09-16) ??**re-read `CLAUDE.md` and this from disk**.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`cycle10-plan.md` superseded = its Phase A); settled decisions
   **`docs/decisions.md`**; current cycle plan `docs/cycle14-plan.md`.
2. ??**Prior-art gate live, hole fixed** ??`guard_cycle.py` accepts `REFUTED:` and `FIXED: <slug> - <path>:<line> - <what>`.
3. ??**Retrospectives 10??3 done/disposed**; `retrospective.py` **v2** fixes slug saturation (`tools/bench/retro_v2_comparison.md`).
4. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** (not "diagram loaded" ??refuted); fixed by `ensure_loaded()` in `tools/gscript.py`, 26 mutating wrappers.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-preconditions
  since: 2026-09-17 03:5x
  purpose: probe_move_into_v0 on a SCRATCH COPY, then build OpLoopEndRef_v0 and read WhileLoop#637's
    conditional terminal on the MAIN VI read-only. Original md5 2a78e17c449... asserted before and after.
# 2026-09-17 03:0x-04:0x material/cycle15-d1-build: **NO LabVIEW was ever started** - the D1 phase-P probe was
# written and gated but never ran (guard_cycle: violations due). Original md5 verified 2a78e17c449... untouched.
# 2026-09-17 material/gpu-n1-localise: NO LabVIEW touched (DLL + recorded files only, ctypes; no COM anywhere in
# the import chain) - gates G0a/G0b assert tasklist shows no LabVIEW.exe at start and at end.
# Holder history (cycle15 D0 v1/v2/v3, md5s, scratch copies created+deleted, TIFFs written+deleted, GUI action
# counts): archive/2026-09-17-status-d0-and-gpu-narrative.md 짠1. Earlier: the 2026-09-16 narrative archive.
```
**Never assume an instance exited** (pid 14352 did not): `tasklist | grep -i labview`, kill strays. Fresh instances
??1,500 handles; unique scratch VI name per run, deleted in the same run.

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
**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` / `instrument-libraries` / `frame-loop-wire-graph` /
`rotor-sign-diagnosis` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS** (`docs/stage2-plan.md`): `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi`
162/162. **Say it exactly:** bit-identical to the reference for the **first 10,018 frames only** (before the first
bead loss), and both are **replay** artefacts ??recorded TIFFs, `FOR` loops, no acquisition, no stop protocol.
**THE GAP (outcome review):** 168 op VIs, 116 recipes, 217 peer exchanges ??two replay VIs, **zero runnable
experimental VIs**.

## OPEN ??one line each; the long form is in the narrative archives

1. ?윞 **PERIODIC auto-reset not gated by `Auto-Reset` at the wire level** (`ForLoop#1359`, 10 terminals, 0 panel sources); one `Value` read inside #1359 closes it. ??2026-09-16 archive, OPEN 1.
2. ?윟 **Autofocus CLOSED** ??`Auto-Focus` uid 24266 stops the piezo; `CaseStructure #10407` every 25 frames ??3.6 Hz.
2c. ?윟 **uid 9775 READS camera geometry** (the size written is the panel display area, not the ROI) ??the 1280횞1024 budget basis is safe. Residual: `Property Items[] ??Is Write` over the 106 Property nodes.
3. ?윞 **Peer-archive dispositions** ??39 pre-09-15 `legacy`; **27 are real debt** (L6); L1: 64/336 docs lack frontmatter.
5. **Startup drives instruments** (ASI diagrams 10/88, PI 1/3/4/5 ??`main-vi-startup.md:22-33`): fine while apart, a hard blocker at assembly; excise node-by-node (rule 1a).
6??. ??RESOLVED ??bgrun regex, REVIEW-log scan skip, `premature-build`/`scope-creep` devices. 4. `Global motor pos.vi` write-only; **user: keep it**.
9. ?윟 **A2 DONE** ??owner semantics, six structure classes (54/54); `FlatSequence` the exception (owner uid 0, error 1055). `docs/diagram-hierarchy.md`.
10. ?윟 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree); left: the 57 `FlatSequenceFrame` diagrams, reachable via `FlatSequence.Diagrams[]` **3578BC00**. ?윞 Needs ONE new op VI ??judgement call.
11??2. ??**Retrospective v2 ADOPTED** (A?밇 closed, `violations.py --due` empty rc=0); **doc lint + ingest BUILT**, but
   MEASURED 2026-09-17: **2 fail / 4 warn / 3 pass** ???뵶 L4 *two* `current` cycle plans (14 + 15) and L6 27 undisposed
   reviews; the "1 fail/3 warn/5 pass" figure is stale. ??archive 짠2.
13. ?윟 **Cycle 15 step 1(b)(c) MEASURED ??`docs/main-vi-stop-and-save.md`.** ?윞 Left: which `Diagram#639` sink of wire
   3457 is `WhileLoop#637`'s cond terminal ??**guessed twice ??build the READER** (recursive `ControlTerminal`
   census, then `WhileLoop.Loop End Ref` 0x06362C00). ??archive 짠2.
14. ?뵶 **The cycle-15 prior-art review is only PARTLY disposed** ??A1/A2 `settled-already`, A3?밃6/B2 `contradicted`,
   A7/B3 `unread-evidence` BLOCK on purpose (D1's method vs `decisions.md:19`; `SubVI.Replace` 635E001 unverified).
   **Only a judgement session may refute or fix those.** ??archive 짠2.
15. ??**`bgrun.py --detach` BUILT and MEASURED** (deadline + END/TIMEOUT survive detachment; `BGRUN KILL` line;
   detached stdout ??the log). 15b. ?뵶 **its deadline kill does NOT kill an ORPHANED grandchild**
   (`detach_canary.log`) ??pre-existing; the Job-Object fix is a **judgement call**. ??archive 짠3.
16. ?뵢 **GPU N1, full fixture: max |?x| 4.13e-06 px 쨌 |?y| 3.13e-05 px 쨌 |?z| 1.28e-05 쨉m 쨌 1 flip** vs acceptance
   `decisions.md:38` (x,y ??1e-6, 0 flips) ??**x/y and the flip are OUTSIDE it**. **LOCALISED 2026-09-17**
   (`docs/gpu-backend.md` 짠2026-09-17, raw `tools/bench/gpu_n1_deltas.json`, 8/8 gates): every x/y exceedance is
   **bead 4 on 10 frames of f11805?밼11823**, in the all-beads-lost tail, interleaving the 13 recorded lost rows;
   **over the first 10,018 frames max |?x| 4.86e-07 쨌 |?y| 4.68e-07 쨌 0 exceedances**; the flip is k1679/f1937
   bead 4, one cal slice (?z 4.7 nm); **two runs bit-identical**. ?뵶 **Acceptability is a JUDGEMENT call.**
17. ??**D0 CLOSED ??the original's full unattended cycle RAN, 16 pass / 0 fail** (`drive_original_copy_v3.py`,
   HWND-gated clickprobe, `SetControlValue` stop ??idle in 2 s, `tra001-000` written, md5 unchanged). ??archive 짠5.
17b. ?뵶 **v3's R11 never gated on the stop** ??`rec(..., left2, ...)` (`drive_original_copy_v3.py:415-418`) scores the
   *restart*, and `reset_controls()` runs only at line 248, so "stop works only in the frame loop" is **UNPROVEN**
   (peer `??026-09-17-d0v3-stop-heuristic.md`, ANSWERED, adopted). Next D0 step is its VI-Server-only test: stops
   `False` + readback ??restart ??one `True` each ??poll values + `ExecState`.
19. ?뵶 **D1 REV 2 (`docs/d1-build-plan.md`) is written and prior-art-reviewed; the build did NOT start.**
   `archive/peer/2026-09-17-priorart-priorart-d1-build.md` ??**10 findings, 0 novel, all accepted and disposed**
   (`FIXED:` 횞6). The two that change the cycle: **(A1+A6)** relocating a plain primitive or a subVI call is the
   *settled* route (`decisions.md:19`, `restructure-plan-4.6.md:79-81`, and `tools/recipes/probe_relocate_route.py`
   asked this in cycle 8) ??so D1's ONLY real unknown is **relocating a STRUCTURE WITH ITS CONTENTS**
   (`#5540 #2222 #12589 #10407 #1359 #29874`), whose documented route is `Make Selection` 0x6349002 ??
   `Copy Selection` 0x6349003 ??`AbstractDiagram.Paste` 0x6375400 (`vi-scripting.md:323-325`) and **has never been
   run here**; **(A4)** `#10407` (autofocus) is in the kernel's forward slice and **neither placement is legal** ??
   tracking loop = VISA on a path whose stall makes acquisition skip reads (rule 1c / `decisions.md:30`),
   acquisition loop = its input no longer exists. ?뵶 **JUDGEMENT.** Also A5 (writer must STREAM, not relocate the
   accumulator), A3 (`#11639` AND `#17883` are two nodes; `CaseStructure#22082` unplaced), A2 (row 1.7 before the
   per-frame measurement `decisions.md:46,:52`). Probe written, gated, unrun: `tools/recipes/probe_move_into_v0.py`.
20. ?뵶 **Cycle 14's retrospective ran** (`archive/peer/2026-09-17-retrospective-cycle14.md`, ANSWERED) and left
   **two slugs DUE, which now BLOCK every recipe build**: `repeated-failure-class` 7/3 (the 2026-09-16 disposition
   gate **failed at its in-flight edge**) and `device-failed` 1/1 (the `unreported-fact` runner-exit device let
   `diag_stop_condterm_panel.log:15-18` end **rc=0 with a failed gate**). Each needs a dated `DECISION:` block in
   `docs/violation-decisions.md`. Its finding 7 also flags *judgement taken inside material sessions*.
18. ?뵶 **The original saves EVERY FRAME as a 1.3 MB TIFF** (`IMAQ Write TIFF File 2` #22700, diagram 43) ??
   **~118 MB/s at 90 Hz**. Any unattended overnight harness must bound this or the disk fills in minutes.

## NEXT

?윟 **Slug block cleared** (`violations.py --due` empty, rc=0); the **OUTCOME REVIEW is RUN and disposed**
(`archive/peer/2026-09-16-outcome-review-20260916.md`, ANSWERED, **7 OUTCOME-VIOLATION slugs**).
?뵶 **BLOCKING, in order:** (1) the two DUE slugs of OPEN 20 ??`py tools/violations.py --due` rc=1; (2) OPEN 19's
three D1 design calls (`#10407`'s loop 쨌 streaming writer vs `.tra` format 쨌 row 1.7 before the p50/p99 measurement).
Then Phase P: `MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/probe_move_into_v0.log -- py -u
tools/recipes/probe_move_into_v0.py` (builds `OpMoveIn_v0`, control arm `#8885`, real question `#12589`).
?뵶 **Earlier JUDGEMENT item:** CLAUDE.md turns that into a **delivery** cycle, contradicting
`docs/cycle14-plan.md` (짠3 `Diagrams[]` op, 짠4 A3 ??170/170, 짠5 OPEN 1's read, 짠6 A4). Queued second: **is item
16's GPU divergence acceptable**, on the 2026-09-17 localisation.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
`docs/restructure-plan-4.6.md` target 쨌 `docs/pre-rig-master-plan.md` the plan 쨌 `docs/diagram-hierarchy.md` A2/A3 쨌
`docs/gpu-backend.md` GPU 쨌 narrative: the 2026-09-17 and 2026-09-16 status archives 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only, no lock taken, nothing built, run, or edited. I read `docs/`, `archive/peer/`, `tools/bench/*.log`, `tools/recipes/` and `tools/gscript.py` directly.

**Headline:** File 1 is released — all seven round‑1 verdicts landed, I opened every citation and each one says what the disposition claims. File 2 is not: REV 3 fixed the U2G terminal lookup but left a *second* defect that is visible in run 1's own log, and it hand‑rolls two helpers the project already owns (one of which carries exactly the fix that second defect needs).

---

# FILE 1 — `build_oploopendref_v0.py` REV 2

## Did the seven fixes land? Verified one by one, against the cited files

| round‑1 finding | citation I opened | landed? |
|---|---|---|
| A3‑i ordering | `docs/main-vi-stop-and-save.md:72-74` (the two‑step order), `docs/violation-decisions.md:281-290` (2026‑09‑17 03:38, "DECISION: device … build the reader `OpLoopEndRef_v0`", naming `0x06362C00` and the read‑only #637 verification) | **yes** — the docstring now states the real ordering and names the later dated decision as what supersedes it. The supersession is legitimate: `:285` says "STATUS OPEN 13 already names the reader", `:288` names only this one |
| A3‑ii zero branch | `tools/bench/drive_original_copy_v3.log:80-81` | **yes** — both the docstring and the `out["verdict"]` string read INCONCLUSIVE / READER SUSPECT |
| A3‑iii Abort citation | `docs/frame-ownership-design.md:105`; `docs/main-vi-stop-and-save.md:75-78` | **yes**, and the document itself was corrected — `:75-77` now cites `:105` and names the review |
| A4 unread evidence | `docs/toolkit-capabilities.md:510-511` — "fp_labels returns 114 objects and `report("ControlTerminal")` returns 114 — every front-panel object has exactly one diagram terminal in this VI" | **yes**, quoted accurately |
| B3‑i census not 1077 | `docs/toolkit-capabilities.md:234-238` ("'no 1077' is NOT a verdict that a property attached … Any 'does property X exist on class Y?' test must use that"), `docs/NAMES.md:241-247` (the Loop/ForLoop/WhileLoop id block is "not yet verified on this machine"; `WhileLoop: Loop End Ref 6362C00` at `:246`) | **yes** — L3 is the census |
| B3‑ii helpers imported | `tools/recipes/build_opcaseframes_v0.py:48-59` `prop_node(cls, pid, label, pos) -> (uid, name)` and `:62-71` `add_indicator(uid, name, key, labels)` | **yes**, and the call shapes match the real definitions; both read the module‑global `OP` at call time, so `CF.OP = OP` is a sufficient rebinding |
| B4 confirming not discovering | `tools/bench/test_oploopcast.log:84` | **yes** |

## PART A / PART B — no blocking prior art found in the current text

**A1/A2** — the direction is *ordered*, not refuted: `docs/violation-decisions.md:287-290`. No slug (a decision that mandates the build is not prior art that stops it).

**B1** — still genuinely novel. I re‑checked independently rather than trusting round 1: the only `6362C00` / `LpEndRef` hits in the project are this recipe, docs, peer logs, and NI **example** nodes seen during seeding (`tools/bench/build_opwhilecast_v0.log:34` node uid 291 terminal 4 `'LpEndRef'`; `tools/bench/probe_example_forloop.log:16`, same node with `HasConditionalTerm` two lines up at `:14` — so that is the **ForLoop** id 6362002, not 6362C00). No op, recipe or claudeDev VI reads a While loop's conditional terminal.

### Three prose findings, deliberately **without** slugs — each would cost more to block than it saves

1. **Supporting evidence the docstring does not cite, which lowers L4/L5's risk.** `tools/recipes/build_oploopcast_v0.py:280-287` already builds and verifies the identical downstream shape on this donor lineage — `Tunnel['Outside Terminal']` → `Terminal['Connected Wire']` → `GObject['UID']`, each link exact‑class or upcast, `ExecState 1` at every step (`:276-279` is the gate the docstring does cite). So "a property node's reference output feeding a `Terminal`‑class property node" is already proven here. The residual risk — that `WhileLoop.Loop End Ref` returns something *other* than a Terminal ref, making PN_IS/PN_CW a **downcast** (the break recorded at `build_opcaseframes_v0.py:93-97` and `archive/peer/2026-09-15-opcaseframes-multiframe-to-casestructure-downcast.md:32`) — is real but bounded, and L4/L5 stop without saving, which is the coded response. Cheapest insurance if you want it: one `GObject.Class Name` read off PN_LER's output, the same practice `docs/NAMES.md:276-277` used for `Loop.Shift Registers[]`.
2. **`FRAME_DIAGRAM = 43` is a cached Traverse index.** It matches the record (`docs/main-vi-stop-and-save.md:26-29`: index 43 ↔ uid 639, same md5), but `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29` says not to assume a cached index survives sessions, and the sibling recipe in this same cycle re‑resolves by uid. I am **not** slugging it because the only consumer is `node_labels(MAIN, 43)` for a cosmetic label, and a wrong index yields an empty label rather than a wrong one — it cannot manufacture a false fact.
3. **Dead duplicates left by the REV‑2 edit:** `node_terms_of()` is now unreferenced (its callers `data_term`/`make_indicator` were deleted), and `import build_track_v6_core as B` is unused — while `B.walk()` (`tools/recipes/build_track_v6_core.py:84-92`) is the very helper `CF.prop_node`/`CF.add_indicator` use. Cosmetic; noted so it does not get copied forward.

---

# FILE 2 — `probe_move_into_v0.py` REV 3

## PART A

### A3 `contradicted` — the docstring's account of the fix contradicts the file 130 lines later

`probe_move_into_v0.py:9-10`: *"Phase 1 **now resolves every terminal through `node_terms_uid` by exact name**, and finds the VI reference by following the wire…"*, repeated at `:243`: *"Every terminal below is therefore resolved through node_terms_uid, by EXACT name, **never through net_map**."*

`:132` `census()` still calls `g.net_map`, and `:173-180` resolves the Move Invoke's `reference` **and `owner`** — the two terminals the whole op turns on — out of that `net_map` result via `find_term()`. The claim covers the U2G block only.

### A4 `unread-evidence` — run 1's cause was already written down, in two of our own files, before the new diagnostic ran

The docstring credits `tools/bench/diag_u2g_terminals.py` with measuring why `net_map` returned four of twelve terminals. Our files already said it:

- `tools/gscript.py:2352-2355` — the walker stops after three consecutive empty terminals, with the comment *"out-of-range terminal — OR an unassigned connector-pane slot of a subVI (**2026-09-07: those truncated the list**)"*. `UID to GObject Reference.vi` has empties at conpane slots 4–7 (`tools/bench/diag_u2g_terminals.log`, section A), which is precisely four terminals returned.
- `docs/toolkit-capabilities.md:482-485` — *"**SUPERSEDED 2026-09-14:** `node_terms` (OpNodeTerms_v0) reads every terminal of every `Nodes[]` node with direction and wire … the 'invisible object kinds' below were never invisible to the array readers, **only to the per-terminal walker's end-of-list heuristics**."* The capability row is `:23` (`node_terms` / `node_terms_uid`, ~0.8 s/node vs the walker's ~8 s/node).

This is not merely a citation gap: it is why the remaining `net_map` use at `:132`/`:173` is still the wrong reader, and `docs/toolkit-capabilities.md:294` records `net_map` on an op leaving the target `ExecState 0`. Run 1 paid ~35 s of walking plus ~15 s purging 313 junk Invokes out of a 69 s run for terminals the documented reader returns correctly.

## PART B

### B2 `already-failed` — the name-keyed terminal dict, and the failure is in this probe's own log

`find_term()` (`:137-144`) builds `names = {nm: (ti, w) for ti, nm, w in terms}` — keyed by **name only**. The Move Invoke has four duplicated names (measured, `tools/bench/probe_move_into_v0.log:44`: `8:'owner'=w872, 9:'owner'=w0`, same for `Move`, `position`, `duplicate`), so the dict keeps the **output** side. The run recorded it:

- `tools/bench/probe_move_into_v0.log:46` — `Move Invoke = node[13] uid 741; owner term (9, 0)` (index 9, wire 0 — the unwired output),
- `:47` — `owner wire 0 also touches []`, so the loop at `:182-187` that is meant to **delete the old `VI.Block Diagram` owner source (uid 744) never deletes anything**, and `:51` then branches the Diagram cast onto a name that resolves ambiguously on an already-wired input.

This exact defect class was diagnosed and its remedy adopted here a month ago:

- `archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29` — *"Duplicate-name dict entries selected the output-side … whose unwired `wire == 0` then falsely matched … **Require `(name, is_source)` and never source-match unless `wire != 0`**"*; `:47` records the fix adopted and the rebuild passing 5/5.
- `docs/toolkit-capabilities.md:242-244` (active doc) — *"the erdosmiller creator's connector pane has **two terminals named `error out`** … **Names do not carry direction**; `Terminal.Is Source?` (634A003) does."*

REV 3 states that only the U2G resolution changed, so this is untouched. **The cost if it ships:** `gscript.wire()` documents that *"a FOUND name whose connect is illegal is **declined silently**"* (`tools/gscript.py:1149-1152`) and the call passes `branch=True`, which disables the count check — so `OpMoveIn_v0` can be built with its `owner` still fed by `VI.Block Diagram`, move nodes to the **top level**, and return P2/P3 = FAIL. That reads as *"reparenting into a nested diagram is impossible with today's fleet"* — a false negative on the single question D1 turns on (`docs/d1-build-plan.md:123-130`).

### B3‑i `helper-exists` — both hand-rolled scanners already exist, and one of them *is* the fix for B2

`tools/recipes/build_track_v6_core.py:84-92`:
```python
def walk(target, diagram=0):          # uid-keyed, via node_terms_uid, the documented reader
def term(rows, name, source):         # :95-96 — matches (name, is_source), not name alone
```
`term()` is the direction-keyed lookup `find_term()` should be; `walk()` is `all_terms()` (`:244-251`) plus the two open-coded `for cand in range(60)` scans at `:272-278` and `:283-289`. Both are already imported and used by the sibling recipes (`build_opcaseframes_v0.py:37`, `build_opwiresource_v5.py:38`) — including the one this cycle's File 1 now imports.

### B3‑ii `helper-exists` — `owner_of()` drops the guards `read_owner()` exists to carry

`probe_move_into_v0.py:352-356` claims it *"mirrors `read_owner()` of `tools/recipes/build_opownerchain_v1.py:246` VERBATIM except that the target path is a parameter"*. I opened it. `read_owner` (`:246-279`) also returns **five error columns** (`errL, errT, errO, errU, errG`, `:268-269`) and the **`uid_back` / `cls_back` identity cross-check** (`:274-275`); its docstring `:247-248` says the poisoning exists *"so a property read that never ran is visible instead of being mistaken for an answer"*. `owner_of()` keeps the poison but returns only `(ownercls, owner_uid)` — so a read that **errored** and a move that **failed** both surface as `owner_uid == 0`, again on P2/P3. The identity gate is the one `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29` requires *"on every read"*. (`OWNER_LABELS = opwiresource_v5_labels.json` is correct — `build_opownerchain_v1.py:165`.)

## Where I found NO prior art for File 2 — and one premise I checked rather than assumed

- **P1's premise is sound, and the evidence is stronger than the docstring's citation.** `move_out` reparenting is not merely a docstring claim: `tools/bench/moveout_chain.log:36-37` shows `move_out -> 2471` followed by `top-level node uids after move: [2471, 874, …]` — the moved CLFN appearing in the **top-level** `Nodes[]`. Worth citing, since `docs/toolkit-capabilities.md:366` records the *other* probe (position-only `move_object`) as *"reparenting is inferred, not proven"*, and `archive/peer/2026-09-13-scripted-diagram-selection.md:162` asserts `GObject.Move` *"changes the position of an object within its existing owner"*.
- **P3 (a structure with its contents, by `GObject.Move` with an owner)** — still never attempted here, as the round‑1 d1 review found. Genuinely open.
- **No slug, but the cheapest upgrade available:** P3 tests "the contents came with it" only by total `Diagram` count (`:440`), matching `docs/d1-build-plan.md:128-129`. The direct test is one more call to the `owner_of` already in the script, and it is already measured‑good for this class — `docs/diagram-hierarchy.md:85` (`206 → CaseStructure#57 … agrees 3/3`) and `:92` (*"Five of the six classes behave like `CaseStructure`. Diagram → owner returns the structure's class and a usable uid"*).

---

## Verdicts

```
FILE 1 — tools/recipes/build_oploopendref_v0.py REV 2
PRIOR-ART: novel
    All seven round-1 verdicts verified as landed against their own citations
    (violation-decisions.md:281-290; main-vi-stop-and-save.md:72-74,:75-78;
     toolkit-capabilities.md:234-238,:510-511; NAMES.md:241-247;
     build_opcaseframes_v0.py:48-59,:62-71; drive_original_copy_v3.log:80-81;
     test_oploopcast.log:84). B1 re-verified independently: still novel.

FILE 2 — tools/recipes/probe_move_into_v0.py REV 3
PRIOR-ART: contradicted     (A3 — probe_move_into_v0.py:9-10,:243 "every terminal … never through net_map"
                             vs :132,:173-180, which resolve Move.owner/.reference out of net_map)
PRIOR-ART: unread-evidence  (A4 — tools/gscript.py:2352-2355 and docs/toolkit-capabilities.md:482-485,:23
                             already record the walker's end-of-list truncation and name node_terms_uid
                             as the reader; also :294)
PRIOR-ART: already-failed   (B2 — find_term() at :137-144 keys terminals by NAME only;
                             archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29,:47
                             and docs/toolkit-capabilities.md:242-244;
                             MEASURED failing in this probe's own tools/bench/probe_move_into_v0.log:44,:46-47)
PRIOR-ART: helper-exists    (B3-i — tools/recipes/build_track_v6_core.py:84-92 walk(), :95-96 term(name, is_source))
PRIOR-ART: helper-exists    (B3-ii — tools/recipes/build_opownerchain_v1.py:246-279, esp. :247-248,:268-269,:274-275;
                             archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29)
```

All four blocking slugs are File 2's, and all four are disposable by one edit apiece — key terminals by `(name, is_source)` via `build_track_v6_core.term()`, route the remaining `net_map` reads through `walk()`/`node_terms_uid`, and restore `read_owner`'s error and identity columns in `owner_of()`. File 1 is clear to build as written.

## Sources

(extract from answer)

## What was done with it

FILE 1 (`build_oploopendref_v0.py`) is verdict `novel` and was built as reviewed - no edit, no release needed.
All FOUR of FILE 2's slugs are ACCEPTED and fixed in `tools/recipes/probe_move_into_v0.py` REV 4, before it ran.
The `already-failed` finding is the one that mattered: it is a defect visible in the probe's own run-1 log that
would have produced a FALSE NEGATIVE on the question D1 turns on, and nothing in this session had noticed it.

FIXED: contradicted - tools/recipes/probe_move_into_v0.py:5-31 - the docstring no longer claims more than the
code does. `net_map` and the name-keyed `find_term()` are now GONE from the whole file (not just the U2G block):
`census()`/`find_term()` are deleted, the Move Invoke's `owner`/`reference` and the `Nodes[]` cast are resolved
through `walk()`/`term()`, so the claim and the file agree. (A3)

FIXED: unread-evidence - tools/recipes/probe_move_into_v0.py:9-16 - run 1's cause is credited to the files that
already recorded it, `tools/gscript.py:2352-2355` (the walker stops after three consecutive empty terminals; an
unassigned connector-pane slot looks like the end of the list) and `docs/toolkit-capabilities.md:482-485,:23,:294`
(that heuristic SUPERSEDED by node_terms/node_terms_uid), with `tools/bench/diag_u2g_terminals.log` demoted to
the machine confirmation it is. (A4)

FIXED: already-failed - tools/recipes/probe_move_into_v0.py:133-160,:200-241 - terminals are keyed by
`(name, is_source)` via `build_track_v6_core.term()`, so the Move Invoke's SINK `owner` (index 8, wire 872) is
used instead of run 1's unwired OUTPUT `owner` (index 9, wire 0). The delete of the old `VI.Block Diagram` owner
source is now ASSERTED to have happened, the sink is asserted bare before the connect, and new gate **P1a**
asserts after the connect that `Move.owner` is carried by a wire whose SOURCE is the Diagram cast. Without those
the probe could have moved nodes to the top level and reported "reparenting is impossible", which is the false
negative `archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29` and
`docs/toolkit-capabilities.md:242-244` exist to prevent. (B2)

FIXED: helper-exists - tools/recipes/probe_move_into_v0.py:76-77,:133-141 - `build_track_v6_core.walk()` and
`.term()` are imported and used; the hand-rolled `census()`, `find_term()`, `all_terms()` and both open-coded
`for cand in range(60)` scans are deleted. Only `wire_ends()` remains hand-written, and it is a wire index over
`walk()`'s rows that refuses to resolve wire 0. (B3-i)

FIXED: helper-exists - tools/recipes/probe_move_into_v0.py:376-425 - `owner_read()` now carries `read_owner()`'s
five error columns and the `uid_back`/`cls_back` identity echo (build_opownerchain_v1.py:247-248,:268-269,
:274-275), and `owner_of()` RAISES when the echo is not the uid asked for, so P2/P3 report "UNRESOLVED READ"
instead of scoring an errored read as `owner_uid == 0`. (B3-ii)

Two prose findings on FILE 1 taken but not slugged: the dead `node_terms_of()`/`B` import are left in place for
this run (cosmetic, and editing the recipe would re-arm the premature-build gate on a file this review released);
`FRAME_DIAGRAM = 43` stays a cached index because its only consumer is a cosmetic label lookup that can yield an
empty string but never a wrong fact. The suggested `GObject.Class Name` read off PN_LER is NOT added for the same
gate reason; L4/L5 stop without saving, which is the coded response to the downcast risk it insures against.
On FILE 2, the optional per-frame owner re-check is declined in writing at
`tools/recipes/probe_move_into_v0.py:517-523`, on cost (~170 Diagram reads at ~1 s each), not on doubt.
