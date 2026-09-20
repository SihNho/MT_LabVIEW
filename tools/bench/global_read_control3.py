"""global_read_control3.py - READ-global positive control from NI's shipped examples (copies in claudeDev).

The lab hierarchy has no READ global (motor subVI: 0 sites; main VI: 7 sites, all WRITE), and drop_subvi cannot
place one (error 1057). NI ships example VIs that read globals (Network Streams 'Global Stop', Occurrence 'Global -
Occurrence Loop Stop'). For each candidate example VI (COPIED to claudeDev, reference only, deleted afterwards):
  1. probe the Traverse class name for global nodes: report_all(copy, cls) for cls in GLOBAL_CLASSES -> uids
  2. walk every diagram (net_map) to map uid -> (diagram, Nodes[] index) and read the terminal tuple
  3. node_terms on each global node -> Is Source?
    prediction: at least one global node reads TRUE (a READ) and at least one FALSE (a WRITE) across the examples;
    the Traverse class name that works is recorded for docs/NAMES.md.
  py tools/bgrun.py --max-min 12 --log tools/bench/global_read_control3.log -- py -u tools/bench/global_read_control3.py
"""
import glob
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EX = r"C:\Program Files\National Instruments\LabVIEW 2026\examples"
CANDIDATES = sorted(glob.glob(os.path.join(EX, "Data Communication", "Network Streams", "Simple Network Streams", "*.vi")))[:4] + \
             sorted(glob.glob(os.path.join(EX, "Synchronization", "Occurrence", "*.vi")))[:4]
GLOBAL_CLASSES = ("GlobalVariable", "Global", "Global Variable", "GlobalVI")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    reads = writes = 0
    class_ok = None
    for src in CANDIDATES:
        S = os.path.join(g.CLAUDEDEV, f"SCRATCH_gread_{os.getpid()}_{os.path.basename(src)}")
        shutil.copyfile(src, S)
        print(f"\n== {os.path.basename(src)}", flush=True)
        uids = None
        for cls in ([class_ok] if class_ok else GLOBAL_CLASSES):
            try:
                rows = g.report_all(S, cls)
                uids = {o["uid"] for o in rows}
                class_ok = cls
                print(f"   Traverse class {cls!r}: {len(rows)} global node(s)", flush=True)
                break
            except Exception as e:
                print(f"   Traverse class {cls!r}: {str(e)[:90]}", flush=True)
        if not uids:
            try:
                os.remove(S)
            except OSError:
                pass
            continue
        dias = g.report_all(S, "Diagram")
        found = 0
        t0 = time.time()
        for d in dias:
            if found >= len(uids):
                break
            nodes, _ = g.net_map(S, d["i"], max_nodes=80, max_terms=24)
            for n, (uid, _l, terms) in nodes.items():
                if uid in uids:
                    found += 1
                    oracle = [(t, w) for _ti, t, w in terms]
                    rws = g.node_terms(S, d["i"], n)
                    data = [r for r in rws if r["name"]]
                    direction = None
                    if len(data) == 1 and not data[0]["src_err"]:
                        direction = "READ" if data[0]["is_source"] else "WRITE"
                    reads += direction == "READ"; writes += direction == "WRITE"
                    print(f"   diagram {d['i']:2d} n {n:2d} uid {uid:6d} terms {oracle} -> {direction} "
                          f"(named {len(data)}, errs {[(r['name_err'], r['src_err'], r['conn_err'], r['wire_err']) for r in data]})", flush=True)
        print(f"   {found}/{len(uids)} global nodes located in {time.time() - t0:.0f} s", flush=True)
        try:
            os.remove(S)
        except OSError as e:
            print("   cleanup:", str(e)[:80], flush=True)
    print(f"\nTraverse class for global nodes: {class_ok!r}", flush=True)
    verdict = "PASS: READ globals read TRUE" if reads else ("FAIL: globals found but none reads TRUE" if writes else "INCONCLUSIVE: no global nodes located")
    print(f"VERDICT (positive control): {verdict}  [READ {reads}, WRITE {writes}]", flush=True)
    return 0 if reads else 3


if __name__ == "__main__":
    sys.exit(main())
