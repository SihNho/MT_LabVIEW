"""Card 134-4 step 4 (offline, read-only): F3 listed objects 10363 (b on the real graph) vs 10334 (04204133's end, provisional
base); terminals / wires / owners equal. Is the +29 (OuterTerminal 1, InnerTerminal 2, Terminal 18, Wire 8) in the BASE (a's real
read vs a's simulated end) or in b's DELTA? Compares objs class counts of the two bases and the two ends.
PREDICTION: the base diff == the end diff (+29), b's delta per class identical on both bases."""
import collections, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                           # noqa: E402
J = lambda p: json.load(open(os.path.join(ROOT, p) if not os.path.isabs(p) else p, encoding="utf-8"))   # noqa: E731
REF, PB = J("tools/bench/plan_ring_p3b2.json"), J("tools/bench/plan_ring_p3b2b.json")
fr, fb = REF["finalized"]["step_files"], PB["finalized"]["step_files"]
print("  FACT  ref step files {0} (first {1}, last {2}); b step files {3} (first {4})".format(
    len(fr), fr[0]["path"], fr[-1]["path"], len(fb), fb[0]["path"]), flush=True)
cc = lambda s: collections.Counter(o.get("class") for o in s["objs"])                           # noqa: E731
S = {}
for nm, fl in (("ref", fr), ("b", fb)):
    first, last = J(fl[0]["path"]), J(fl[-1]["path"])
    S[nm] = (cc(first.get("state") or first), cc(last["state"]), first.get("n", first.get("step")), last.get("n", last.get("step")))
d = lambda a, b: dict((k, b[k] - a[k]) for k in set(a) | set(b) if b[k] != a[k])              # noqa: E731
print("  FACT  ref first-step objs {0}, end {1}; b first-step objs {2}, end {3}".format(
    sum(S["ref"][0].values()), sum(S["ref"][1].values()), sum(S["b"][0].values()), sum(S["b"][1].values())), flush=True)
print("  FACT  first-step diff (b - ref) {0}".format(d(S["ref"][0], S["b"][0])), flush=True)
print("  FACT  end diff (b - ref) {0}".format(d(S["ref"][1], S["b"][1])), flush=True)
db, dr = d(S["b"][0], S["b"][1]), d(S["ref"][0], S["ref"][1])
print("  FACT  delta over the session (end - first): ref {0}; b {1}".format(dr, db), flush=True)
# 04204133 = sessions a + b in one plan (40 step files = base + 39 actions); b = its last len(fb)-1 actions, so a's SIMULATED end
# is ref step file [len(fr) - len(fb)] (the state before b's first action)
na = len(fr) - len(fb)
aend = J(fr[na]["path"])["state"]
ca = cc(aend)
print("  FACT  ref step [{0}] = {1} (a's simulated end): objs {2}".format(na, fr[na]["path"], sum(ca.values())), flush=True)
print("  FACT  base diff: a's REAL read (b first) - a's SIMULATED end {0}".format(d(ca, S["b"][0])), flush=True)
drb = d(ca, S["ref"][1])
print("  FACT  b's delta: on a's simulated end {0}; on a's real read {1}".format(drb, db), flush=True)
ok = d(ca, S["b"][0]) == d(S["ref"][1], S["b"][1]) and drb == db
print("{0}  O1 the end diff == the base diff (a real vs a simulated), b's own delta identical on both bases".format(
    "PASS" if ok else "FAIL"), flush=True)
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "O1 objdiff not in the base", [])), flush=True)
