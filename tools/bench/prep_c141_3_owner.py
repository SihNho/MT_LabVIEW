r"""prep_c141_3_owner - card 141-3 pass item 1 (PD325(b)): OFFLINE owner check from the logs, no LabVIEW.
Claim under test (review archive/peer/2026-10-02-c141-2-scratch-td.md): the two "survivors" of gate TD in the 141-2 scratch,
terminal uids 28004 / 28979, belonged in the BASE graph to the deleted Insert Into Array nodes #27928 / #28916 and in the scratch to
the NEW Replace Array Subset nodes #6942 / #6805 (LabVIEW re-used the freed uids in-session).
Sources: base graph tools/bench/graph_ring_p3b2b_20261002_133824.json (md5 pinned by the card), scratch log
tools/bench/diag_c141_p4s01_scratch.log (md5 pinned), sim end tools/bench/sim/ring_p4_s01/ring_p4_s01/step_24_wire.json.
PRIOR ART: none for this check (the review's step 4.1 names it; done here by script, not by hand).
PREDICTION: O1-O5 PASS. Any FAIL -> card rule "else return".
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c141_3_owner.log -- py -u tools/bench/prep_c141_3_owner.py"""
import ast, hashlib, json, os, re, sys                                                  # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                         # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
LOG = os.path.join(B, "diag_c141_p4s01_scratch.log")
SIM = os.path.join(B, "sim", "ring_p4_s01", "ring_p4_s01", "step_24_wire.json")
WANT = {28004: (27928, 6942), 28979: (28916, 6805)}                                    # uid -> (base owner, scratch owner), PD325(b)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                           # noqa: E731
G = []


def gate(label, ok, d=""):
    G.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


gate("O0 inputs md5 == card (graph 50595c62, log 17c5caf6)", md5(GRAPH) == "50595c62d0332a94bf066538cf20c0ae" and md5(LOG) == "17c5caf6fc8c1dece1a099a51e444e8e",
     (md5(GRAPH), md5(LOG)))
base = json.load(open(GRAPH, encoding="utf-8"))["terminals"]
L = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
brow = dict((int(r["term_uid"]), r) for r in base)
gate("O1 base: 28004/28979 are 'output array' of #27928/#28916",
     all(u in brow and int(brow[u]["owner_uid"]) == WANT[u][0] and brow[u]["term_name"] == "output array" for u in WANT),
     dict((u, (brow.get(u) or {}).get("owner_uid")) for u in WANT))
dele = dict((int(m.group(1)), i + 1) for i, ln in enumerate(L) for m in [re.search(r"stagexecdeleted GrowableFunction #(\d+) -> gone \[(\d+)\]", ln)] if m)
cen = [i + 1 for i, ln in enumerate(L) if re.search(r"delete_object GrowableFunction #(27928|28916) CENSUS DIFF: Node 665 -> 664", ln)]
gate("O2 log: #27928 and #28916 deleted (gone, node census 665 -> 664 each)", all(WANT[u][0] in dele for u in WANT) and len(cen) == 2,
     {"deleted_at": dele, "census_lines": cen})
td = [(i + 1, ln) for i, ln in enumerate(L) if ln.startswith("  FAIL  TD ")]
diff = set()
if len(td) == 1:
    dd = ast.literal_eval(td[0][1][td[0][1].index("{"):])
    diff = set(dd["plan_deletes"]) - set(dd["lost_rows"])
gate("O3 log: the one TD FAIL line's plan_deletes - lost_rows == {28004, 28979}", diff == set(WANT), {"line": [t[0] for t in td], "diff": sorted(diff)})
made = {}                                                                               # (diagram_index, nodes_index) -> new uid
names = {}                                                                              # (new uid, t index) -> name
for ln in L:
    m = re.search(r"new #(\d+) #\d+ lives at: \{'diagram_index': (\d+), .*'nodes_index': (\d+)", ln)
    if m:
        made[(int(m.group(2)), int(m.group(3)))] = int(m.group(1))
    m = re.search(r"new #(\d+) t(\d+)\s+'([^']*)'", ln)
    if m:
        names[(int(m.group(1)), int(m.group(2)))] = m.group(3)
found = {}
for i, ln in enumerate(L):
    m = re.search(r"FACT  connect #(\d+)->#(\d+) AFTER", ln)
    if m and int(m.group(2)) in WANT:
        prev = [p for p in L[max(0, i - 3):i] if "OP connect_from_wire sink D[" in p]
        a = re.search(r"sink D\[(\d+)\]\.N\[(\d+)\]\.t(\d+)", prev[-1]) if prev else None
        own = made.get((int(a.group(1)), int(a.group(2)))) if a else None
        found[int(m.group(2))] = {"line": i + 1, "sink": a.group(0) if a else None, "owner": own,
                                  "name": names.get((own, int(a.group(3)))) if a and own else None}
gate("O4 log: in the scratch, 28004 is a terminal of NEW #6942 and 28979 of NEW #6805 (connect sink address -> created node)",
     all((found.get(u) or {}).get("owner") == WANT[u][1] for u in WANT), found)
st = json.load(open(SIM, encoding="utf-8"))
st = st.get("state", st)
srows = st["terminals"]
s_uids = set(str(r["term_uid"]) for r in srows)
newown = [r for r in srows if str(r.get("owner_uid")) not in set(str(b["owner_uid"]) for b in base)]
gate("O5 sim end: no row 28004/28979 (so the plan 'deletes' them) and the new nodes' rows carry non-base owners",
     not (s_uids & set(str(u) for u in WANT)) and len(newown) > 0,
     {"new_owner_rows": len(newown), "sample": [dict((k, r.get(k)) for k in ("term_uid", "owner_uid", "term_name", "wire_uid")) for r in newown[:4]]})
n = sum(1 for _l, ok in G if ok)
ff = next((lab for lab, ok in G if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(G) - n, ff, [])), flush=True)
sys.exit(0 if ff is None else 1)
