"""card 116-1 - the regression set for the stop-record / guard_card / doc_lint / audit_cycle / launch-gate edits, OFFLINE.

    py tools/bench/diag_c116a_regress.py before|after

Existed first: diag_c115a_regress.py (child runner + RESULT parse, copied), diag_c111c_regress.py (stop-record module set).
No LabVIEW: every child is a pure-Python self-test (grep for win32com/gscript/lv_gui over the set: none import them).
FAILURES ON RECORD BEFORE THIS CARD (PD229(c)): selftest_errorlist_reuse_81 K9 PASSES by asserting the guard_card `cd`
hole EXISTS (archive/peer/2026-09-25-hyp-selftest-elreuse-81.md:116); the fix flips it, so K9 is re-pinned to rc 2 and
is the ONE declared verdict change. Nothing else on record fails.
Prediction contract:
  before: every child ends with a RESULT line; its failing-label set is saved to diag_c116a_regress_before.json.
  after : G1 every child's failing-label set == before's (K9 re-pinned: it must now PASS as "refused");
          G2 no child that passed before fails after; G3 the new children (selftest_stoprecord_c116a, selftest_c116a_landed)
          RESULT PASS fail 0.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

PY = sys.executable
NAMES = ["stoprecord_table", "stoprecord_bgrun", "stoprecord_eqform", "stoprecord_supersession", "stoprecord_offline_c107",
         "c103d_hooks", "c106d_tools", "c108e_tools", "c111c_launchunit", "c110_launchgate", "launch_gate",
         "stage_prerun_headcmp_79-6", "errorlist_reuse_81", "audit_c7", "audit_cost_window", "audit_c4c_split"]
NEW = ["stoprecord_c116a", "c116a_landed"]
# card 116-3 R1, review archive/peer/2026-09-28-c116c-regress.md (supported): FAIL_RE also matches `-> FAIL <x>`
# (selftest_stoprecord_supersession.py:65) and `**FAIL** <x>` (selftest_audit_c7.py:27); the failing set is a MULTISET
# (two gates may share a label, c111c D4h) and G4 gates the fail count; a tally is read from the LAST non-empty line only.
FAIL_RE = re.compile(r"^\s*(?:->\s*)?(?:GATE\s+(.+?)\s+FAIL\b|\*\*FAIL\*\*\s+(\S+)|\[?FAIL\]?\s+(\S+))", re.M)


def child(name, tag):
    log = os.path.join(HERE, "selftest_{0}_c116a_{1}.log".format(name, tag))
    path = os.path.join(HERE, "selftest_{0}.py".format(name))
    if not os.path.exists(path):
        return None, None, [], os.path.relpath(log, ROOT)
    with open(log, "w", encoding="utf-8") as f:
        try:
            rc = subprocess.call([PY, "-u", path], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=600)
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
    body = open(log, encoding="utf-8", errors="replace").read()
    res = None
    for line in body.splitlines():
        if line.startswith("RESULT "):
            try:
                res = json.loads(line[7:])
            except ValueError:
                res = None
    fails = sorted(x for x in ((m.group(1) or m.group(2) or m.group(3) or "").strip()[:60]
                               for m in FAIL_RE.finditer(body)) if x)
    if res is None:                  # older self-tests print a tally instead of a C6 RESULT line
        last = next((ln for ln in reversed(body.splitlines()) if ln.strip() and not ln.startswith("BGRUN")), "")
        t = TALLY_RE.findall(last)
        if t:
            p, f = int(t[-1][0]), int(t[-1][1])
            res = {"status": "PASS" if f == 0 and rc == 0 else "FAIL", "gates": {"pass": p, "fail": f}, "tally": True}
    return rc, res, fails, os.path.relpath(log, ROOT)


TALLY_RE = re.compile(r"(\d+) pass(?:,| /)\s*(\d+) fail")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "after"
    G = []

    def gate(l, ok, d=""):
        G.append((l, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:400]), flush=True)
    got = {}
    for name in NAMES + (NEW if tag != "before" else []):
        rc, res, fails, log = child(name, tag)
        g = (res or {}).get("gates") or {}
        got[name] = {"rc": rc, "status": (res or {}).get("status"), "pass": g.get("pass"), "fail": g.get("fail"),
                     "fails": fails}
        print("SELFTEST {0}: rc {1} status {2} pass {3} fail {4} fails {5} ({6})".format(
            name, rc, got[name]["status"], g.get("pass"), g.get("fail"), fails, log), flush=True)
    snap = os.path.join(HERE, "diag_c116a_regress_before.json")
    if tag == "before":
        json.dump(got, open(snap, "w", encoding="utf-8"), indent=1)
        for name in NAMES:
            gate("B {0} printed a RESULT line or a tally".format(name), got[name]["status"] is not None, got[name])
        on_record = {"stoprecord_offline_c107": (15, 10), "c111c_launchunit": (32, 1), "stage_prerun_headcmp_79-6": (1, 1)}
        for name in NAMES:           # PD229(c): the failures on record are NAMED; any other failure is new
            want = on_record.get(name)
            g = got[name]
            ok = ((g["status"] == "FAIL" and (g["pass"], g["fail"]) == want) if want else g["status"] == "PASS")
            # headcmp H1 is FLAKY, not fixed: 116-1 saw 1/1, the rerun (diag_c116a_regress_before2.log:14) 2/0. Its HEAD
            # copy of selftest_launch_gate.py uses a PID-named sandbox (L1's defect; suspected, not measured, as the
            # cause), so either verdict is on record.
            if name == "stage_prerun_headcmp_79-6" and g["status"] == "PASS":
                ok = True
            gate("B2 {0} {1}".format(name, "on-record FAIL %d/%d" % want if want else "PASS"), ok, (g["pass"], g["fail"]))
    else:
        before = json.load(open(snap, encoding="utf-8"))
        for name in NAMES:
            b, a = before.get(name) or {}, got[name]
            gate("G1 {0} failing set unchanged ({1})".format(name, b.get("fails")), a["fails"] == b.get("fails"),
                 (a["fails"], a["pass"], a["fail"]))
            gate("G2 {0} status not worse ({1} -> {2})".format(name, b.get("status"), a["status"]),
                 not (b.get("status") == "PASS" and a["status"] != "PASS"), (b.get("pass"), a["pass"]))
            gate("G4 {0} fail count not higher ({1} -> {2})".format(name, b.get("fail"), a["fail"]),
                 a["fail"] is not None and (b.get("fail") is None or a["fail"] <= b["fail"]), a["rc"])
        for name in NEW:
            a = got[name]
            gate("G3 new {0} RESULT PASS fail 0".format(name), a["status"] == "PASS" and a["fail"] == 0 and a["rc"] == 0, a)
    n = sum(1 for _l, ok in G if ok)
    first = next((l for l, ok in G if not ok), None)
    print("=== GATES: {0} pass / {1} fail".format(n, len(G) - n))
    print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
    return 0 if first is None else 1


if __name__ == "__main__":
    sys.exit(main())
