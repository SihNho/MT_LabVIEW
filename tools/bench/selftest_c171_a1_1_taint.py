# ---
# labview: none
# hardware: none
# ---
r"""selftest_c171_a1_1_taint - cards 171-a1-1 / 171-a1-2 (PD412(b)-(c), gate-fp fp-103): the dry's taint follows NAMES bound
from stub reads, narrowed (171-a1-2) to names whose bound VALUE is stub-shaped (stage_prerun._stub_shaped).
OFFLINE: no COM, no LabVIEW; the fixture recipe and nothing else is written, under %TEMP%; dries run with --no-record.
EXISTING checked first: selftest_c134_1_dry.py (statement-scoped taint, T1 = the 133-3 bytes must FAIL FR; T3/T3b/T3c) and
selftest_dry_c130_5.py (executor-stop rule). Neither has a gate that reads a name bound by an EARLIER stub-touching statement.
This test calls stage_prerun's own dry (subprocess) and its _line_units / _stub_shaped; nothing is copied.
Measured shapes (diag_c171_a1_2_which_t1.log / _p170.log): plan 170's A2 reads c0 = {} (stage_replay_swap.py:39, 185 Fake uses);
T1's FR reads real = 5911 simulated rows, no Fake (bound at the 133-3 recipe's :45 `real = x.run(); s.gate(E1..)`, 21 Fake uses).
PREDICTION (one fixture, gates in this order):
  U  _line_units(stage_replay_swap.py): line 39 binds {c0}; lines 40 and 41 are ONE unit that reads c0.
  S  _stub_shaped: Fake / {} / [] / {1: Fake} / [{"a": Fake}] -> True; [{"r": 1}] / 0 / False / "x" -> False.
  a  ZA: FALSE gate on plain python data -> `FAIL  ZA` (never UNVERIFIED).
  c  ZC: c0 = {} built by iterating a stub (plan-170 shape), gate FALSE on c0.get(1) -> `UNVERIFIED  ZC`.
  b  ZB: an unrelated statement binds x from a stub (x = 0, a scalar), next gate FALSE on plain data -> `FAIL  ZB`.
  d  ZD: c0 rebound clean ({1: "y"}, no stub), gated FALSE on c0.get(1) -> `FAIL  ZD`.
  t  ZT (card 134-1 T1 shape): real = 3 simulated rows + list(stub) in ONE stub-touching statement, gate FALSE on len(real)
     -> `FAIL  ZT` (non-empty Fake-free data is not stub output).
  f  ZF: lst holds a Fake (bound in a stub-touching statement), gate FALSE on len(lst) -> `UNVERIFIED  ZF`.
  The dry ends `=== DRY FAIL: first_fail=GATE ZA ...`.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c171_a1_1_taint.log -- py -u tools/bench/selftest_c171_a1_1_taint.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                 # noqa: E402

TMP = tempfile.mkdtemp(prefix="c171_a1_1_taint_")
GRAPH = os.path.join(ROOT, "tools", "bench", "sim", "ring_p3b2_base_real_fsmap.json")
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


# U / S - the unit table on the real recipe and the value rule (stage_prerun imported; its dry is not run in-process)
sys.argv = ["x"]
import stage_prerun as SP                                            # noqa: E402
U = SP._line_units(os.path.join(ROOT, "tools", "recipes", "stage_replay_swap.py"))
u39, u40, u41 = U.get(39), U.get(40), U.get(41)
gate("U _line_units: :39 binds c0; :40-41 one unit reading c0",
     u39 is not None and "c0" in u39[1] and u40 is not None and u41 is not None and u40[0] == u41[0] and "c0" in u40[2],
     (u39 and sorted(u39[1]), u40 and u40[0], u41 and u41[0], u40 and sorted(u40[2])[:8]))
F = SP.Fake("t")
want = [(F, True), ({}, True), ([], True), ({1: F}, True), ([{"a": F}], True),
        ([{"r": 1}], False), (0, False), (False, False), ("x", False)]
got = [SP._stub_shaped(v) for v, _w in want]
gate("S _stub_shaped: Fake/empty/holds-a-Fake True; non-empty Fake-free data and scalars False", got == [w for _v, w in want],
     got)

BASE = json.load(open(GRAPH, encoding="utf-8"))
fx = os.path.join(TMP, "stage_zz_c171_a1_1_taint.py")
open(fx, "w", encoding="utf-8").write(r'''"""fixture (cards 171-a1-1/-2 self-test): names bound from stub reads."""
import os, sys
sys.path.insert(0, {tools!r})
import stagekit as K, gscript as g          # noqa: E401


def body(s):
    s.start()
    ok0 = 1 + 1 == 2
    s.gate("ZA plain false on real data", ok0 and 1 == 2)
    c0 = dict((int(x), 1) for x in g.subvis(s.work, 0))
    s.gate("ZC gate on a name bound from a stub read",
           c0.get(1) == "x")
    x = len(g.some_reader(s.work))
    s.gate("ZB plain false after an unrelated stub-binding statement", 1 == 2)
    c0 = {{1: "y"}}
    s.gate("ZD name rebound clean then gated false", c0.get(1) == "x")
    real = [{{"r": i}} for i in range(3)] + list(g.subvis(s.work, 1))
    s.gate("ZT simulated rows bound in a stub-touching statement, gated false", len(real) == 4)
    lst = [g.some_reader(s.work), len(g.other_reader(s.work))]
    s.gate("ZF a container holding a stub value, gated false", len(lst) == 3)


if __name__ == "__main__":
    st = K.Stage({vi!r}, {md5!r}, "zz_c171_a1_1", preload=False, deadline_min=5,
                 out_json=os.path.join(K.BENCH, "zz_c171_a1_1.json"), task="selftest")
    sys.exit(K.run(body, st))
'''.format(tools=os.path.join(ROOT, "tools"), vi=BASE["vi"], md5=BASE["md5"]))
p = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "stage_prerun.py"), "--dry", fx, "--no-record",
                    "--graph", GRAPH], cwd=ROOT, capture_output=True, text=True, timeout=240)
out = p.stdout
end = [ln for ln in out.splitlines() if ln.startswith("=== DRY ")]
end = end[-1] if end else "NO DRY LINE: " + out[-400:] + p.stderr[-400:]
print("  FACT  dry ends: " + end[:300], flush=True)
for ln in out.splitlines():
    if any(t in ln for t in ("  ZA ", "  ZB ", "  ZC ", "  ZD ", "  ZT ", "  ZF ")):
        print("  FACT  " + ln.strip()[:200], flush=True)


def has(prefix, lab):
    return any(ln.strip().startswith(prefix + "  " + lab) for ln in out.splitlines())


gate("a FALSE gate on plain data FAILs (ZA)", has("FAIL", "ZA") and not has("UNVERIFIED", "ZA"))
gate("c name bound to an empty container from a stub read, gated one statement later -> UNVERIFIED (ZC)",
     has("UNVERIFIED", "ZC") and not has("FAIL", "ZC"))
gate("b unrelated stub-binding statement does not relabel the next gate (ZB FAILs)", has("FAIL", "ZB")
     and not has("UNVERIFIED", "ZB"))
gate("d name rebound clean then gated FALSE -> FAILs (ZD)", has("FAIL", "ZD") and not has("UNVERIFIED", "ZD"))
gate("t T1 shape: non-empty Fake-free data bound in a stub-touching statement, gated FALSE -> FAILs (ZT)",
     has("FAIL", "ZT") and not has("UNVERIFIED", "ZT"))
gate("f a container holding a stub value, gated FALSE -> UNVERIFIED (ZF)", has("UNVERIFIED", "ZF") and not has("FAIL", "ZF"))
gate("dry ends DRY FAIL naming ZA first", end.startswith("=== DRY FAIL: first_fail=GATE ZA"), end[:200])
n_f = res.count(False)
print(P.result_line(P.make_result(res.count(True), n_f, None if not n_f else "selftest_c171_a1_1_taint")), flush=True)
sys.exit(1 if n_f else 0)
