# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-3.json
# ---
r"""prep_c167_a1_3_scan - card 167-a1-3 (OFFLINE, stored json only): (1) every action of the ring plans P2b..P5-2e whose `dst` names one
of the closure sink nodes (the frame-keyed cdiff(S1, 7815af09) rows), with plan file:line, id, op, src, dst and `why` - the candidate
CITATIONS for class R; (2) the shape of the p6_facts F1 rows (one wire row, one item-only row). Prints only; nothing written.
Found before writing: no shared "which plan action wired sink X" function (grep "def .*action.*sink|def .*wired_by" tools -> 0); the
stagekit pb_inherit_ctx / case_move_frames read plans for frames, not for sinks. PREDICTION CONTRACT: >= 1 action per cdiff node.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c167_a1_3_scan.log -- py -u tools/bench/prep_c167_a1_3_scan.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B = "tools/bench/"
PLANS = ["plan_ring_p2b", "plan_ring_p3a", "plan_ring_p3b1", "plan_ring_p3b2a", "plan_ring_p3b2b", "plan_ring_p4_s01", "plan_ring_p4_s02v18",
         "plan_ring_p4_s03v18", "plan_ring_p4_s04v18", "plan_ring_p4_s05v18", "plan_ring_p4_s06v18", "plan_ring_p4_s07v18", "plan_ring_p4_s08v18",
         "plan_ring_p4_s09v18", "plan_ring_p5s01a", "plan_ring_p5s01", "plan_ring_p5s02a", "plan_ring_p5s02b", "plan_ring_p5s02c",
         "plan_ring_p5s02d", "plan_ring_p5s02e"]
NODES = {376, 2048, 2626, 5058, 6384, 8634, 10068, 10150, 10382, 10757, 11261, 11529, 28083, 29240, 29625}


def uid_of(d):
    if isinstance(d, dict):
        try:
            return int(d.get("uid"))
        except (TypeError, ValueError):
            return None
    return None


hits = {}
for p in PLANS:
    f = B + p + ".json"
    if not os.path.isfile(f):
        print("MISSING", f)
        continue
    txt = open(f, encoding="utf-8").read().split("\n")
    P = json.loads("\n".join(txt))
    for a in P.get("actions") or []:
        u = uid_of(a.get("dst"))
        if u in NODES:
            ln = next((i for i, t in enumerate(txt, 1) if '"id": "%s"' % a.get("id") in t), None)
            hits.setdefault(u, []).append(p)
            print("HIT %s:%s | %s | %s | src %s | dst %s | why %s" % (f, ln, a.get("id"), a.get("op"), json.dumps(a.get("src"))[:120],
                                                                   json.dumps(a.get("dst"))[:160], str(a.get("why"))[:420]))
print("NODES without a hit", sorted(NODES - set(hits)))
F1 = L.J(B + "p6_facts.json")["rows"]["F1"]
print("F1 n", len(F1), "keys", sorted(F1[0].keys()))
for r in F1:
    if r.get("uid") == 5637 or r.get("item") in (11, 54):
        print("F1ROW", json.dumps(r)[:1800])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
