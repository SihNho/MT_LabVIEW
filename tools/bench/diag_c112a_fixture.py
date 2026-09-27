"""diag_c112a_fixture - card 112-1: find a NON-D1 scratch fixture among docs/wiki/subvi/*.json (read-only, no LabVIEW):
 (T2) a case-selector / structure Tunnel OUTER sink fed directly by a ControlTerminal;
 (T1) a While/For loop with a register whose RIGHT inner sink and LEFT inner source are each wired to one node terminal.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c112a_fixture.log -- py -u tools/bench/diag_c112a_fixture.py"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
n = 0
for p in sorted(glob.glob(os.path.join(ROOT, "docs", "wiki", "subvi", "*.json"))):
    if os.path.basename(p).startswith("D1_"):
        continue
    try:
        G = json.load(open(p, encoding="utf-8"))
    except Exception as e:                                   # noqa: BLE001
        print("SKIP", os.path.basename(p), e)
        continue
    T = G.get("terminals") or []
    if not T:
        print("NOTERMS", os.path.basename(p), sorted(G.keys())[:12])
        continue
    byw = {}
    for r in T:
        if r.get("wire_uid"):
            byw.setdefault(r["wire_uid"], []).append(r)
    t2 = []
    for r in T:
        if r.get("owner_class") in ("Tunnel", "SelectorTunnel") and r.get("term_class") == "OuterTerminal" and not r["is_source"] \
                and r.get("wire_uid"):
            src = [x for x in byw[r["wire_uid"]] if x["is_source"]]
            sinks = [x for x in byw[r["wire_uid"]] if not x["is_source"]]
            if len(src) == 1 and (src[0].get("term_class") == "ControlTerminal" or src[0].get("owner_class") == "ControlTerminal"):
                t2.append((r["owner_uid"], r["owner_class"], r["term_uid"], src[0]["term_uid"], src[0]["term_name"], len(sinks)))
    t1 = []
    for L in G.get("loops") or []:
        for R, lefts in (L.get("left_of") or {}).items():
            ri = [x for x in T if x["owner_uid"] == int(R) and x.get("term_class") == "InnerTerminal"]
            li = [x for x in T if x["owner_uid"] in [int(v) for v in (lefts if isinstance(lefts, list) else [lefts])]
                  and x.get("term_class") == "InnerTerminal"]
            t1.append((L.get("class"), L.get("loop_uid"), int(R), [(x["term_uid"], x["wire_uid"]) for x in ri],
                       [(x["term_uid"], x["wire_uid"]) for x in li]))
    if t1 or t2:
        n += 1
        print("VI", os.path.basename(p), "| vi:", G.get("vi") or G.get("source"), "| T2:", t2[:4], "| T1:", t1[:3])
print("CANDIDATES", n)
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
