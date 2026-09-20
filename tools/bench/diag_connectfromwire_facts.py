r"""diag_connectfromwire_facts.py - READ-MOSTLY diagnostic for cycle 15 route-B session 1. Two independent
questions, one run, one log, no new op built and nothing saved over anything.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/diag_connectfromwire_facts.log \
        -- py -u tools/bench/diag_connectfromwire_facts.py

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md, "before creating any new op, tool or recipe"):
  * `tools/gscript.py` already has `wire_control` (with the `src_diagram_index` parameter this diagnostic is
    about), `report_all`, `node_terms_uid`, `node_labels`, `fp_labels`, `panel_wiring`, `delete_object`,
    `remove_bad_wires_scripted`, `open_panel`, `close_panel`. Nothing here is hand-rolled.
  * `tools/recipes/build_track_v6_core.py` already has `walk()` and `term()`; `build_opconnectnested_v1.py`
    already has `ladder_from()` - the wire-topology walker that identifies an op's two ladders. Both are
    IMPORTED, not re-implemented.
  * `tools/bench/bench_prep.py` already reads LabVIEW's handle count and restarts above the limit.
  * `grep "^def " tools/gscript.py`: there is NO helper that calls `Get Controls.vi` on its own, and none that
    dumps an op VI's node/terminal topology - hence PART A below, which is 20 lines of the two imports above.

PART A - TOPOLOGY of the two halves the new op `OpConnectFromWire_v0` would be fused from
  (`docs/d1-build-plan.md` 11t names them: front half `OpWireSource_v5.vi`, back half `OpConnectNested_v1.vi`).
  Purely read-only: open the panel, walk diagram 0, print every node with its class, label and terminals, plus
  the panel control/indicator labels. Prediction contract:
    A1  `OpConnectNested_v1.vi` opens at ExecState 1 and has exactly TWO `To More Specific Class` nodes.
    A2  it has exactly ONE `Traverse for GObjects` node (one `References` source), so both its ladders share one
        `Class Name` - i.e. a wire-class source ladder needs a SECOND traverse or a different front half.
    A3  `OpWireSource_v5.vi` opens at ExecState 1, and the count of its `To More Specific Class` nodes and of its
        `Traverse`-like `References` sources is REPORTED (the prior-art finding B3-i claims it carries TWO
        independent Traverse -> IA -> TMSC ladders; this run says yes or no, measured).
    A4  `OpWireSource_v5.vi` contains a node whose data output is `Terms[]` and whose `reference` input is fed
        from a To More Specific Class - the exact sub-chain the new op's SOURCE side needs.

PART B - WHY THE 6 `from-ctl` ROWS RAISE 5001. Read `tools/bench/build_d1_v0_run9.log`:
    line 358   `SKIPPED-PHASE  S3c-ctlterm: the 6 ControlTerminals reparented into 1.2 (plan s5d)`
    lines 315-320  all six failures are `error 5001: LV-Scripting.lvlib:Get Controls.vi`
  and `tools/recipes/build_d1_v0.py:1057`  `g.wire_control(TARGET, [lbl], s_cls, s_i, [sink_name])` - with NO
  `src_diagram_index`, so it defaults to 0 = the TOP-LEVEL block diagram. `gscript.wire_control`'s own docstring
  says "Get Controls only sees control TERMINALS living on the given diagram - a terminal placed inside a
  loop/case needs that subdiagram's index (2026-09-01)". The 8 control terminals live on `Diagram #639`.
  TWO COMPETING CAUSES, and this part separates them on a fresh working copy of the original (never the original):
    H-newline  the label's literal newlines break the name match in `Get Controls.vi`.
    H-diagram  the label is fine; `Get Controls.vi` was looking on the wrong diagram.
  Note what the run-9 log already settles on its own and this run only confirms: the labels were ALREADY passed
  with literal newlines (the repr in lines 317-320 contains real newlines), and three of the six failing labels
  (`Auto-Reset`, `Reset Tracking`, `Correction Factor`) contain NO newline at all - so H-newline cannot be the
  cause of at least those three.
  Prediction contract, per label tested (one WITH newlines, uid 28148; one WITHOUT, uid 17472):
    B1  `src_diagram_index=0` -> RuntimeError containing `5001` and `Get Controls.vi`   (reproduces run 9)
    B2  `src_diagram_index=<traverse index of Diagram #639>` -> NO error, and the sink terminal's wire goes
        from 0 to non-zero.
    B3  the newline label and the no-newline label behave THE SAME under B2 (if they differ, H-newline is live
        for the newline label only, and that is the fact to report).
  Sinks are BARED first (delete the existing wire net, exactly as run 9's relocation leaves them bare); the
  target is a throwaway copy with a unique name, deleted in this same run.

RULE 1 / 1a: the original is copied, never opened, never written; its md5 is read before AND after in an outer
finally. Nothing is saved anywhere. No hardware, no GUI.
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
sys.path.insert(0, HERE)
import gscript as g                                    # noqa: E402
import build_track_v6_core as B                        # noqa: E402
from build_opconnectnested_v1 import ladder_from, walk, term, src_of, cls_of   # noqa: E402
from bench_prep import labview_handles                 # noqa: E402

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
V1 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
STAMP = time.strftime("%H%M%S")
WORK = os.path.join(g.CLAUDEDEV, f"SCRATCH_cfw_{STAMP}.vi")
FRAME_DIAG_UID = 639          # MEASURED: the frame loop's body diagram, owner of the 8 ControlTerminals
g._run.__defaults__ = (6.0, 120.0)

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ PART A
def dump(path, tag):
    """Read-only topology dump of an op VI's top-level diagram."""
    print(f"\n=== A: {tag}  {path}", flush=True)
    if not os.path.exists(path):
        gate(f"A0 {tag} exists", False, path)
        return None
    g.open_panel(path)
    time.sleep(0.6)
    es = g.exec_state(path)
    gate(f"A0 {tag} opens at ExecState 1", es == 1, f"ExecState {es}")
    w = walk(path, 0)
    tmsc, refs, terms_pn = [], [], []
    for u, (n, lab, rows) in sorted(w.items(), key=lambda kv: kv[1][0]):
        cls = cls_of(u, w)
        ins = [(r["i"], r["name"], r["wire"]) for r in rows if not r["is_source"]]
        outs = [(r["i"], r["name"], r["wire"]) for r in rows if r["is_source"]]
        print(f"   N[{n:2}] #{u:<6} {cls:<12} {lab!r:<34} IN {ins}  OUT {outs}", flush=True)
        if term(rows, "specific class reference", True):
            tmsc.append(u)
        if term(rows, "References", True):
            refs.append(u)
        if term(rows, "Terms[]", True):
            terms_pn.append(u)
    ctls = [(i, l, ind) for i, l, ind in g.fp_labels(path)]
    print(f"   PANEL {ctls}", flush=True)
    fact(f"{tag}: {len(w)} nodes; TMSC {tmsc}; References sources {refs}; 'Terms[]' outputs {terms_pn}")
    g.close_panel(path)
    return dict(w=w, tmsc=tmsc, refs=refs, terms_pn=terms_pn, path=path)


def part_a():
    a1 = dump(V1, "OpConnectNested_v1")
    if a1:
        gate("A1 OpConnectNested_v1 has exactly TWO To More Specific Class nodes", len(a1["tmsc"]) == 2,
             f"TMSC {a1['tmsc']}")
        gate("A2 OpConnectNested_v1 has exactly ONE 'References' source (one Traverse, one Class Name)",
             len(a1["refs"]) == 1, f"References sources {a1['refs']}")
        try:
            w = a1["w"]
            inv = next(u for u, (n, lab, rows) in w.items() if lab == "Invoke Node")
            sink = ladder_from(w, term(w[inv][2], "reference", False)["wire"], "SINK  ")
            src = ladder_from(w, term(w[inv][2], "Wire Source", False)["wire"], "SOURCE")
            fact(f"A2b ladders: SINK {sink}; SOURCE {src}; Invoke #{inv}")
        except Exception as e:
            fact(f"A2b ladder walk raised {str(e)[:140]}")
    a5 = dump(V5, "OpWireSource_v5")
    if a5:
        gate("A3 OpWireSource_v5's TMSC and Traverse counts are REPORTED (no pass/fail claim)", True,
             f"TMSC {a5['tmsc']}, References sources {a5['refs']}")
        ok = False
        if a5["terms_pn"]:
            w = a5["w"]
            pn = a5["terms_pn"][0]
            ref_w = (term(w[pn][2], "reference", False) or {}).get("wire")
            feeder = src_of(w, ref_w)
            ok = feeder is not None and feeder in a5["tmsc"]
            fact(f"A4 'Terms[]' node #{pn} reference w{ref_w} <- #{feeder} "
                 f"({'a TMSC' if ok else 'NOT a TMSC'})")
        gate("A4 OpWireSource_v5's 'Terms[]' property node is fed by a To More Specific Class", ok)


# ------------------------------------------------------------------ PART B
CASES = [
    # (label as recorded in d1_rewire_sources.json, sink uid, sink terminal index, sink terminal name)
    ("Auto-Reset", 9647, 1, "y"),
    ("Force\nsmoothing\nhalf-width", 1359, 7, "Force\nsmoothing\nhalf-width"),
]


def class_index(target, classes=("SubVI", "Function", "CaseStructure", "ForLoop", "WhileLoop", "Comparison",
                                 "IndexArray", "Property", "Invoke", "Unbundler", "Bundler")):
    """uid -> (class name, traverse index within that class) - the addressing wire_control's DEST side uses."""
    out = {}
    for cls in classes:
        try:
            for i, o in enumerate(g.report_all(target, cls)):
                out[o["uid"]] = (cls, i)
        except Exception as e:
            print(f"   (class_index: {cls} raised {str(e)[:60]})", flush=True)
    return out


def bare_sink(target, diag_i, uid, t_i):
    """Delete whatever wire currently drives that sink terminal, so the state matches run 9's (a cut terminal)."""
    w = B.walk(target, diag_i)
    n_i = w[uid][0]
    rows = g.node_terms(target, diag_i, n_i)
    wire = next((r["wire"] for r in rows if r["i"] == t_i), 0)
    if wire:
        order = [o["uid"] for o in g.report_all(target, "Wire")]
        if wire in order:
            g.delete_object(target, "Wire", order.index(wire), verify=False)
            g.remove_bad_wires_scripted(target)
    rows = g.node_terms(target, diag_i, n_i)
    now = next((r["wire"] for r in rows if r["i"] == t_i), 0)
    return wire, now, n_i


def try_wire(target, label, s_cls, s_i, sink_name, diag_i):
    try:
        g.wire_control(target, [label], s_cls, s_i, [sink_name], src_diagram_index=diag_i)
        return ""
    except Exception as e:
        return str(e)[:200]


def part_b():
    print("\n=== B: the 6 from-ctl 5001 rows - newline vs diagram index", flush=True)
    shutil.copyfile(ORIGINAL, WORK)
    time.sleep(0.4)
    g.open_panel(WORK)
    time.sleep(1.2)
    es = g.exec_state(WORK)
    fact(f"B0 fresh working copy {os.path.basename(WORK)}: ExecState {es}")
    d639 = [o["uid"] for o in g.report_all(WORK, "Diagram")].index(FRAME_DIAG_UID)
    fact(f"B0 Diagram #{FRAME_DIAG_UID} is Traverse('Diagram') index {d639}")
    pw = {r["uid"]: r for r in g.panel_wiring(WORK)}
    for lbl, uid, t_i, t_name in CASES:
        rows = [r for r in pw.values() if r["label"] == lbl]
        fact(f"B0 panel row for {lbl!r}: {rows}")
    ci = class_index(WORK)
    for lbl, uid, t_i, t_name in CASES:
        nl = "\\n" in repr(lbl)
        s_cls, s_i = ci.get(uid, (None, None))
        if s_cls is None:
            gate(f"B  sink #{uid} found in the class index ({lbl!r})", False)
            continue
        was, now, n_i = bare_sink(WORK, d639, uid, t_i)
        fact(f"B  sink #{uid} t{t_i} {t_name!r} on Diagram[{d639}].N[{n_i}] ({s_cls}[{s_i}]): "
             f"wire {was} -> {now} after baring")
        e0 = try_wire(WORK, lbl, s_cls, s_i, t_name, 0)
        gate(f"B1 src_diagram_index=0 raises 5001 from Get Controls.vi  [{lbl!r}, newline={nl}]",
             "5001" in e0 and "Get Controls" in e0, f"error {e0!r}")
        e1 = try_wire(WORK, lbl, s_cls, s_i, t_name, d639)
        rows = g.node_terms(WORK, d639, n_i)
        after = next((r["wire"] for r in rows if r["i"] == t_i), 0)
        gate(f"B2 src_diagram_index={d639} wires it  [{lbl!r}, newline={nl}]", (not e1) and bool(after),
             f"error {e1!r}; sink wire {now} -> {after}")
    print("\n   (B3 is read off the two B2 rows above: same verdict for the newline and the no-newline label "
          "=> the newline is NOT the cause)", flush=True)


def main():
    print(f"  FACT  LabVIEW handles at start: {labview_handles()}", flush=True)
    part_a()
    try:
        part_b()
    finally:
        try:
            g.close_panel(WORK)
        except Exception as e:
            print(f"   (close_panel: {str(e)[:80]})", flush=True)
        for _ in range(6):
            try:
                if os.path.exists(WORK):
                    os.remove(WORK)
                break
            except OSError:
                time.sleep(1.0)
        gate("Z scratch deleted (never saved)", not os.path.exists(WORK), WORK)
    print(f"  FACT  LabVIEW handles at end: {labview_handles()}", flush=True)
    print(f"\n=== diag_connectfromwire_facts: {len(passes)} pass, {len(fails)} fail"
          f"{(' -> ' + ', '.join(fails)) if fails else ''} ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1800:]}", flush=True)
    finally:
        same = md5(ORIGINAL) == ORIG_MD5
        print(f"  {'PASS' if same else 'FAIL'}  Z(finally) original md5 unchanged  {md5(ORIGINAL)}",
              flush=True)
        if not same:
            rc = 1
    sys.exit(rc)
