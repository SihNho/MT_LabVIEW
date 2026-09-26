"""card 104-2 E3 diagnostic (OFFLINE, no LabVIEW, no edit): the recipe's cdiff (stage_d1_disp.py:42-53, copied verbatim, not
imported - importing the recipe runs its stage) applied to (a) the Part-B DRY end (--from-step 33, Part-A binding), (b) the full
DRY end (no split), (c) the simulated step-57 state itself. Live run stage_d1_disp_c104B2.log:312 had extra [] and 15 of the
21 open rows missing. Prediction: unknown - this measures whether the 15 missing rows reproduce offline (then they are not
LabVIEW-side) or only live."""
import copy
import json
import os
import sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T)
os.chdir(os.path.dirname(T))
import vigraph as V  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402
import jev_candidates as JC  # noqa: E402
import protocol  # noqa: E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))  # noqa: E731
BENCH = os.path.join(T, "bench")
PLAN = os.path.join(BENCH, "sim/disp/plan_disp.json")
P = J(PLAN)
A = P["actions"]
WIKI = J(JC.WIKI, P["context"]["s1_key"] + ".json")
PA = J(BENCH, "stage_d1_dispA.json")["partA"]
LIVE = [(1566, 'error in (no error)'), (10067, 'Initial Time at Start'), (12236, 'x'), (12236, 'y'), (16184, 'error in'),
        (17164, 'error in'), (18136, 'error in'), (19532, 'Cycle Start Time'), (21699, 'x'), (27165, 'error in (no error)'),
        (27466, 'error in (no error)'), (28094, 'error in (no error)'), (31870, 'error in'), (33114, 'error in (no error)'),
        (35648, 'error in (no error)')]     # stage_d1_disp_c104B2.log:312 'missing' (data, copied from the log line)


def cdiff(x, objs, real):
    loops = copy.deepcopy(x.step(len(A))["state"]["loops"])
    ob = x.bind["obj"]
    for L in loops or []:
        L["right_uids"] = [ob.get(int(u), int(u)) for u in L.get("right_uids") or []]
        L["left_of"] = dict((str(ob.get(int(k), int(k))), [ob.get(int(y), int(y)) for y in (v if isinstance(v, list) else [v])])
                            for k, v in (L.get("left_of") or {}).items())
    Greal = JC.from_parts({"terminals": real, "graph_summary": WIKI["graph_summary"]}, objs, loops, JC.node_labels_default(),
                          WIKI["fs_tunnel_pairs"], "diag_c104_e3")
    cd = V.computation_diff(SS.load_s1(P), Greal)
    return (sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"])),
            sorted(set((int(r["node"]), r["term"]) for r in P["open_rows"])), len(cd["rows"]))


out = {}
for lab, kw in (("partB_dry", {"from_step": 33, "binding": os.path.join(BENCH, "stage_d1_dispA.json")}), ("full_dry", {})):
    st, ff, ex = SX.dry_run(PLAN, log=lambda *_a: None, **kw)
    got, want, n = cdiff(ex, ex.be.st["objs"], ex.be.read())
    out[lab] = {"dry": st, "ff": (ff or "")[:200], "rows": n, "got": len(got), "want": len(want),
                "extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))}
    print(lab, json.dumps(out[lab], default=str)[:1500], flush=True)
want = sorted(set((int(r["node"]), r["term"]) for r in P["open_rows"]))
print("open_rows raw", len(P["open_rows"]), "unique (node,term)", len(want))
print("LIVE missing (15) subset of want:", set(map(tuple, LIVE)) <= set(want), " live got = want - missing:",
      sorted(set(want) - set(map(tuple, LIVE))))
for lab in out:
    print(lab, "missing == LIVE missing:", sorted(map(tuple, out[lab]["missing"])) == sorted(LIVE))
json.dump(out, open(os.path.join(BENCH, "diag_c104_e3.json"), "w", encoding="utf-8"), indent=1, default=str)
print(protocol.result_line(protocol.make_result(1, 0, None)))
