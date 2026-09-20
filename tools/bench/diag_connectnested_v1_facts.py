r"""diag_connectnested_v1_facts.py - READ-ONLY. Every name/index `build_opconnectnested_v1.py` needs, measured
before the recipe is written (CLAUDE.md: no mid-run name discovery).

    MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/diag_connectnested_v1_facts.log \
        -- py -u tools/bench/diag_connectnested_v1_facts.py

WHAT ALREADY EXISTS (checked before writing this, per the standing rule):
  * `tools/recipes/build_opconnectnested_v0.py` - built the v0 op; its `walk()`/`term()`/`connect()` helpers are
    reused verbatim below rather than re-written.
  * `tools/recipes/build_opconstvalue_v1.py:165-199` - the PROVEN route for getting a second `To More Specific
    Class` into an op VI: `copy_by_index(<NI example>, "Function", i_tmsc, OP, expect_uid=..., finish=...)` plus a
    TYPED refnum seed control on `target class`. This diagnostic measures the same two donors.
  * `gscript.walk`-equivalents: `node_labels`, `node_terms_uid`, `fp_labels`, `panel_wiring`, `report_all`.

PREDICTION CONTRACT (each line is asserted; the run prints FACTs either way and changes nothing)
 D1 `OpConnectNested_v0.vi` opens at ExecState 1 and holds exactly ONE `To More Specific Class`.
 D2 that TMSC's `target class` input carries a non-zero wire, and the run NAMES its source (panel control, or a
    node + terminal). This decides whether v1 branches that wire or creates its own seed.
 D3 the Traverse node's `References` output wire is named, and the ONE Index Array on it is identified.
 D4 the SOURCE `Nodes[]` property node is identified by wire topology (its `reference` currently branches off the
    TMSC) - that is the single wire v1 re-points.
 D5 the NI example `Navigating Nodes and Wires.vi` diagram 3 still holds a `To More Specific Class`; its
    `Function` Traverse index is printed (the copy_by_index address).
 D6 `Create To More Specific Class.vi` exists in the erdosmiller library; its connector-pane / panel labels are
    printed (the alternative donor route). Read-only: md5 before and after.
 D7 the ORIGINAL working copy's md5 is `2a78e17c449cacdaf5da389818526859` before and after (nothing opens it).
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g                        # noqa: E402
from bench_prep import labview_handles      # noqa: E402

OPV0 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v0.vi")
OPC2 = os.path.join(g.CLAUDEDEV, "OpConnect2_v0.vi")
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects", "Navigating Nodes and Wires.vi")
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATE_TMSC = os.path.join(LIB, "Create To More Specific Class.vi")
ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
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


def walk(target, diagram=0, limit=120):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(limit):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def term(rows, name, source=None):
    for r in rows:
        if r["name"] == name and (source is None or r["is_source"] == source):
            return r
    return None


def dump(target, w, tag):
    print(f"\n--- {tag}: {len(w)} nodes on diagram 0", flush=True)
    for uid, (n, lab, rows) in w.items():
        print(f"   Nodes[{n:2d}] #{uid:<6} {str(lab)[:40]:<40} "
              f"{[(r['i'], r['name'], 'OUT' if r['is_source'] else 'IN', r['wire']) for r in rows]}", flush=True)


def src_of(w, wire):
    for u, (n, lab, rows) in w.items():
        for r in rows:
            if r["is_source"] and r["wire"] == wire and wire:
                return u, lab, r["name"], n
    return None, None, None, None


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    t0 = time.time()
    fact(f"handles before {labview_handles()}")
    gate("D7a original md5 before", md5(ORIG) == ORIG_MD5, md5(ORIG))

    # ---------------------------------------------------------------- D1..D4  OpConnectNested_v0
    try:
        g.open_panel(OPV0)
        time.sleep(0.6)
        es = g.exec_state(OPV0)
        w = walk(OPV0, 0)
        dump(OPV0, w, "OpConnectNested_v0.vi")
        tmscs = [u for u, (n, lab, rows) in w.items() if term(rows, "specific class reference", True)]
        gate("D1 OpConnectNested_v0 ExecState 1 and exactly ONE To More Specific Class",
             es == 1 and len(tmscs) == 1, f"ExecState {es}, TMSC {tmscs}")
        fact(f"panel labels: {[(i, l, ind) for i, l, ind in g.fp_labels(OPV0)]}")
        fact(f"panel_wiring: {[(r['label'], r['uid'], r['wire']) for r in g.panel_wiring(OPV0)]}")
        if tmscs:
            tm = tmscs[0]
            tc = term(w[tm][2], "target class", False)
            fact(f"TMSC #{tm} Nodes[{w[tm][0]}] terminals "
                 f"{[(r['i'], r['name'], r['is_source'], r['wire']) for r in w[tm][2]]}")
            if tc and tc["wire"]:
                u, lab, nm, n = src_of(w, tc["wire"])
                pw = {r["wire"]: r["label"] for r in g.panel_wiring(OPV0)}
                fact(f"D2 TMSC 'target class' <- w{tc['wire']} from node #{u} {lab!r} terminal {nm!r} "
                     f"(Nodes[{n}]); panel object on that wire: {pw.get(tc['wire'])!r}")
                gate("D2 TMSC 'target class' is wired and its source is NAMED", True)
            else:
                gate("D2 TMSC 'target class' is wired", False, f"{tc}")
            # D3 Traverse + its Index Array
            trav = next((u for u, (n, lab, rows) in w.items() if term(rows, "References", True)), None)
            if trav:
                wr = term(w[trav][2], "References", True)["wire"]
                ias = [(u, w[u][0]) for u, (n, lab, rows) in w.items()
                       if lab == "Index Array" and (term(rows, "array", False) or {}).get("wire") == wr]
                fact(f"D3 Traverse #{trav} Nodes[{w[trav][0]}] References=w{wr}; "
                     f"Index Arrays on that array: {ias}")
                gate("D3 exactly one Index Array on the Traverse References array", len(ias) == 1, f"{ias}")
            # D4 the source Nodes[] PN = a Property Node whose `reference` carries the TMSC's output wire
            sc = term(w[tm][2], "specific class reference", True)
            pns = [(u, w[u][0]) for u, (n, lab, rows) in w.items()
                   if lab == "Property Node" and (term(rows, "reference", False) or {}).get("wire") == sc["wire"]]
            fact(f"D4 TMSC 'specific class reference' = w{sc['wire']}; property nodes on it: {pns}")
            gate("D4 the TMSC output feeds TWO property nodes (sink + source Nodes[])", len(pns) == 2, f"{pns}")
            for u, n in pns:
                data = [r["name"] for r in w[u][2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
                fact(f"D4  PN #{u} Nodes[{n}] data outputs {data}")
    except Exception as e:
        gate("D1-D4 OpConnectNested_v0 inspected", False, f"EXC {str(e)[:200]}")
    finally:
        try:
            g.close_panel(OPV0)
        except Exception:
            pass

    # ---------------------------------------------------------------- D5  the NI example donor
    try:
        ex_md5 = md5(EX)
        labs = {r["uid"]: r["label"] for r in g.node_labels(EX, 3)}
        tm_ex = [u for u, l in labs.items() if l == "To More Specific Class"]
        order = [o["uid"] for o in g.report_all(EX, "Function")]
        fact(f"D5 example diagram-3 TMSC uids {tm_ex}; Function Traverse indices "
             f"{[(u, order.index(u)) for u in tm_ex if u in order]}")
        gate("D5 the NI example still holds a To More Specific Class on diagram 3", bool(tm_ex), f"{tm_ex}")
        gate("D5b NI example md5 unchanged", md5(EX) == ex_md5, ex_md5)
    except Exception as e:
        gate("D5 NI example inspected", False, f"EXC {str(e)[:200]}")

    # ---------------------------------------------------------------- D6  the erdosmiller creator
    try:
        gate("D6a Create To More Specific Class.vi on disk", os.path.exists(CREATE_TMSC), CREATE_TMSC)
        if os.path.exists(CREATE_TMSC):
            c_md5 = md5(CREATE_TMSC)
            fact(f"D6 conpane: {g.conpane(CREATE_TMSC)}")
            fact(f"D6 fp_labels: {[(i, l, ind) for i, l, ind in g.fp_labels(CREATE_TMSC)]}")
            gate("D6b Create To More Specific Class.vi md5 unchanged", md5(CREATE_TMSC) == c_md5, c_md5)
    except Exception as e:
        gate("D6 erdosmiller creator inspected", False, f"EXC {str(e)[:200]}")

    gate("D7b original md5 after", md5(ORIG) == ORIG_MD5, md5(ORIG))
    fact(f"handles after {labview_handles()}")
    g._lv = None
    print("\n--- FACTS ---", flush=True)
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== diag_connectnested_v1_facts: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
