# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_166-a1-1.json
# ---
"""diag_c166_a1_1_q - card 166-a1-1 (OFFLINE, read-only JSON query): print the terminal rows of the given owner uids / wire uids /
term uids in a stored graph file or a stagesim step file ({"state": {...}}). argv: <json> <owners,> [<wires,>] [<terms,>]; with
terms given, the rows on those terms' wires are printed too. uids compared as strings (stagesim new uids are not ints)."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as PR  # noqa: E402


def ids(i):
    return set(x for x in sys.argv[i].split(",") if x) if len(sys.argv) > i else set()


owners, wires, terms = ids(2), ids(3), ids(4)
G = json.load(open(sys.argv[1], encoding="utf-8"))
G = G.get("state", G)
T = G["terminals"]
print("KEYS row {0}".format(sorted(T[0].keys())), flush=True)
wires |= set(str(r.get("wire_uid")) for r in T if str(r.get("term_uid")) in terms and r.get("wire_uid"))
for r in T:
    if str(r.get("owner_uid")) in owners or str(r.get("wire_uid")) in wires or str(r.get("term_uid")) in terms:
        print("ROW " + json.dumps(r, sort_keys=True), flush=True)
cls = dict((str(o["uid"]), o) for o in G.get("objs") or [])
for u in sorted(owners):
    print("OBJ #{0} {1}".format(u, json.dumps(cls.get(u), sort_keys=True)), flush=True)
print(PR.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}), flush=True)
