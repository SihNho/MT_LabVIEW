r"""diag_connectnested_donors.py - READ-ONLY census of the four candidate donors for `OpConnectNested_v0`
(`docs/d1-build-plan.md` §11m: `Terminal.Connect Wire` 6349C03 with BOTH ends addressed by INDEX on NESTED
diagrams).

    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_connectnested_donors.log \
        -- py -u tools/bench/diag_connectnested_donors.py

WHY A MEASUREMENT AND NOT A GUESS (CLAUDE.md "when a diagnosis is GUESSED twice, build the reader"): the recipe
headers disagree about where a NESTED diagram reference comes from, and the answer decides the whole build.

  * `build_opwiresr_v0.py:4-13` - the body-node ladder starts at a **WhileLoop-typed** reference
    (`TMSC.specific class reference` -> `Loop[Diagram] 6361401` -> `AbstractDiagram[Nodes[]]`), so BOTH ends of a
    wire built that way would sit on the SAME loop. §11m's test (c) needs two DIFFERENT diagrams.
  * `build_opnodeterms_v0.py:4-6` - its donor `OpNetInfo_v1.vi` reaches `Nodes[]` from a **Diagram** obtained with
    `Class Name = "Diagram"`, `index = <diagram index>` (that is how `gscript.node_terms` is called,
    `tools/gscript.py:693-694`), and continues `IA_n[index 2] -> Node[Terminals[]] -> IA_t[index 3]` - i.e. it
    ALREADY ENDS on a Terminal reference addressed by (diagram index, node index, terminal index), which is
    exactly one half of `OpConnectNested_v0`.

WHAT IS BEING MEASURED, per donor: every node on diagram 0 with its label and every terminal (index, name,
is_source, connected wire), plus the object counts and the front-panel labels. From that the build knows:
  Q1  does the Diagram reference in `OpNetInfo_v1` come from a Traverse array + a cast, and where is the cast?
  Q2  is the Traverse array branchable, so a SECOND IndexArray can select a SECOND diagram from the same call
      (the only route to two independent nested diagrams inside one op run)?
  Q3  which nodes must be deleted from the copy to leave `IA_t.element` (the Terminal reference) standing?
  Q4  `OpConnect_v0`'s two TOP-LEVEL ladders - how each starts (`VI[Block Diagram]`), so the swap to a Diagram
      reference is a re-wire rather than a rebuild.

READ-ONLY: no copy is made, no VI is edited, nothing is saved. Panels are opened (a scripting READ needs the
target loaded) and closed again; md5 of every donor is asserted before and after.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g                       # noqa: E402
from bench_prep import labview_handles     # noqa: E402

DONORS = ["OpNetInfo_v1.vi", "OpNodeTerms_v0.vi", "OpConnect_v0.vi", "OpStopFromNode_v0.vi",
          "OpCreateConstOnTerm_v0.vi", "OpWhileCast_v0.vi"]
OUT = os.path.join(HERE, "connectnested_donors.json")
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


def census(name):
    p = os.path.join(g.CLAUDEDEV, name)
    if not os.path.exists(p):
        gate(f"D0 {name} on disk", False, p)
        return None
    m0 = md5(p)
    g.open_panel(p)
    time.sleep(0.6)
    rec = {"file": name, "md5": m0, "exec_state": g.exec_state(p), "size": os.path.getsize(p)}
    rec["counts"] = {c: g.count(p, c) for c in
                     ("Node", "Property", "Invoke", "IndexArray", "Wire", "ControlTerminal", "SubVI",
                      "Diagram", "WhileLoop", "ForLoop", "Constant")}
    print(f"\n----- {name}: ExecState {rec['exec_state']}, {rec['counts']}", flush=True)
    nodes = []
    try:
        w = walk(p, 0)
    except Exception as e:
        fact(f"{name}: walk failed {str(e)[:120]}")
        w = {}
    for uid, (n, lab, rows) in w.items():
        terms = [(r["i"], r["name"], "OUT" if r["is_source"] else "IN", r["wire"]) for r in rows]
        nodes.append({"uid": uid, "n": n, "label": lab, "terms": terms})
        print(f"   Nodes[{n:2d}] #{uid:<6} {str(lab)[:42]:<42} {terms}", flush=True)
    rec["nodes"] = nodes
    try:
        rec["panel"] = [(i, lab, ind) for i, lab, ind in g.fp_labels(p)]
        print(f"   PANEL: {rec['panel']}", flush=True)
    except Exception as e:
        rec["panel"] = []
        fact(f"{name}: fp_labels failed {str(e)[:100]}")
    try:
        g.close_panel(p)
    except Exception:
        pass
    gate(f"D {name} md5 unchanged by the read", md5(p) == m0, m0)
    return rec


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    t0 = time.time()
    fact(f"LabVIEW handles before: {labview_handles()} (fresh-instance baseline ~31,500)")
    out = {}
    try:
        for nm in DONORS:
            try:
                r = census(nm)
                if r:
                    out[nm] = r
            except Exception as e:
                gate(f"D {nm} censused", False, f"EXC {str(e)[:200]}")
    finally:
        g._lv = None
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    fact(f"census -> {OUT}")
    fact(f"LabVIEW handles after: {labview_handles()}")
    print("\n--- FACTS ---", flush=True)
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== diag_connectnested_donors: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
