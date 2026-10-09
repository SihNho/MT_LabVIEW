# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-1.md
# ---
"""prep_c156_a1_1_probe2 - card 156-a1-1 (OFFLINE, json only): read-only look at the cycle-155 pass-A sim step files around the #376
move (step 09 -> 10): do out-tunnels #5204 / #10404 and RSRs #24083 / #24150 survive mv_376, and what are their wires. Prediction: rows
print for both steps; RESULT 1/0.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c156_a1_1_probe2.log -- py -u tools/bench/prep_c156_a1_1_probe2.py"""
import collections, json, os, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
D = os.path.join(ROOT, "tools", "bench", "sim", "ring_p5s02", "_passA", "ring_p5s02p")
for f in ("step_09_create.json", "step_10_move_in.json", "step_12_move_in.json"):
    st = json.load(open(os.path.join(D, f), encoding="utf-8"))
    S = st["state"]
    T = S["terminals"]
    print("FILE", f, "effect", json.dumps(st.get("effect"), default=str)[:900])
    BYW = collections.defaultdict(list)
    for r in T:
        if r.get("wire_uid"):
            BYW[r["wire_uid"]].append(r)
    for u in (5204, 10404, 24083, 24150, 376, 3453):
        rs = [r for r in T if int(r["owner_uid"]) == u]
        print("  OWN", u, len(rs))
        for r in rs:
            if u == 376 and r["term_name"] not in ("file progress", "file number to append out", "error out", "total data array out"):
                continue
            print("    T", r["term_uid"], repr(r["term_name"]), r["term_class"], r["is_source"], r.get("wire_uid"), r.get("frame_diagram"),
                  [(x["owner_uid"], x["term_name"], x["term_uid"]) for x in BYW.get(r.get("wire_uid"), []) if x["term_uid"] != r["term_uid"]])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
