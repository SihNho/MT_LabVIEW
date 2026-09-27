"""diag_c112c_rows - card 112-3 W0 (offline, no LabVIEW): candidate T1/T2 rows on the BED graph (review
archive/peer/2026-09-27-c112c-fixture.md s2: the fixture is a scratch byte copy of the bed, graph_l2b1_20260927.json).
T1 = an EXISTING register (stagexec.base_registers) whose R.inner is fed by ONE source and whose L.inner wire has ONE sink;
T2 = a WIRED ControlTerminal -> case-selector 'Tunnel' outer face (owner CaseStructure). Prints ROW lines; no gate on choice."""
import collections, json, os, sys                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagexec as X, protocol as P                                                   # noqa: E401,E402
G = X._j(os.path.join(HERE, "graph_l2b1_20260927.json"))
T = G["terminals"]
byw = collections.defaultdict(list)
for r in T:
    if r["wire_uid"]:
        byw[int(r["wire_uid"])].append(r)
cls = dict((int(o["uid"]), o["class"]) for o in G["objs"])
pairs = [(int(Lp["loop_uid"]), int(r_), int((ls_ if isinstance(ls_, list) else [ls_])[0])) for Lp in G.get("loops") or []
         for r_, ls_ in (Lp.get("left_of") or {}).items()]
print("LOOPS", [(Lp.get("loop_uid"), Lp.get("class") or cls.get(int(Lp.get("loop_uid") or 0)), len(Lp.get("right_uids") or []),
                 len(Lp.get("left_of") or {})) for Lp in G.get("loops") or []])
n1 = n2 = 0
for lp, u, L in pairs:
    v = {"loop": lp}
    if cls.get(lp) != "WhileLoop":
        continue
    ri = [r for r in T if int(r["owner_uid"]) == u and r["term_class"] == "InnerTerminal"]
    li = [r for r in T if int(r["owner_uid"]) == L and r["term_class"] == "InnerTerminal"]
    if len(ri) != 1 or len(li) != 1 or not ri[0]["wire_uid"] or not li[0]["wire_uid"]:
        continue
    rw, lw = byw[int(ri[0]["wire_uid"])], byw[int(li[0]["wire_uid"])]
    rs = [x for x in rw if x["is_source"] and x is not ri[0]]
    ls = [x for x in lw if not x["is_source"] and x is not li[0]]
    ok = len(rw) == 2 and len(rs) == 1 and len(lw) == 2 and len(ls) == 1
    n1 += ok
    print("ROW-T1 loop #{0} R #{1} t{2} w{3} <- {4} | L #{5} t{6} w{7} -> {8} | usable {9}".format(
        v["loop"], u, ri[0]["term_uid"], ri[0]["wire_uid"], [(x["owner_uid"], x["owner_class"], x["term_uid"], x["term_name"]) for x in rs],
        L, li[0]["term_uid"], li[0]["wire_uid"], [(x["owner_uid"], x["owner_class"], x["term_uid"], x["term_name"]) for x in ls], ok))
for r in T:
    if r["owner_class"] == "Tunnel" and r["term_class"] == "OuterTerminal" and not r["is_source"] and r["wire_uid"]:
        w = byw[int(r["wire_uid"])]
        s = [x for x in w if x["is_source"]]
        if len(s) == 1 and s[0]["term_class"] == "ControlTerminal":
            inner = sorted(set(int(x["frame_diagram"]) for x in T if x["owner_uid"] == r["owner_uid"] and x["term_class"] == "InnerTerminal"))
            own = sorted(set(tuple(G["owners"].get(str(f), ("?", 0))) for f in inner))
            ok = len(w) == 2 and len(own) == 1 and own[0][0] == "CaseStructure"
            n2 += ok
            print("ROW-T2 CT t{0} {1!r} (owner #{2}) -> Tunnel #{3} outer t{4} w{5} frame {6}; inner frames {7} owners {8}; wire ends {9} | usable {10}".format(
                s[0]["term_uid"], s[0]["term_name"], s[0]["owner_uid"], r["owner_uid"], r["term_uid"], r["wire_uid"], r["frame_diagram"], inner, own, len(w), ok))
print(P.result_line(P.make_result(int(n1 > 0) + int(n2 > 0), int(n1 == 0) + int(n2 == 0),
                                  None if n1 and n2 else "no usable T1 ({0}) or T2 ({1}) row".format(n1, n2))))
