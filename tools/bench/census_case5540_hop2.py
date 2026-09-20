"""census_case5540_hop2.py - READ-ONLY second hop of the reseed selector chain (main VI by reference only):
(1) the inner Case #10445 (feeds Or.x): its terminals; (2) every LoopTunnel of the VI whose INNER wire is one of the
unresolved feeders (Or.y 10312, Less?.y 10850, And.y 9806, Equal?.y 10142, Q&R x 3268 / y 10103, #5540 t1 5979 /
t4 5746) -> which control/outside source they carry; (3) the sinks of And.out 9921, Equal?.out 10249, Q&R remainder
10187 on diagram 43; (4) constants on the VI near those nodes (report 'Constant' positions) as candidates for the
unresolved feeders.  py tools/bgrun.py --max-min 10 --log tools/bench/census_case5540_hop2.log -- py -u tools/bench/census_case5540_hop2.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
DIA = 43
UNRESOLVED = {10312: "Or.y", 10850: "Less?.y", 9806: "And.y", 10142: "Equal?.y", 3268: "Q&R.x", 10103: "Q&R.y",
              5979: "#5540 t1", 5746: "#5540 t4"}
OUTS = {9921: "And.out", 10249: "Equal?.out", 10187: "Q&R.rem", 10573: "Case10445.out"}
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    labels = {r["uid"]: r["label"] for r in g.node_labels(MAIN, DIA)}
    rows_by = {}
    for n in range(400):
        u, rows = g.node_terms_uid(MAIN, DIA, n)
        if not u:
            break
        rows_by[u] = (n, rows)
    if 10445 in rows_by:
        print("#10445 'Case Structure' terminals:", flush=True)
        for r in rows_by[10445][1]:
            print(f"   {r['i']:>3} | {r['name']!r:<30} | {'S' if r['is_source'] else 's'} | wire {r['wire']}", flush=True)
    print("\nSinks of the intermediate outputs on diagram 43:", flush=True)
    for u, (n, rows) in rows_by.items():
        for r in rows:
            if not r["is_source"] and r["wire"] in OUTS:
                print(f"   {OUTS[r['wire']]} (wire {r['wire']}) -> #{u} {labels.get(u)!r}.{r['name']!r}", flush=True)
    print("\nUnresolved feeders: loop tunnels whose INNER wire matches (scan of every LoopTunnel):", flush=True)
    tun = g.report_all(MAIN, "LoopTunnel")
    print(f"   {len(tun)} tunnels on the VI", flush=True)
    found = set()
    for o in tun:
        t = g.tunnels(MAIN, o["i"])
        hits = [w for w in t["in_wires"] if w in UNRESOLVED]
        if hits:
            found.update(hits)
            print(f"   tunnel {t['uid']} mode {t['index_mode']}: inner {hits} = {[UNRESOLVED[w] for w in hits]}; outer {t['out_name']!r} wire {t['out_wire']}", flush=True)
    print(f"\n   still unresolved (constants / registers / other): {[(w, UNRESOLVED[w]) for w in UNRESOLVED if w not in found]}", flush=True)
    cons = g.report_all(MAIN, "Constant")
    print(f"\nConstants on the VI: {len(cons)}; positions near the selector nodes (x 3000-6000, y 1000-2500):", flush=True)
    for o in cons:
        if 3000 <= o["pos"][0] <= 6000 and 1000 <= o["pos"][1] <= 2500:
            print(f"   constant uid {o['uid']} at {o['pos']} owner {o.get('owner')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
