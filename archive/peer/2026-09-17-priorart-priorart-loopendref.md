# priorart-priorart-loopendref

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.5877  in 50 / out 37789 / cache-create 193021 / cache-read 3425002  (529s, 33 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (532s)
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
r"""build_oploopendref_v0.py - OpLoopEndRef_v0.vi: a While loop's CONDITIONAL TERMINAL, read from the machine.

THE DEVICE FOR `repeated-failure-class`, round 5 (docs/violation-decisions.md 2026-09-17 03:38, 7 occurrences):
"how does WhileLoop #637 stop" was diagnosed by INFERENCE twice - `diag_stop_condterm_panel`,
`diag_stop_save_seam` - and both were refuted, because no reader exists. CLAUDE.md: "the second time a class of
failure is explained by inference rather than read from the machine, the next build is the READER for it". STATUS
OPEN 13 and `docs/main-vi-stop-and-save.md:74,:164-165` both already name this exact reader as the mandated step.

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

PREDICTION CONTRACT (every value is asserted in the run)
  L0  MAIN md5 2a78e17c449cacdaf5da389818526859 before AND after; the main VI is only ever READ.
  L1  the copy of OpWhileCast_v0.vi opens at ExecState 1.
  L2  its TMSC is found by terminal names ('target class' + 'specific class reference').
  L3  each of the five property nodes is CREATED and the creator reports no error (build_property raises on
      1077, so a class/ID LabVIEW rejects stops the build instead of producing a silent no-op node).
  L4  after wiring TMSC -> PN_LER the VI is still ExecState 1. THIS IS THE REAL STRUCTURAL GATE: a
      WhileLoop-class property node accepts the cast output only if the seed genuinely typed the TMSC, and it is
      the same gate that proved the ForLoop chain (build_oploopcast_v0.py:276-279).
  L5  ExecState 1 after every remaining wire, and before the single save.
  L6  after `fresh()` (kill LabVIEW, COM-preflight, cold reload - `g.reset()` would only test memory,
      build_opownerchain_v1.py:456-460) the SAVED op is still ExecState 1.
  L7  FUNCTIONAL, read-only on the main VI: scanning Traverse indices of class WhileLoop, exactly one index
      returns LoopUID 637, and for it the op returns a conditional-terminal UID != 0 with no error.
  L8  the conditional terminal's `Connected Wire`: reported, NOT predicted. Both live hypotheses are recorded
      here so the outcome is machine-checkable either way -
        wire 3457  => the source is `CompoundArithmetic` #11639  (stop (end) uid 7 OR-ed;  main-vi-stop-and-save.md:48)
        wire 15229 => the source is `CompoundArithmetic` #17883  (stop (end) 2 uid 19587)
        0          => the conditional terminal is UNWIRED, i.e. #637 does not stop from a Boolean at all and
                      docs/frame-ownership-design.md:92-97's "the normal stop is LabVIEW's Abort" is the answer.
        anything else is a third answer and is reported as such.
      No branch of L8 is a failure; the gate is only that ONE source terminal resolves (OpWireSource_v5's own
      contract) when the wire is non-zero.
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
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402
from build_opwiresource_v5 import OP as OP_WS, MAP_OUT as MAP_WS, read_terminal  # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "OpWhileCast_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpLoopEndRef_v0.vi")
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


def data_term(uid):
    """A property node's data terminal is Terminals[4] (0 reference in, 1 error in, 2 reference out, 3 error out).
    Resolved BY INDEX and returned BY NAME - the donor recipe's own idiom (build_oploopcast_v0.py:281), so no
    property short-name is ever guessed."""
    _n, rows = node_terms_of(uid)
    if not rows:
        raise RuntimeError(f"node {uid} not on diagram 0")
    return next(r["name"] for r in rows if r["i"] == 4)


def make_indicator(uid, term_name):
    n, rows = node_terms_of(uid)
    t = next(r["i"] for r in rows if r["name"] == term_name)
    before = set(inds())
    g.create_indicator(OP, n, t)
    new = [l for l in inds() if l not in before]
    if len(new) != 1:
        raise RuntimeError(f"indicator on {term_name} of {uid}: {new}")
    return new[0]


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

    def pn(cls, pid, pos):
        r = g.build_property(OP, cls, [(pid, False)], pos)
        purge()
        return r[-1]["uid"]

    # PN_LER - the ONE new property. Its class must be WhileLoop: `Loop End Ref` is a WhileLoop property, not a
    # Loop one (docs/NAMES.md:246 lists it under WhileLoop; 6362002 under the For-loop table is a DIFFERENT id).
    try:
        u_LER = pn("VI Server:WhileLoop", P_LOOPENDREF, (900, 1150))
    except Exception as e:
        gate("L3a PN_LER WhileLoop['Loop End Ref'] created", False, f"EXC {str(e)[:200]}")
        return 1
    gate("L3a PN_LER WhileLoop['Loop End Ref'] created", True, f"uid {u_LER}")
    g.wire(OP, "Function", idx("Function", tmsc_uid), T_CAST_OUT,
           "Property", idx("Property", u_LER), "reference", branch=True)
    purge()
    es = g.exec_state(OP)
    if not gate("L4 the WhileLoop-class property node ACCEPTS the cast output", es == 1,
                f"ExecState {es} - if 0, the TMSC is not WhileLoop-typed or the property is not on this class"):
        print("STOP: nothing is saved (failure budget - no repair pass).", flush=True)
        return 1
    t_ler = data_term(u_LER)
    fact(f"PN_LER data terminal name {t_ler!r}")

    built = [("L3a", u_LER)]
    try:
        u_TUID = pn("VI Server:GObject", P_UID, (1250, 1100))
        g.wire(OP, "Property", idx("Property", u_LER), t_ler,
               "Property", idx("Property", u_TUID), "reference")
        purge()
        built.append(("L3b", u_TUID))
        u_IS = pn("VI Server:Terminal", P_ISSOURCE, (1250, 1250))
        g.wire(OP, "Property", idx("Property", u_LER), t_ler,
               "Property", idx("Property", u_IS), "reference", branch=True)
        purge()
        built.append(("L3c", u_IS))
        u_CW = pn("VI Server:Terminal", P_CONNW, (1250, 1400))
        g.wire(OP, "Property", idx("Property", u_LER), t_ler,
               "Property", idx("Property", u_CW), "reference", branch=True)
        purge()
        built.append(("L3d", u_CW))
        t_cw = data_term(u_CW)
        u_WUID = pn("VI Server:GObject", P_UID, (1600, 1400))
        g.wire(OP, "Property", idx("Property", u_CW), t_cw,
               "Property", idx("Property", u_WUID), "reference")
        purge()
        built.append(("L3e", u_WUID))
    except Exception as e:
        gate("L3 all five property nodes built and wired", False, f"EXC {str(e)[:220]}; built {built}")
        print("STOP: nothing is saved (failure budget - no repair pass).", flush=True)
        return 1
    gate("L3 all five property nodes built and wired", True, str([u for _k, u in built]))
    es = g.exec_state(OP)
    print(f"  {snap('assembled:')}", flush=True)
    if not gate("L5 the assembled op is legal", es == 1, f"ExecState {es}"):
        print("STOP: not saving a broken VI.", flush=True)
        return 1

    # ---- indicators + label map ----------------------------------------------------------------
    with open(DONOR_MAP, encoding="utf-8") as f:
        label_map = json.load(f)          # label -> meaning, inherited from OpWhileCast_v0
    wanted = [(u_TUID, "UID", "CondTermUID"), (u_WUID, "UID", "CondWireUID"),
              (u_IS, data_term(u_IS), "IsSource"),
              (u_LER, "error out", "LoopEndRefErr"), (u_IS, "error out", "IsSourceErr"),
              (u_CW, "error out", "ConnWireErr"), (u_WUID, "error out", "WireUIDErr")]
    for uid, term, meaning in wanted:
        try:
            label_map[make_indicator(uid, term)] = meaning
        except Exception as e:
            print(f"  indicator {meaning}: EXC {str(e)[:160]}", flush=True)
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
            fact(f"the conditional terminal of #{FRAME_LOOP} is UNWIRED - no Boolean drives it")
            out["source"] = None
            out["verdict"] = ("UNWIRED: WhileLoop#637's conditional terminal carries no wire, so the frame loop "
                              "is not stopped by either stop Boolean through this terminal.")
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

I could not write the plan file (the Write tool is disabled in this session), so the review is the reply — which matches the peer brief anyway ("your output is your answer, nothing else"). I took no lock, ran nothing, and opened no `.vi`.

# PRIOR-ART REVIEW — `build_oploopendref_v0.py` / `OpLoopEndRef_v0.vi` (trigger: new-op)

**Headline:** the *artifact* is genuinely novel — nothing in this project reads a While loop's conditional terminal, and I verified that rather than taking the plan's word for it. Every finding below is about **claims the plan makes and gates it sets**, each of which our own files already answer differently. Six of the seven are disposable by editing a docstring, one gate and one verdict string.

---

## PART A — THE DIRECTION

### A1 SETTLED ALREADY — *in favour*. **No slug emitted.**

`docs/violation-decisions.md:281-290` (**2026-09-17 03:38**, round 5):

> "7 occurrences. The cycle-14 instance is the stop CONDITIONAL TERMINAL of WhileLoop #637: diagnosed by inference twice (`diag_stop_condterm_panel`, `diag_stop_save_seam`), both refuted, because no reader exists … **DECISION: device** — build the reader `OpLoopEndRef_v0` (`WhileLoop.Loop End Ref` 0x06362C00 → the conditional terminal → its connected wire/source), functionally verified on the main VI's #637 (read-only) … It is also D1's S4 gate."

The direction is decided, by name, by ID, with the same verification shape the recipe implements. A decision that *orders* this build is not prior art that should stop it, so I emit **no `settled-already` slug**. Recorded so the disposition can cite it.

Ordering note, no slug: `STATUS.md:118-120` ("NEXT") makes Phase P (`probe_move_into_v0`) the next build while `docs/violation-decisions.md:288` makes this reader a due device, and CLAUDE.md's rule is that the device comes first. Two current documents, two different "next builds"; the device reading is the compliant one and STATUS's NEXT line is the stale half.

### A2 REFUTED ALREADY — no. **No slug.**

Nothing argues against building it. The two prior attempts were *inferences*, not builds (`archive/peer/2026-09-16-stop-condterm-failed-prediction.md`, `…-panel-fail2.md`, summarised at `docs/main-vi-stop-and-save.md:55-74`), and both peers pointed **at** this property as the conclusive route (`tools/bench/peer_stopterm.log:32-37`, `tools/bench/peer_stopterm2.log:49`).

### A3-i CONTRADICTED — "the mandated step" is the **second** of two ordered steps

Plan, `tools/recipes/build_oploopendref_v0.py:7`:
> "STATUS OPEN 13 and `docs/main-vi-stop-and-save.md:74,:164-165` both already name this exact reader as the mandated step."

`docs/main-vi-stop-and-save.md:72-74`:
> "Cheapest remaining test, **in order**: (1) a **recursive** front-panel census — `Traverse for GObjects` over `ControlTerminal`, each terminal's `Connected Wire` vs 3457; (2) **only if that finds no second carrier**, a new reader for `WhileLoop.Loop End Ref` 0x06362C00 on uid 637."

`STATUS.md:78-79`: "**guessed twice ⇒ build the READER** (recursive `ControlTerminal` census, **then** `WhileLoop.Loop End Ref` 0x06362C00)." Both peers said the same independently — `tools/bench/peer_stopterm.log:39`, `tools/bench/peer_stopterm2.log:58` ("**Only if** that returns no second carrier should you build the `Loop End Ref` reader").

The later decision (A1) supersedes the ordering, and skipping step (1) is defensible — step (1) needs a new terminal-by-UID reader of its own, since `panel_wiring` is documented non-recursive (`tools/gscript.py:640`) and `OpWireSource_v5` returns a terminal's *owner*, not its own UID (`docs/toolkit-capabilities.md:48`). What is wrong is the **claim about what those two documents say**.

### A3-ii CONTRADICTED + ALREADY MEASURED — the `Connected Wire == 0` branch is refuted before the run

Plan, `build_oploopendref_v0.py:59-60` and the verdict it writes at `:357-360`:
> "0 => the conditional terminal is UNWIRED, i.e. **#637 does not stop from a Boolean at all** …" / `"UNWIRED: WhileLoop#637's conditional terminal carries no wire, so the frame loop is not stopped by either stop Boolean through this terminal."`

Measured functionally on a running copy — `tools/bench/drive_original_copy_v3.log:80-81`:
> `STEP 10 R9 stop via the VI's own control VISERVER PASS SetControlValue -- idle after 2s, 1 re-arms`
> `STEP 11 R10 trace file written FILE PASS … ['cal001 (171552 B)', 'tra001-000 (196282 B)']`

and `archive/2026-09-17-status-d0-and-gpu-narrative.md:212-213` ("✅ **WORKS — idle after 2 s** … `tra001-000` … written by `save N xyz traces.vi` **because the VI stopped properly**").

`save N xyz traces.vi` #6384 sits on diagram 19, **after** the frame loop (`docs/main-vi-stop-and-save.md:80`), so that file is evidence `WhileLoop#637` terminated normally from the stop Booleans, not by Abort. A zero therefore cannot mean "#637 does not stop from a Boolean"; it would mean the reader or the addressing is wrong. Rewrite the branch so zero reads as *inconclusive / reader suspect*. (`STATUS.md:105-108` disputes only the *restriction* "only in the frame loop" — R11 scored the restart; the R9/R10 result stands.)

### A3-iii CONTRADICTED — the Abort citation points at superseded camera text

Plan `:60` cites "`docs/frame-ownership-design.md:92-97`'s *the normal stop is LabVIEW's Abort*". Lines 92-97 are the **superseded** overload paragraph ("the camera free-runs into the driver's ring buffer … `Buffer Number Mode = Last` … no pool eviction, no `Lossy Enqueue Element`"). The Abort sentence is `docs/frame-ownership-design.md:105`. The wrong numbers were inherited from `docs/main-vi-stop-and-save.md:75`, which carries the same error — fix both. And :105 speaks about the **new design's** operator, which `docs/main-vi-stop-and-save.md:75-76` says the wiring measurement "does not contradict or confirm".

### A4 UNREAD EVIDENCE — the cardinality bearing on the skipped step (1)

`docs/toolkit-capabilities.md:510-511`:
> "Also measured: `fp_labels` returns 114 objects and `report("ControlTerminal")` returns 114 — **every front-panel object has exactly one diagram terminal in this VI**."

The question was ruled open because a **tab-page-nested** control terminal might be wire 3457's other carrier (`docs/main-vi-stop-and-save.md:68-71`). A whole-VI `ControlTerminal` traverse returning exactly the top-level 114 is direct evidence against a 115th control terminal existing. Not conclusive alone (it rests on Traverse being whole-hierarchy), but it is the cheapest thing bearing on the step being skipped, and neither the plan nor `main-vi-stop-and-save.md:72-74` mentions it.

---

## PART B — THE ARTIFACT

### B1 ALREADY BUILT — **no. Genuinely novel.** No slug.

Verified independently: `docs/toolkit-capabilities.md:27` — `loop_cast`/`OpWhileCast_v0` returns loop UID, the For-loop N wire and `Loop.Shift Registers[]`, nothing else; its label map is `{"Array": "ShiftRegUIDs", "UID": "LoopUID", "error out 2": "ShiftRegsErr", "reference": "seed"}` (`tools/bench/build_opwhilecast_v0.log:101`). The only `6362C00`/`LpEndRef` hits in the project are docs, peer logs, and an NI **example** VI's node seen during seeding (`tools/bench/probe_example_forloop.log:16`, `build_opwhilecast_v0.log:34`) — whose property nodes were deleted at `build_opwhilecast_v0.log:47-49`. And the loop node's own `Terminals[]` cannot reach it (`archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:4`; `docs/toolkit-capabilities.md:35`).

### B2 ALREADY FAILED — not this build. **No slug**, but read before running

`OpCaseFrames_v0` failed five times: `tools/bench/build_opcaseframes_v0.log:24, 49, 78, 108, 127`. Run 5 matters because it failed **additively** — `:120-126` show the property attaching with its census passing (`CENSUS VI Server:MultiFrameStructure 6363801 -> data terminal 'Frames[]'`), then `:127` `FAIL A runnable with the seed wired [… ('Frames[] node + seed (wired)', 0)]`. Same *shape* as gate L4. It is **not** the same construction (that recipe was mid-surgery on a retargeted donor; this one is additive), and the donor lineage already did TMSC-out → class property node three times cleanly (`build_opwhilecast_v0.log:64-78`, both `ExecState=1`). No slug: L4 is the right gate and stopping there without saving is the right response.

### B3-i CONTRADICTED — L3's gate rests on a rule our files already refuted

Plan `:45-46`: "the creator reports no error (**build_property raises on 1077**, so a class/ID LabVIEW rejects stops the build instead of producing a silent no-op node)."

`docs/toolkit-capabilities.md:234-238`:
> "⚠️ But **'no 1077' is NOT a verdict that a property attached** … the 1077 above came from a **deliberately bogus** id, while `Control.Value` **633200D** — a *valid* id on the wrong class — created a node with **no `Value` terminal and no error at all** … The robust check is the **data-terminal-name census** (`build_opcaseframes_v0.py:49-58`) … **Any 'does property X exist on class Y?' test must use that.**"

This build *is* that test: `docs/NAMES.md:241-247` marks the whole Loop/ForLoop/WhileLoop ID block "**not yet verified on this machine**", only `ForLoop.Loop Count` and `Loop.Shift Registers[]` verified since (`:249-252`). The recipe half-covers it by accident — `data_term()` (`:143-151`) indexes `Terminals[4]` and would raise `StopIteration` on an unconfigured 4-terminal node. Assert the census, not the 1077.

### B3-ii HELPER EXISTS — the census and the indicator check are already written

- `tools/recipes/build_opcaseframes_v0.py:48-59` `prop_node()` — builds, asserts exactly one new Property, walks it, asserts **exactly one data SOURCE terminal**, prints `CENSUS … -> data terminal '<name>'`, returns `(uid, name)`. That is `pn()` + `data_term()` (`build_oploopendref_v0.py:217-220`, `:143-151`) done correctly, and it is the function `docs/toolkit-capabilities.md:237` names as required.
- `tools/recipes/build_opcaseframes_v0.py:62-71` `add_indicator()` — asserts one new panel object, that it **is** an indicator, and that its label is **unique**. `make_indicator()` (`build_oploopendref_v0.py:153-160`) checks only "one new label", so a duplicate label would silently mis-key the label map L7/L8 then drive `SetControlValue` from.
- Both ship with `must`/`walk`/`term` from `build_track_v6_core` (`build_opcaseframes_v0.py:33,37`).

### B4 ALREADY MEASURED — one item, prose only, **no slug**

`tools/bench/test_oploopcast.log:84` already records `WhileLoop[1] uid 637`. L7's three-index scan is cheap and a stronger gate, so re-measuring is fine — but state it as confirming `test_oploopcast.log:84`, not as a discovery. The substantive already-measured item is A3-ii.

---

## Verdicts

```
PRIOR-ART: contradicted      A3-i   "mandated step" vs docs/main-vi-stop-and-save.md:72-74, STATUS.md:78-79
PRIOR-ART: contradicted      A3-ii  L8 zero-branch vs tools/bench/drive_original_copy_v3.log:80-81
PRIOR-ART: already-measured  A3-ii  the frame loop's Boolean stop is already measured functionally
PRIOR-ART: contradicted      A3-iii docs/frame-ownership-design.md:92-97 is not the Abort text (that is :105)
PRIOR-ART: unread-evidence   A4     docs/toolkit-capabilities.md:510-511 (114 == 114 control terminals)
PRIOR-ART: contradicted      B3-i   L3's 1077 gate vs docs/toolkit-capabilities.md:234-238
PRIOR-ART: helper-exists     B3-ii  tools/recipes/build_opcaseframes_v0.py:48-59 and :62-71
```

No `novel` line. Nothing here asks for the build to be abandoned — B1 is real new work; the seven findings are the docstring's two miscitations, the L8 verdict text, the L3 gate, and two helpers that already exist in `build_opcaseframes_v0.py`.

## Sources

(extract from answer)

## What was done with it

ALL SEVEN VERDICTS ACCEPTED AND ACTED ON before the build ran. B1 ("genuinely novel") is the release for the
artifact itself; the seven findings are about claims and gates, and every one is a `FIXED:` below — none is
refuted, and none asked for the build to be abandoned.

FIXED: contradicted - tools/recipes/build_oploopendref_v0.py:6-19 - the docstring no longer claims
main-vi-stop-and-save.md:74 and STATUS:78-79 "mandate this reader"; it states the real ordering (recursive
ControlTerminal census FIRST, Loop End Ref only if that finds no second carrier) and names violation-decisions.md
:281-290 of 2026-09-17 03:38 as the later dated decision that supersedes it. (A3-i)

FIXED: contradicted - tools/recipes/build_oploopendref_v0.py:77-88 and :372-381 - the `Connected Wire == 0` branch
now reads INCONCLUSIVE / READER SUSPECT and cites drive_original_copy_v3.log:80-81 plus the `tra001-000` written by
#6384 after the loop, instead of concluding "#637 does not stop from a Boolean". (A3-ii, and the same finding's
already-measured half)

FIXED: contradicted - docs/main-vi-stop-and-save.md:75 - the Abort citation is corrected from
frame-ownership-design.md:92-97 (the superseded camera-overload paragraph) to :105, in the document that carried
the error, with the review named. The recipe carries the same correction. (A3-iii)

FIXED: unread-evidence - tools/recipes/build_oploopendref_v0.py:17-19 - docs/toolkit-capabilities.md:510-511
(fp_labels 114 == report("ControlTerminal") 114, i.e. no 115th, tab-page-nested control terminal) is now recorded
as the cheapest evidence bearing on the step being skipped. (A4)

FIXED: contradicted - tools/recipes/build_oploopendref_v0.py:57-64 and :230-236 - gate L3 is no longer "no error
1077". It is the DATA-TERMINAL-NAME CENSUS that docs/toolkit-capabilities.md:234-238 requires of any "does property
X exist on class Y?" test, which is what this build is (NAMES.md:241-247 marks the WhileLoop id block unverified
on this machine). (B3-i)

FIXED: helper-exists - tools/recipes/build_oploopendref_v0.py:100-110 - build_opcaseframes_v0's `prop_node()` and
`add_indicator()` are IMPORTED and called (the module parameterises them by a module-global `OP`, so the whole
adaptation is rebinding it); the hand-rolled `pn()`, `data_term()` and `make_indicator()` are deleted. This also
buys the unique-label assertion the label map depends on. (B3-ii)

FIXED: already-measured - tools/recipes/build_oploopendref_v0.py:70-72 - L7 is stated as CONFIRMING
tools/bench/test_oploopcast.log:84 ("WhileLoop[1] uid 637"), not as discovering it. (B4)

B2 (already-failed, no slug emitted) is carried into the docstring as a warning: `OpCaseFrames_v0` run 5 failed in
the same SHAPE as gate L4 (property attached, census passed, ExecState still 0 with the seed wired). L4 is where
that would show and the coded response is to stop without saving.

RESULT OF THE BUILD ITSELF: see `tools/bench/build_oploopendref_v0.log` and `tools/bench/loopendref_637.json`.
