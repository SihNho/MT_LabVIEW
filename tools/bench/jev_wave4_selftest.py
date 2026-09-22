r"""jev_wave4_selftest - the FOURTH WAVE: #5, #7 and #2 of docs/jev-integration-plan.md's 2nd-wave table wired
as ADVISORY signals (user 2026-09-23: "배선 하나하나 물어본다던지 Jev 최대한 활용하는 방법으로 제시한게 위의
테이블이잖아" - the table was approved in full on 2026-09-22, but #5/#7 stayed CLI-only and #2 a manual aid).

    py tools/bgrun.py --max-min 10 --log tools/bench/jev_wave4_selftest.log -- py -u tools/bench/jev_wave4_selftest.py

WHAT IT PROVES, WITH NO KEY AND NO NETWORK (every model call is stubbed; a real key changes nothing here):

  A  #5 ROW CHECK    jev_rowcheck.normalise_row accepts BOTH documented schemas and refuses a third;
                     check_rows is time-capped, key-less-safe and never raises; stage_lines' line format.
  B  #5 IN STAGEKIT  a Stage with 3 fake rows prints one JEV-ROWCHECK line per row, fires ONCE, and the
                     firing point is `_op`'s first statement - i.e. before the first mutating call.
  C  #7 CONTRADICT   audit_cycle._jev_contradict records a baseline on a first run, asks only about items
                     ADDED since, writes its state atomically, and prints the JEV-CONTRADICT line; and
                     `audit_cycle.py` itself still exits exactly as it did (two runs, --no-jev vs off).
  D  #2 GATE-ROW     guard_peer.gaterow_advisory turns a fake failing log into per-row lines, writes them to
                     jev_gate.log, and is rate-limited to ONE reading per log revision.

NO LabVIEW: `stagekit` is imported (it imports `gscript`, which only Dispatches on demand) but NO Stage is
started, no VI is opened, no mutator runs - case B calls the advisory hook directly and reads `_op`'s source.
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

P = F = 0


def gate(label, ok, detail=""):
    global P, F
    ok = bool(ok)
    if ok:
        P += 1
    else:
        F += 1
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label, ("  " + str(detail)) if detail else ""),
          flush=True)
    return ok


def head(t):
    print("\n---------- {0}".format(t), flush=True)


class _Canned(object):
    """A stand-in for tools/jev.py: no socket is opened, and every call is counted."""

    def __init__(self, noul=0.93, key="TEST", err=None):
        self.noul_value, self.key, self.err, self.calls = noul, key, err, 0
        self.UNKNOWN_LO, self.UNKNOWN_HI = 0.30, 0.70

    def get_key(self):
        return self.key

    def ask(self, state, questions, purpose="", timeout=60, retries=3):
        self.calls += 1
        if self.err:
            return None, self.err
        name = next(iter(questions))
        return {"answers": {name: {"type": "noul", "noul": self.noul_value}}}, None

    def ask_n(self, state, questions, n=None, purpose="", timeout=60, retries=3):
        self.calls += 1
        if self.err:
            return None, None, self.err
        return self.noul_value, {"spread": 0.0, "n": n or 3, "n_ok": n or 3, "values": [self.noul_value]}, None

    def noul(self, resp, name=None):
        try:
            return float(resp["answers"][name]["noul"])
        except Exception:                                                          # noqa: BLE001
            return None

    def verdict(self, p):
        if p is None:
            return "unknown"
        return "yes" if p >= self.UNKNOWN_HI else ("no" if p <= self.UNKNOWN_LO else "unknown")


# ============================================================ A - #5 the row-check API
def case_a():
    head("A  #5 jev_rowcheck: the two accepted schemas, the budget, the key-less path")
    import jev_rowcheck as RC

    shape_a = {"uid": 10429, "i": 21, "name": "Tunnel", "is_source": False, "wire": 1731,
               "source": {"uid": 23868, "i": 3, "name": "output", "is_source": True}}
    shape_b_sub = {"row": "D", "wire": 1731,
                   "source": {"uid": 23868, "term": 3, "name": "output"},
                   "sink": {"uid": 10429, "term": 21, "name": "Tunnel"}}
    shape_b_flat = {"id": "E", "src_uid": 23868, "src_term": 3, "src_name": "output",
                    "sink_uid": 10429, "sink_term": 21, "sink_name": "Tunnel"}

    na, nb, nf = RC.normalise_row(shape_a), RC.normalise_row(shape_b_sub), RC.normalise_row(shape_b_flat)
    gate("A1 shape A normalises to itself", na and na["uid"] == 10429 and na["source"]["uid"] == 23868, na)
    gate("A2 shape B (sub-dicts) folds into shape A",
         nb and nb["uid"] == 10429 and nb["i"] == 21 and nb["source"]["uid"] == 23868 and nb["source"]["i"] == 3,
         nb)
    gate("A3 shape B (flat keys) folds into shape A",
         nf and nf["uid"] == 10429 and nf["i"] == 21 and nf["source"]["uid"] == 23868 and nf["source"]["i"] == 3,
         nf)
    gate("A4 the two ends are not swapped", nb["name"] == "Tunnel" and nb["source"]["name"] == "output")
    gate("A5 a third shape is refused, not guessed at",
         RC.normalise_row({"foo": 1}) is None and RC.normalise_row("not a dict") is None)
    gate("A6 the row label is carried through", nb.get("label") == "D" and nf.get("label") == "E")

    real, canned = RC.jev, _Canned(noul=0.93)
    try:
        RC.jev = canned
        rows = [shape_a, shape_b_sub, shape_b_flat]
        by_uid = {10429: [{"table": "t", "uid": 10429, "i": 21, "name": "Tunnel", "is_source": False}],
                  23868: [{"table": "t", "uid": 23868, "i": 3, "name": "output", "is_source": True}]}
        res = RC.check_rows(rows, by_uid=by_uid)
        gate("A7 three rows -> three results, all `ok` at p=0.93",
             len(res) == 3 and all(r["verdict"] == "ok" and abs(r["p"] - 0.93) < 1e-9 for r in res),
             [(r["label"], r["verdict"], r["p"]) for r in res])
        gate("A8 one model call per row", canned.calls == 3, canned.calls)

        canned.calls = 0
        res = RC.check_rows(rows, by_uid=by_uid, budget_s=-1.0)
        gate("A9 a spent budget skips every row and spends NOTHING",
             all(r["verdict"] == "skipped" for r in res) and canned.calls == 0, canned.calls)

        canned.key, canned.calls = None, 0
        lines = RC.stage_lines(rows, "selftest_stage", by_uid=by_uid, write_log=False)
        gate("A10 no key -> ONE line, no call", len(lines) == 1 and "no key" in lines[0] and canned.calls == 0,
             lines)

        canned.key, canned.calls = "TEST", 0
        lines = RC.stage_lines(rows + [{"foo": 1}], "selftest_stage", by_uid=by_uid, write_log=False)
        ok_fmt = all(ln.startswith("JEV-ROWCHECK | selftest_stage | ") for ln in lines)
        gate("A11 line format `JEV-ROWCHECK | <stage> | <row> | <class> p=<p>` + a TOTAL",
             len(lines) == 5 and ok_fmt and " p=0.93" in lines[0] and "TOTAL" in lines[-1], lines[0])
        gate("A12 the unparseable row reads `unknown`, never `ok`",
             "| unknown " in lines[3] and "ok" not in lines[3].split("|")[3], lines[3])

        canned.err = "HTTP 500 boom"
        res = RC.check_rows([shape_a], by_uid=by_uid)
        gate("A13 an API error is `unknown`, not an exception", res[0]["verdict"] == "unknown", res[0]["err"])
    finally:
        RC.jev = real


# ============================================================ B - #5 inside stagekit
def case_b():
    head("B  #5 in stagekit: 3 fake rows, one firing, before the first mutating call")
    import inspect

    import stagekit as K
    import jev_rowcheck as RC

    src = inspect.getsource(K.Stage._op)
    body = [ln.strip() for ln in src.splitlines() if ln.strip() and not ln.strip().startswith(('"', "#"))]
    first = next((ln for ln in body if not ln.startswith("def ")), "")
    gate("B1 `_op`'s FIRST statement is the row check (so it runs before any mutator)",
         first.startswith("self._rowcheck()"), first[:60])

    s = K.Stage.__new__(K.Stage)          # no __init__: nothing is pinned, no path is touched, no VI is opened
    s.name, s.planned_rows, s._rowcheck_done = "selftest_stage", [], False
    s.facts, s.R = [], {}
    s.deadline_s, s.reserve_s, s.t0 = 600.0, 0.0, time.time()
    rows = [{"row": "R1", "source": {"uid": 23868, "term": 3, "name": "output"},
             "sink": {"uid": 10429, "term": 21, "name": "Tunnel"}},
            {"row": "R2", "src_uid": 111, "src_term": 0, "src_name": "a", "sink_uid": 222,
             "sink_term": 1, "sink_name": "b"},
            {"uid": 333, "i": 2, "name": "c", "source": {"uid": 444, "i": 0, "name": "d"}}]
    K.Stage.plan_rows(s, rows, tag="selftest")
    gate("B2 plan_rows stores the rows without touching `self.rows`",
         len(s.planned_rows) == 3 and s.R.get("planned_rows") == 3)

    real, canned = RC.jev, _Canned(noul=0.91)
    buf, real_out = io.StringIO(), sys.stdout
    try:
        RC.jev = canned
        sys.stdout = buf
        out1 = K.Stage._rowcheck(s)
        calls_after_first = canned.calls
        out2 = K.Stage._rowcheck(s)
    finally:
        RC.jev, sys.stdout = real, real_out
    printed = buf.getvalue()
    gate("B3 one JEV-ROWCHECK line per row (+ TOTAL), printed into the stage log",
         len(out1) == 4 and printed.count("JEV-ROWCHECK | selftest_stage |") == 4, out1[:1])
    gate("B4 the verdicts landed in the stage's JSON record", s.R.get("jev_rowcheck") == out1)
    # These fake uids are in NO measured table, so `check_row` answers `unknown` WITHOUT asking - which is the
    # documented behaviour and, incidentally, the cheap path. What B5 measures is that the SECOND call adds
    # nothing at all: no line, and not one more model call than the first one made.
    gate("B5 it fires ONCE - a second call is silent and costs nothing",
         out2 == [] and canned.calls == calls_after_first,
         (out2, calls_after_first, canned.calls))
    gate("B5b an unmeasured uid is `unknown` without a call", canned.calls == 0 and
         all("unknown" in ln for ln in out1[:3]), canned.calls)

    s2 = K.Stage.__new__(K.Stage)
    s2.name, s2.planned_rows, s2._rowcheck_done, s2.facts, s2.R = "no_rows", [], False, [], {}
    gate("B6 a stage that declared no rows spends nothing", K.Stage._rowcheck(s2) == [])

    s3 = K.Stage.__new__(K.Stage)
    s3.name, s3.planned_rows, s3._rowcheck_done, s3.facts, s3.R = "broken", [{"row": "X"}], False, [], {}
    s3.deadline_s, s3.reserve_s, s3.t0 = 600.0, 0.0, time.time()
    hidden = sys.modules.pop("jev_rowcheck")
    sys.modules["jev_rowcheck"] = None      # an import of None raises ImportError
    try:
        out = K.Stage._rowcheck(s3)
    except Exception as e:                                                         # noqa: BLE001
        out = "RAISED " + type(e).__name__
    finally:
        sys.modules["jev_rowcheck"] = hidden
    gate("B7 an unimportable checker is a line, never an exception", out == [], out)


# ============================================================ C - #7 at cycle close
def case_c():
    head("C  #7 Pre-decided contradictions at cycle close (audit_cycle C8)")
    import audit_cycle as AC
    import jev_contradict as JC

    class Args(object):
        no_jev = False

    tmpdir = tempfile.mkdtemp(prefix="jevwave4_")
    state = os.path.join(tmpdir, "state.json")
    plan = os.path.join(tmpdir, "plan.md")
    with open(plan, "w", encoding="utf-8") as fh:
        fh.write("## Pre-decided\n\n"
                 "1. THE ROTOR SIGN is followed verbatim from the hardware count, sign included.\n"
                 "2. The magnet translation stays inside the envelope banner, never homed.\n"
                 "3. CORRECTION TO 1: the rotor sign is NOT followed; the unsigned command stands.\n")

    real_state, real_jev, real_sys_jev = AC.JEV_CONTRADICT_STATE, JC.jev, sys.modules.get("jev")
    canned = _Canned(noul=0.93)

    def run(args):
        """_jev_contradict over the THREE-item test plan, never the project's real one."""
        return AC._jev_contradict(args, plan_path=plan)

    try:
        # BOTH bindings are replaced: `jev_contradict` bound the module at ITS import, and `_jev_contradict`
        # does its own `import jev` at call time, which reads sys.modules.
        AC.JEV_CONTRADICT_STATE, JC.jev, sys.modules["jev"] = state, canned, canned

        a = Args()
        a.no_jev = True
        gate("C1 --no-jev spends nothing and prints nothing", run(a) == [] and
             canned.calls == 0 and not os.path.exists(state))

        a.no_jev = False
        first = run(a)
        st = json.load(open(state, encoding="utf-8"))
        gate("C2 a FIRST run records a baseline and asks NOTHING",
             first == [] and canned.calls == 0 and sorted(st["seen_ids"]) == ["1", "2", "3"], st.get("n_items"))

        with open(state, "w", encoding="utf-8") as fh:      # pretend item 3 is the one added this cycle
            json.dump({"seen_ids": ["1", "2"], "n_items": 2}, fh)
        hits = run(a)
        gate("C3 only pairs involving the NEW item are asked", 0 < canned.calls <= 2, canned.calls)
        gate("C4 the suspect prints as `JEV-CONTRADICT | <a>↔<b> p=<p>`",
             len(hits) == 1 and "JEV-CONTRADICT |" in hits[0] and "3↔1" in hits[0] and "p=0.93" in hits[0],
             (hits or ["-"])[0][:90])
        st = json.load(open(state, encoding="utf-8"))
        gate("C5 the state file is rewritten and carries every id",
             sorted(st["seen_ids"]) == ["1", "2", "3"] and st["last_suspects"] == 1 and
             not os.path.exists(state + ".tmp"), st.get("last_pairs"))

        canned.calls = 0
        gate("C6 a second run in the same cycle asks nothing (no new item)",
             run(a) == [] and canned.calls == 0, canned.calls)

        canned.key, canned.calls = None, 0
        with open(state, "w", encoding="utf-8") as fh:
            json.dump({"seen_ids": ["1", "2"], "n_items": 2}, fh)
        gate("C7 no key -> one line, no call", run(a) == [] and canned.calls == 0)

        canned.key = "TEST"
        AC.JEV_CONTRADICT_STATE = os.path.join(tmpdir, "nosuchdir", "state.json")
        with open(plan, "a", encoding="utf-8") as fh:
            fh.write("4. A fourth item mentioning the rotor sign and the unsigned command again.\n")
        gate("C8 an unwritable state file is survived, not raised", isinstance(run(a), list))
    finally:
        AC.JEV_CONTRADICT_STATE, JC.jev = real_state, real_jev
        if real_sys_jev is not None:
            sys.modules["jev"] = real_sys_jev
        else:
            sys.modules.pop("jev", None)

    # The audit itself must still exit exactly as it did. THREE runs over the same window: C8 silenced by the
    # env var, C8 silenced by the flag, and C8 LIVE against the project's own plan. The live run costs nothing
    # because tools/bench/jev_contradict_state.json does not exist yet, so it records the baseline and asks no
    # pair - which is also how the first real cycle close will behave.
    off_env = dict(os.environ)
    off_env["JEV_ADVISORY_OFF"] = "1"
    rcs, outs = [], []
    for args, env in ((["--since-hours", "1"], off_env),
                      (["--since-hours", "1", "--no-jev"], off_env),
                      (["--since-hours", "1"], dict(os.environ))):
        r = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "audit_cycle.py")] + args,
                           cwd=ROOT, env=env, capture_output=True, text=True, errors="replace", timeout=420)
        rcs.append(r.returncode)
        outs.append((r.stdout or "") + (r.stderr or ""))
    gate("C9 audit_cycle.py exits identically with C8 off, off, and LIVE", len(set(rcs)) == 1, rcs)
    gate("C10 no run raised", not any("Traceback (most recent call last)" in o for o in outs))
    gate("C11 silenced C8 prints nothing; the live run prints its own C8 line",
         "C8 Pre-decided contradictions" not in outs[0] and "C8 Pre-decided contradictions" not in outs[1]
         and "C8 Pre-decided contradictions" in outs[2],
         [ln.strip() for ln in outs[2].splitlines() if "C8 Pre-decided" in ln][:1])
    gate("C12 C8 never appears in `AUDIT VIOLATIONS:`",
         all("C8" not in ln for o in outs for ln in o.splitlines() if ln.startswith("AUDIT VIOLATIONS")),
         [ln for ln in outs[2].splitlines() if ln.startswith("AUDIT ")][:1])
    gate("C13 the live run left a baseline state file",
         os.path.exists(real_state) or "no key" in outs[2], os.path.basename(real_state))


# ============================================================ D - #2 at the failed-prediction gate
def case_d():
    head("D  #2 gate-row verdicts beside the failed-prediction block (guard_peer)")
    import guard_peer as GP
    import jev_gaterow as GR
    import jev_gaterow_q as GQ

    tmpdir = tempfile.mkdtemp(prefix="jevwave4d_")
    log = os.path.join(tmpdir, "fake_build.log")
    with open(log, "w", encoding="utf-8") as fh:
        fh.write("BGRUN START 2026-09-23 04:00:00 limit 20.0 min: py -u tools/recipes/stage_fake_v2.py\n"
                 "---------- [1] the bed\n"
                 "  PASS  K1 the ORIGINAL md5 pin holds\n"
                 "  FAIL  D7 #637 terminals 48 -> 47  observed=47 expected=48\n"
                 "  FAIL  W1 ExecState after the move  observed=0 expected=1\n"
                 "BGRUN END rc=1 after 140s\n")
    rows = GQ.fail_rows(log)
    gate("D1 the two FAIL rows of a fake failing run are found",
         len(rows) == 2 and [r["label"] for r in rows] == ["D7", "W1"], [r["label"] for r in rows])

    real_v, real_state = GR.verdicts_for, GP.GATEROW_STATE
    real_gatelog = os.path.join(GP.BENCH, "jev_gate.log")
    calls = {"n": 0}

    def fake_verdicts_for(path, **kw):
        calls["n"] += 1
        return "D7: prediction-error (p=0.88) | FAIL D7 #637 terminals 48 -> 47\nW1: defect (p=0.81) | FAIL W1"

    try:
        GR.verdicts_for = fake_verdicts_for
        GP.GATEROW_STATE = os.path.join(tmpdir, "gaterow_state.json")
        before = os.path.getsize(real_gatelog) if os.path.exists(real_gatelog) else 0
        err = io.StringIO()
        real_err = sys.stderr
        try:
            sys.stderr = err
            first = GP.gaterow_advisory(log)
            second = GP.gaterow_advisory(log)
        finally:
            sys.stderr = real_err
        gate("D2 one JEV-GATEROW line per failing row, on stderr",
             len(first) == 2 and all(ln.startswith("JEV-GATEROW | fake_build.log | ") for ln in first) and
             "JEV-GATEROW" in err.getvalue(), (first or ["-"])[0][:80])
        gate("D3 the classes reach the line verbatim",
             "prediction-error (p=0.88)" in first[0] and "defect (p=0.81)" in first[1])
        gate("D4 rate-limited to ONE reading per log revision", second == [] and calls["n"] == 1, calls["n"])
        after = os.path.getsize(real_gatelog) if os.path.exists(real_gatelog) else 0
        gate("D5 the lines were appended to tools/bench/jev_gate.log", after > before, (before, after))
        st = json.load(open(GP.GATEROW_STATE, encoding="utf-8"))
        gate("D6 the state file names the log revision and is written atomically",
             len(st.get("seen") or {}) == 1 and "fake_build.log|" in list(st["seen"])[0] and
             not os.path.exists(GP.GATEROW_STATE + ".tmp"), list(st["seen"])[0])

        with open(log, "a", encoding="utf-8") as fh:        # a NEW revision of the same log is read again
            fh.write("  FAIL  X9 another run\n")
        GP.gaterow_advisory(log)
        gate("D7 a changed log is a new revision and is read again", calls["n"] == 2, calls["n"])

        def boom(path, **kw):
            raise RuntimeError("no network")

        GR.verdicts_for = boom
        GP.GATEROW_STATE = os.path.join(tmpdir, "state2.json")
        gate("D8 an exception inside the reading is swallowed", GP.gaterow_advisory(log) == [])

        GR.verdicts_for = fake_verdicts_for
        GP.GATEROW_STATE = os.path.join(tmpdir, "state3.json")
        os.environ["JEV_ADVISORY_OFF"] = "1"
        calls["n"] = 0
        off = GP.gaterow_advisory(log)
        os.environ.pop("JEV_ADVISORY_OFF", None)
        gate("D9 JEV_ADVISORY_OFF=1 silences it", off == [] and calls["n"] == 0)
    finally:
        GR.verdicts_for, GP.GATEROW_STATE = real_v, real_state

    src = open(os.path.join(ROOT, "tools", "hooks", "guard_peer.py"), encoding="utf-8").read()
    i_call = src.find("gaterow_advisory(path)\n\n    first =")
    i_allow = src.find("if allow:\n        return 0")
    gate("D10 it is called only AFTER the allow path has returned - never a discharge basis",
         i_call > 0 and i_allow > 0 and i_call > i_allow, (i_allow, i_call))
    gate("D11 `gaterow_advisory`'s value is discarded by the gate",
         "    gaterow_advisory(path)" in src and "= gaterow_advisory" not in src)


def main():
    print("=" * 100)
    print("jev_wave4_selftest - #5 rowcheck in stagekit, #7 contradict at audit close, #2 gaterow at the "
          "failed-prediction gate")
    print("=" * 100, flush=True)
    t0 = time.time()
    for fn in (case_a, case_b, case_c, case_d):
        try:
            fn()
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            print(traceback.format_exc()[-1800:], flush=True)
            gate("{0} completed without an unhandled exception".format(fn.__name__), False, str(e)[:120])
    print("\n" + "=" * 100)
    print("=== GATES: {0} pass / {1} fail   ({2:.0f} s)".format(P, F, time.time() - t0), flush=True)
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
