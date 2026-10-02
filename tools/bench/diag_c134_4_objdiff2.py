"""Card 134-4, the objdiff review's cheapest test (archive/peer/2026-10-02-c134-4-objdiff.md:69-76), OFFLINE, read-only.
Replaces diag_c134_4_objdiff.py's gate O1 (it indexed ref step 21 as a's end; a's actions are non-contiguous [1-7,14-19,24-27,32-35]).
(1) objs class counts: a's SIMULATED end (tools/bench/sim/ring_p3b2b_base_provisional.json) vs a's REAL read (b's step_00_base,
= graph_ring_p3b2a_fs_20261002_102553.json). (2) the extra Wire / Terminal / Inner / OuterTerminal rows of the real read: their uids,
and for Terminal-like rows whether an owner (via the terminal table) is a node a created (uid absent from the pre-a base).
PREDICTION: Q1 diff == {OuterTerminal 1, InnerTerminal 2, Terminal 18, Wire 8}, no node class; Q2 the 8 Wire uids are all absent from
the provisional (simulated) objs and listed; Q3 b's node delta identical on both bases (end - base per class)."""
import collections, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                           # noqa: E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                         # noqa: E731
prov = J("tools/bench/sim/ring_p3b2b_base_provisional.json")
prov = prov.get("state") or prov
real = J("tools/bench/sim/ring_p3b2b/step_00_base.json")
real = real.get("state") or real
cc = lambda s: collections.Counter(o.get("class") for o in s["objs"])                           # noqa: E731
d = lambda a, b: dict((k, b[k] - a[k]) for k in set(a) | set(b) if b[k] != a[k])              # noqa: E731
q1 = d(cc(prov), cc(real))
want = {"OuterTerminal": 1, "InnerTerminal": 2, "Terminal": 18, "Wire": 8}
ok = []
ok.append(q1 == want)
print("{0}  Q1 objs class diff a-real - a-sim == {1}  got {2} (sim {3}, real {4})".format(
    "PASS" if ok[-1] else "FAIL", want, q1, len(prov["objs"]), len(real["objs"])), flush=True)
pu = set(int(o["uid"]) for o in prov["objs"])
extra = collections.defaultdict(list)
for o in real["objs"]:
    if o.get("class") in want and int(o["uid"]) not in pu:
        extra[o["class"]].append(int(o["uid"]))
print("  FACT  real-only rows by class: {0}".format(dict((k, sorted(v)) for k, v in extra.items())), flush=True)
AW = {28871, 29097, 29131, 29144, 29154, 29168, 29176, 29260, 29270, 29305}
ok.append(len(extra.get("Wire", [])) == 8)
print("{0}  Q2 8 real-only Wire rows; in a's recorded new-wire set: {1}".format(
    "PASS" if ok[-1] else "FAIL", sorted(set(extra.get("Wire", [])) & AW)), flush=True)
tu = set(int(r["term_uid"]) for r in real["terminals"])
for k in ("Terminal", "InnerTerminal", "OuterTerminal"):
    us = extra.get(k, [])
    own = collections.Counter(next((r["owner_class"] for r in real["terminals"] if int(r["term_uid"]) == u), "<not a term row>") for u in us)
    print("  FACT  {0} rows: {1} of {2} are terminal-table uids; owner classes {3}".format(k, len(set(us) & tu), len(us), dict(own)), flush=True)
REF, PB = J("tools/bench/plan_ring_p3b2.json"), J("tools/bench/plan_ring_p3b2b.json")
bend = J(PB["finalized"]["step_files"][-1]["path"])["state"]
nodecls = lambda c: dict((k, v) for k, v in c.items() if k not in want)                        # noqa: E731
db = nodecls(d(cc(real), cc(bend)))
pf = os.path.join(ROOT, "tools/bench/plan_ring_p3b2b_provisional_c133_5.json")
print("  FACT  b's node delta on a's real read {0}".format(db), flush=True)
if os.path.isfile(pf):
    pp = json.load(open(pf, encoding="utf-8"))
    sf = (pp.get("finalized") or {}).get("step_files") or []
    if sf and os.path.isfile(os.path.join(ROOT, sf[-1]["path"])):
        print("  FACT  provisional b end file {0} (may be overwritten by later finalizes)".format(sf[-1]["path"]), flush=True)
nf = ok.count(False)
print(P.result_line(P.make_result(len(ok) - nf, nf, None if not nf else "Q1/Q2 objdiff2", [])), flush=True)
sys.exit(1 if nf else 0)
