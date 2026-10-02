r"""selftest_x10_c138_2 - card 138-2 (PD299(b), retrospective-cycle136 device-failed) self-test of X10's SOURCE read count
(stage_prerun.x10_source_reads). OFFLINE, no LabVIEW, no COM. PRIOR ART: selftest_x10_c136_2.py (edit branch, dry-count R),
selftest_x10_c132_4.py (read-only branch, loop T5), selftest_x10_c132_1.py (Executor model).
PREDICTION: S1 a script whose reads sit behind `if not DRY`, in a lambda called twice and a helper called twice -> source 5,
dry 2 -> edit model R = 1 + 5 = 6 (never the dry 2), PASS, peak == c136_2's formula; S2 a read in a for loop (+ ops) -> FAIL
UNMEASURED 'not bounded' 'inside a loop', no run; S3 lambda key= read -> UNMEASURED; S4 a read-holding helper passed as a value ->
UNMEASURED; S5 two s.start() -> sessions 2, per_session '<= 3 (total over 2 sessions'; S6 Executor record + an unbounded script ->
FAIL UNMEASURED with runs present; S7 recipes stage_d1_ring_p3b2a/b.py: source 2 each (census_snapshot @ the `snap` lambda x 2);
S8 Executor record (plan_ring_p3b2b.json) + recipe b: R == exec_R + 2, peak == exec_peak + 2 * read_mb.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_c138_2.log -- py -u tools/bench/selftest_x10_c138_2.py"""
import json, os, sys, tempfile                                                       # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P, stagexec as SX                           # noqa: E401,E402
res, tmp = [], []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


def script(text):
    fd, p = tempfile.mkstemp(prefix="x10src_c138_2_", suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    tmp.append(p)
    return p


m = SP.load_memory_model()
v = lambda k: float(m[k]["value"])                                                 # noqa: E731
MD5 = "49cf7f770fc331e06607687af640ad5e"
st = round(float(m["load_by_vi"][MD5]["value"]) + v("op0_read_mb"), 1)
base = {"executors": [], "ops": ["connect_term_uid"] * 26, "first_mutation": "Stage._op connect_term_uid",
        "input_md5": MD5, "x10_reads": ["Stage.uid_index"] * 2}
peak = lambda n, r: round(st + r * v("read_mb") + n * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
HEAD = "import stagekit as K\nDRY = True\n"
MAIN = "\nif __name__ == '__main__':\n    K.run(body, K.Stage('a', 'b', 'c'))\n"
S1 = script(HEAD + "snap = lambda s: s.census_snapshot()\n\ndef helper(s):\n    return s.uid_index('Node', 1)\n\n"
            "def body(s):\n    s.start()\n    c0 = snap(s)\n    if not DRY:\n        s.read_terms()\n    helper(s)\n"
            "    helper(s)\n    s.connect(1, 2)\n    c1 = snap(s)\n" + MAIN)
src = SP.x10_source_reads(S1)
ok, det = SP.x10_gate(S1, [], trace=base)
r = (det.get("runs") or [{}])[0]
gate("S1 DRY-guarded/lambda/helper reads: source {0} == 5, dry {1} == 2, R {2} == 6, peak {3} == {4}, PASS".format(
    src["reads"], r.get("dry_reads"), r.get("R"), r.get("peak_mb"), peak(26, 6)),
     src["reads"] == 5 and ok is True and r.get("src_reads") == 5 and r.get("dry_reads") == 2 and r.get("R") == 6
     and r.get("peak_mb") == peak(26, 6), (src["sites"], r.get("reads_line")))
S2 = script(HEAD + "def body(s):\n    s.start()\n    for i in range(3):\n        s.census_snapshot()\n    s.connect(1, 2)\n" + MAIN)
ok, det = SP.x10_gate(S2, [], trace=dict(base, x10_reads=["Stage.census"]))
gate("S2 read in a for loop: FAIL UNMEASURED, 'not bounded' + 'inside a loop', no run (never counted once)",
     ok is False and not det.get("runs") and "UNMEASURED" in det.get("why", "") and "not bounded" in det["why"]
     and "inside a loop" in det["why"] and SP.x10_source_reads(S2)["reads"] is None, det.get("why"))
S2b = script(HEAD + "def body(s):\n    a = [s.uid_index('N', u) for u in (1, 2)]\n"
             "    b = dict((u, c) for u, c in s.census_snapshot().items())\n    for x in s.census(tag='t'):\n        pass\n" + MAIN)
s2b = SP.x10_source_reads(S2b)
gate("S2b comprehension ELEMENT read unbounded; first-generator iter and for-loop iter read counted once each",
     s2b["reads"] is None and len(s2b["unbounded"]) == 1 and "uid_index" in s2b["unbounded"][0]
     and sorted((x["read"], x["times"]) for x in s2b["sites"]) == [("census", 1), ("census_snapshot", 1)], s2b)
S3 = script(HEAD + "def body(s):\n    s.start()\n    xs = sorted([1, 2], key=lambda u: s.uid_index('N', u))\n"
            "    s.connect(1, 2)\n" + MAIN)
ok, det = SP.x10_gate(S3, [], trace=base)
gate("S3 read in a key= lambda: FAIL UNMEASURED", ok is False and not det.get("runs") and "not bounded" in det.get("why", "")
     and "key" in det["why"], det.get("why"))
S4 = script(HEAD + "def rd(s):\n    return s.census_snapshot()\n\ndef body(s):\n    s.start()\n    s.retry(rd, 3)\n"
            "    s.connect(1, 2)\n" + MAIN)
ok, det = SP.x10_gate(S4, [], trace=base)
gate("S4 read-holding function passed to an unknown caller: FAIL UNMEASURED", ok is False and not det.get("runs")
     and "used as a value" in det.get("why", ""), det.get("why"))
S4c = script(HEAD + "def rd(s):\n    return s.census_snapshot()\n\ndef body(s):\n    s.start()\n    s.safe('x', rd)\n"
             "    s._op('v', lambda: s.uid_index('N', 1))\n    s.retry(lambda: s.census(), 3)\n" + MAIN)
s4c = SP.x10_source_reads(S4c)
gate("S4c fn to safe() and lambda to _op() count once each (2); lambda to an unknown caller unbounded",
     s4c["reads"] is None and sorted((x["read"], x["times"]) for x in s4c["sites"]) == [("census_snapshot", 1), ("uid_index", 1)]
     and len(s4c["unbounded"]) == 1 and "census" in s4c["unbounded"][0] and "retry" in s4c["unbounded"][0], s4c)
S4b = script(HEAD + "def stop(loop, body):\n    return s.uid_index('Diagram', body)\n\ndef body(_):\n    s.start()\n"
             "    stop(1, 2)\n" + MAIN)
s4b = SP.x10_source_reads(S4b)
gate("S4b a PARAMETER named like the module function `body` is not a reference to it: reads {0} == 1, bounded".format(s4b["reads"]),
     s4b["reads"] == 1 and not s4b["unbounded"], s4b)
S5 = script(HEAD + "def body(s):\n    s.start()\n    s.census_snapshot()\n    s.restart()\n    s.census_snapshot()\n"
            "    s.uid_index('N', 1)\n" + MAIN)
s5 = SP.x10_source_reads(S5)
gate("S5 two sessions: sessions {0} == 2, reads {1} == 3, per_session {2!r} is the total bound".format(
    s5["sessions"], s5["reads"], s5["per_session"]), s5["sessions"] == 2 and s5["reads"] == 3
     and str(s5["per_session"]).startswith("<= 3 (total over 2 sessions"), s5)
PL = os.path.join(B, "plan_ring_p3b2b.json")
ops = SX.compile_plan(json.load(open(PL, encoding="utf-8")))
REC = {"plan": "tools/bench/plan_ring_p3b2b.json", "kinds": [o["kind"] for o in ops], "stop_after": None, "from_step": None,
       "error": None, "checkpoints": sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))}
ok, det = SP.x10_gate(S2, [REC])
gate("S6 Executor + a loop read in the script: FAIL UNMEASURED although the Executor run is modelled",
     ok is False and det.get("runs") and "UNMEASURED" in det.get("why", "") and "not bounded" in det["why"], det.get("why"))
for rn in ("stage_d1_ring_p3b2a.py", "stage_d1_ring_p3b2b.py"):
    s7 = SP.x10_source_reads(os.path.join(ROOT, "tools", "recipes", rn))
    gate("S7 {0}: source reads {1} == 2 (census_snapshot via snap x2), sessions {2} == 1".format(rn, s7["reads"], s7["sessions"]),
         s7["reads"] == 2 and s7["sessions"] == 1 and [(x["read"], x["times"]) for x in s7["sites"]] == [("census_snapshot", 2)],
         s7["sites"])
RB = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2b.py")
ok, det = SP.x10_gate(RB, [REC])
r = (det.get("runs") or [{}])[0]
gate("S8 recipe b + its plan record: R {0} == exec_R {1} + 2; peak {2} == exec {3} + 2*{4}; ok {5}".format(
    r.get("R"), r.get("exec_R"), r.get("peak_mb"), r.get("exec_peak_mb"), v("read_mb"), ok),
     r.get("R") == (r.get("exec_R") or 0) + 2 and r.get("peak_mb") == round(r["exec_peak_mb"] + 2 * v("read_mb"), 1)
     and ok == (r["peak_mb"] <= v("fail_above_mb")), r.get("reads_line"))
for p in tmp:
    os.remove(p)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
