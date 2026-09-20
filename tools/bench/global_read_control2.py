"""global_read_control2.py - POSITIVE CONTROL for READ globals, found in an existing VI (drop_subvi cannot place a
global: error 1057, tools/bench/global_read_control.log).

Target: the motor-loop subVI the main VI calls (`Motor control v5_No Recording.vi`, an ORIGINAL - read by
reference only, never opened, never saved). It is where docs/main-vi-state.md expects the globals to be READ.
Walk every diagram of it (small VI), find nodes whose terminal is named 'Trans position' / 'Rot position' /
'Focus position', run node_terms on each, and report Is Source? per site.
    prediction: at least one site reads Is Source? = TRUE (a READ); if EVERY global site in the whole hierarchy were
    FALSE the op could not be trusted for direction and the main-VI "all WRITE" result stays unverified.
Also reports the VI's md5 before/after (must be identical).
  py tools/bgrun.py --max-min 10 --log tools/bench/global_read_control2.log -- py -u tools/bench/global_read_control2.py
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SUBVIS = json.load(open(os.path.join(HERE, "main_vi_subvis.json"), encoding="utf-8"))
MOTOR = next((p for name, p in ((r["name"], r["path"]) for rows in SUBVIS["diagrams"].values() for r in rows)
              if name.startswith("Motor control v5")), None)
FIELDS = ("Trans position", "Rot position", "Focus position")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    if not MOTOR or not os.path.exists(MOTOR):
        print(f"STOP: motor VI path not found: {MOTOR!r}", flush=True)
        return 2
    md5a = hashlib.md5(open(MOTOR, "rb").read()).hexdigest()
    print(f"target {MOTOR}\n   md5 {md5a}", flush=True)
    dias = g.report_all(MOTOR, "Diagram")
    print(f"   {len(dias)} diagrams: {[(d['i'], d['owner']) for d in dias]}", flush=True)
    sites = []
    t0 = time.time()
    for d in dias:
        nodes, _ = g.net_map(MOTOR, d["i"], max_nodes=80, max_terms=24)
        for n, (uid, _l, terms) in nodes.items():
            names = [t for _ti, t, _w in terms if t]
            for f in FIELDS:
                if f in names:
                    sites.append((d["i"], n, uid, f, [(t, w) for _ti, t, w in terms]))
    print(f"   {len(sites)} global sites found in {time.time() - t0:.0f} s", flush=True)
    reads = writes = 0
    for (di, n, uid, f, oracle) in sites:
        rows = g.node_terms(MOTOR, di, n)
        data = [r for r in rows if r["name"]]
        ok = [(r["name"], r["wire"]) for r in rows][:len(oracle)] == oracle
        direction = None
        if len(data) == 1 and not data[0]["src_err"]:
            direction = "READ" if data[0]["is_source"] else "WRITE"
        reads += direction == "READ"; writes += direction == "WRITE"
        print(f"   diagram {di:2d} n {n:2d} uid {uid:6d} {f:15s} -> {direction} (tuple==walker {ok}, named {len(data)}, "
              f"errs {[(r['name_err'], r['src_err'], r['conn_err'], r['wire_err']) for r in data]})", flush=True)
    md5b = hashlib.md5(open(MOTOR, "rb").read()).hexdigest()
    print(f"   md5 unchanged: {md5a == md5b}", flush=True)
    verdict = ("PASS: READ globals exist and read Is Source? TRUE" if reads else
               ("FAIL: every global site reads FALSE - op cannot be trusted for direction" if sites else "INCONCLUSIVE: no global sites found"))
    print(f"VERDICT (positive control): {verdict}  [READ {reads}, WRITE {writes}]", flush=True)
    return 0 if reads else 3


if __name__ == "__main__":
    sys.exit(main())
