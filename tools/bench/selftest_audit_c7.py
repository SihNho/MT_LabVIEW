"""Self-test for audit_cycle.c7_plan() (card 90-2, retrospective-cycle89 `device-failed`).

Prediction contract (each case is one gate):
  S1  next.json plan.path valid            -> that file, basis 'tools/bench/next.json plan.path'
  S2  next.json absent                     -> fallback (doc_lint current plan or newest cycle plan), basis != next.json
  S3  next.json plan.path names a missing file -> fallback
  S4  next.json has no plan key / not JSON -> fallback
  S5  NEGATIVE: next.json names plan B while a `status: current` plan A exists -> B is chosen, not A
  S6  live repo: c7_plan() returns the file next.json names (docs/d1-loop12-17-split-plan.md today)
Runs on a temporary root; doc_lint.current_plans() is monkeypatched to point at the temp plan A. No LabVIEW.
"""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import audit_cycle  # noqa: E402
import doc_lint  # noqa: E402
import protocol  # noqa: E402

gates = []


def gate(name, ok, detail=""):
    gates.append((name, bool(ok)))
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}" + (f"  [{detail}]" if detail else ""))


def make_root(next_obj, write_next=True):
    r = tempfile.mkdtemp(prefix="c7_")
    os.makedirs(os.path.join(r, "docs"))
    os.makedirs(os.path.join(r, "tools", "bench"))
    a = os.path.join(r, "docs", "planA.md")
    b = os.path.join(r, "docs", "planB.md")
    for p in (a, b):
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("---\ntype: plan\nstatus: current\n---\nx\n")
    if write_next:
        with open(os.path.join(r, "tools", "bench", "next.json"), "w", encoding="utf-8") as fh:
            fh.write(next_obj if isinstance(next_obj, str) else json.dumps(next_obj))
    return r, a, b


_orig = doc_lint.current_plans
try:
    # S1
    r, a, b = make_root({"plan": {"path": "docs/planB.md"}})
    doc_lint.current_plans = lambda: [a]
    p, basis = audit_cycle.c7_plan(root=r)
    gate("S1 next.json plan.path valid -> chosen", p == b and basis == "tools/bench/next.json plan.path", f"{p} | {basis}")
    # S5 negative: A is 'current', next names B -> B
    gate("S5 NEGATIVE: current plan A != next.json plan B -> B wins", p == b and p != a)
    # S2
    r, a, b = make_root(None, write_next=False)
    doc_lint.current_plans = lambda: [a]
    p, basis = audit_cycle.c7_plan(root=r)
    gate("S2 next.json absent -> fallback current plan", p == a and "next.json" not in basis, f"{p} | {basis}")
    # S3
    r, a, b = make_root({"plan": {"path": "docs/nope.md"}})
    doc_lint.current_plans = lambda: [a]
    p, basis = audit_cycle.c7_plan(root=r)
    gate("S3 plan.path missing file -> fallback", p == a and "next.json" not in basis, f"{p} | {basis}")
    # S4a no plan key
    r, a, b = make_root({"cycle": 1})
    doc_lint.current_plans = lambda: [a]
    p, basis = audit_cycle.c7_plan(root=r)
    gate("S4a no plan key -> fallback", p == a, f"{p} | {basis}")
    # S4b not JSON
    r, a, b = make_root("{not json")
    doc_lint.current_plans = lambda: [a]
    p, basis = audit_cycle.c7_plan(root=r)
    gate("S4b unreadable next.json -> fallback", p == a, f"{p} | {basis}")
    # S4c fallback with no current plan -> newest cycle plan
    r, a, b = make_root("{not json")
    with open(os.path.join(r, "docs", "cycle3-plan.md"), "w") as fh:
        fh.write("x")
    doc_lint.current_plans = lambda: []
    p, basis = audit_cycle.c7_plan(root=r)
    gate("S4c no current plan -> newest docs/cycle<N>-plan.md", p and p.endswith("cycle3-plan.md"), f"{p} | {basis}")
finally:
    doc_lint.current_plans = _orig

# S6 live
with open(os.path.join(ROOT, "tools", "bench", "next.json"), encoding="utf-8") as fh:
    live_rel = json.load(fh)["plan"]["path"]
p, basis = audit_cycle.c7_plan()
gate("S6 live repo: c7_plan() == next.json plan.path",
     p and os.path.normcase(os.path.abspath(p)) == os.path.normcase(os.path.join(ROOT, live_rel.replace("/", os.sep)))
     and basis == "tools/bench/next.json plan.path", f"{p} | {basis}")

npass = sum(1 for _, ok in gates if ok)
nfail = len(gates) - npass
print(f"GATES {npass} pass / {nfail} fail")
print(protocol.result_line({"status": "PASS" if nfail == 0 else "FAIL", "gates": {"pass": npass, "fail": nfail},
                            "first_fail": next((n for n, ok in gates if not ok), None), "artefacts": []}))
sys.exit(0 if nfail == 0 else 1)
