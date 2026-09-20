"""test_opnodelabels.py - FUNCTIONAL acceptance of OpNodeLabels_v0 (gscript.node_labels); the decisive test is T2.

Prediction contract (peer review archive/peer/2026-09-14-opnodelabels-v0-plan.md):
  T1 scratch copy of OpFPLabels_v0, diagram 0: len(rows) == len(report_all(scratch,'Node')) and the UID set matches;
     labels are strings (mostly '' - op VIs carry few node labels); no error.
  T2 DECISIVE: main VI diagram 1 (3 implicit Value property nodes, uids 10399 / 10793 / 12476 from the terminal
     sweep), panel closed: their labels are NON-EMPTY and are panel object labels (tools/bench/main_vi_panel_wiring.json).
     Blank -> the Node.Label route is dead for never-displayed headers (recorded; fallback = Control.Create Property
     Node typed seed, peer). Rows for the other nodes of diagram 1 are printed for the record.
  T3 (only if T2 passed) sweep every diagram of the main VI; join by uid with the Value census
     (docs/main-vi-panel-map.md table = tools/bench/main_vi_nodeterms.json Property nodes with an unwired 'reference'
     and a 'Value' row); PREDICTION: >= 80 of 88 implicit nodes get a label that is a panel label; explicit (wired
     reference) Value nodes give ''. Output tools/bench/main_vi_node_labels.json.
  T4 handle audit: 20 runs on the main VI, HandleCount flat within +-100 (post-idle).
Scratch deleted; nothing saved; the main VI is opened by reference only (read-only), never edited.
  py tools/bgrun.py --max-min 25 --log tools/bench/test_opnodelabels.log -- py -u tools/bench/test_opnodelabels.py
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_test_opnodelabels_{os.getpid()}.vi")
for _old in [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_test_opnodelabels")]:
    try:
        os.remove(os.path.join(g.CLAUDEDEV, _old))
    except OSError:
        pass
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def main():
    g._lv = None
    panel = json.load(open(os.path.join(HERE, "main_vi_panel_wiring.json"), encoding="utf-8"))["rows"]
    panel_labels = {r["label"] for r in panel if r.get("label")}
    nt = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
    implicit, explicit = {}, {}
    for di, dg in nt["diagrams"].items():
        for nd in dg["nodes"]:
            names = [t["name"] for t in nd["terms"]]
            if "Value" in names and "reference" in names:
                ref = next(t for t in nd["terms"] if t["name"] == "reference")
                (implicit if ref["wire"] == 0 else explicit).setdefault(int(di), []).append(nd["uid"])
    n_impl = sum(len(v) for v in implicit.values()); n_expl = sum(len(v) for v in explicit.values())
    print(f"census: {n_impl} implicit / {n_expl} explicit Value property nodes over {len(implicit)} diagrams; {len(panel_labels)} panel labels", flush=True)

    # T1
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        rows = g.node_labels(S, 0)
        nodes = g.report_all(S, "Node")
        print(f"T1 scratch: {len(rows)} rows vs {len(nodes)} nodes; labels {[r['label'] for r in rows]}", flush=True)
        check("T1 count", len(rows) == len(nodes), f"{len(rows)} vs {len(nodes)}")
        check("T1 uid set", {r['uid'] for r in rows} == {o['uid'] for o in nodes})
    except Exception as e:
        check("T1", False, f"EXC {str(e)[:200]}")
    finally:
        try:
            os.remove(S)
        except OSError:
            pass

    # T2 decisive
    t0 = time.time(); rows1 = g.node_labels(MAIN, 1); dt = time.time() - t0
    print(f"T2 main diagram 1 ({dt:.1f} s): {len(rows1)} rows", flush=True)
    for r in rows1:
        tag = "IMPLICIT" if r["uid"] in implicit.get(1, []) else ("explicit" if r["uid"] in explicit.get(1, []) else "")
        print(f"   uid {r['uid']:6d} label {r['label']!r} {tag}", flush=True)
    got = {r["uid"]: r["label"] for r in rows1}
    impl1 = implicit.get(1, [])
    hits = [u for u in impl1 if got.get(u) and got[u] in panel_labels]
    nonempty = [u for u in impl1 if got.get(u)]
    check("T2 implicit labels non-empty", len(nonempty) == len(impl1), f"{len(nonempty)}/{len(impl1)}")
    check("T2 implicit labels are panel labels", len(hits) == len(impl1), f"{len(hits)}/{len(impl1)}")
    t2 = len(hits) == len(impl1) and impl1

    if t2:
        out = {"vi": MAIN, "diagrams": {}, "implicit": {}, "explicit": {}}
        n_hit = n_blank = 0; n_expl_blank = 0
        for di in sorted(int(k) for k in TREE["diagrams"].keys()):
            try:
                rows = g.node_labels(MAIN, di)
            except Exception as e:
                print(f"   diagram {di}: EXC {str(e)[:120]}", flush=True); continue
            out["diagrams"][str(di)] = rows
            got = {r["uid"]: r["label"] for r in rows}
            for u in implicit.get(di, []):
                lab = got.get(u, "")
                out["implicit"][str(u)] = {"diagram": di, "label": lab, "is_panel_label": lab in panel_labels}
                if lab in panel_labels and lab:
                    n_hit += 1
                elif not lab:
                    n_blank += 1
            for u in explicit.get(di, []):
                out["explicit"][str(u)] = {"diagram": di, "label": got.get(u, "")}
                if not got.get(u, ""):
                    n_expl_blank += 1
            if di % 20 == 0:
                print(f"   sweep: diagram {di} done ({n_hit} hits so far)", flush=True)
        json.dump(out, open(os.path.join(HERE, "main_vi_node_labels.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        check("T3 >= 80 of 88 implicit nodes labelled with a panel label", n_hit >= 80, f"{n_hit}/{n_impl} hits, {n_blank} blank")
        check("T3 explicit Value nodes give ''", n_expl_blank == n_expl, f"{n_expl_blank}/{n_expl}")
    else:
        print("T3 skipped: T2 did not pass (Node.Label route not decisive here) - recorded, fallback per peer.", flush=True)

    # T4
    for _ in range(3):
        g.node_labels(MAIN, 1)
    h0 = handles()
    for k in range(20):
        g.node_labels(MAIN, 1)
    h1 = handles(); time.sleep(20); h2 = handles()
    check("T4 handles flat (+-100 post-idle)", abs(h2 - h0) <= 100, f"{h0} -> {h1} -> idle {h2}")

    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
