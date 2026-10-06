# ---
# labview: build
# hardware: none
# ---
"""fntest_lib - the shared recorder of card chat-F3's real-LabVIEW function tests (tools/bench/fntest_g*.py).

EXISTING FIRST (checked): tools/fn_records.py owns the registry (plans, add_record, source_md5, status); tools/fncontract.py
records ONE standard outcome for every wrapped gscript call (HISTORY via _record) and stagekit.Stage._op stores the verb's
outcome in stage.R["ops"]; stagexec.LVBackend is the executor's verb layer. Nothing here re-implements any of them: the
recorder only OBSERVES - it taps fncontract._record (so no outcome is lost to HISTORY's 2000-entry ring), groups the
stagekit/stagexec verb cases a runner declares, and at the end writes ONE record per function through fn_records.add_record.

STATUS RULE (stated in every record's `rule`):
  gscript.<fn>  PASS = called >= 1 time on the scratch AND every recorded outcome 'ok' (calls inside a declared NEGATIVE
                window are judged by that window's own prediction instead); FAIL = any other outcome (counts + first reason).
  stagekit.op:<verb> / recipes.<fn>  PASS = every declared case ran without an exception, every op the case issued ended
                outcome 'ok' with err '', and the case's own measured check held; FAIL = the case's numbers.
  A function no case reached gets NO record (it is listed as not-run, never as FAIL). A harness error (an exception raised
  before the function under test was called) is reported as HARNESS and records nothing for that case.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "recipes"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fncontract as FC                                                            # noqa: E402
import fn_records as R                                                             # noqa: E402

CARD = "chat-F3"
RUNS = os.path.join(R.REG_DIR, "runs")


class FT(object):
    def __init__(self, s, runner):
        self.s, self.runner = s, runner
        self.calls, self.neg, self.cases, self.harness = [], [], {}, []
        self._in_neg = None
        orig = FC._record

        def tap(oc):
            orig(oc)
            self.calls.append((self._in_neg, oc))
        FC._record = tap

    # ------------------------------------------------------------------ cases
    def _run(self, fn):
        n0 = len(self.s.R["ops"])
        try:
            res, err = fn(), None
        except Exception as e:                                                     # noqa: BLE001
            res, err = None, "{0}: {1}".format(type(e).__name__, str(e)[:300])
        ops = self.s.R["ops"][n0:]
        return res, err, [(o["verb"], o["outcome"]["outcome"], str(o.get("err") or "")[:200]) for o in ops]

    def case(self, fns, name, fn, check=None):
        """Run one POSITIVE case for the verb-level functions `fns`; check(res) -> (ok, measured dict)."""
        res, err, ops = self._run(fn)
        ok = err is None and all(o[1] == "ok" and not o[2] for o in ops)
        meas = {"err": err, "ops": ops}
        if ok and check:
            try:
                c_ok, c_m = check(res)
            except Exception as e:                                                 # noqa: BLE001
                c_ok, c_m = False, {"check_exc": "{0}: {1}".format(type(e).__name__, str(e)[:200])}
            ok, meas["check"] = bool(c_ok), c_m
        for f in fns:
            self.cases.setdefault(f, []).append({"case": name, "ok": ok, "measured": meas})
        self.s.fact("FNCASE {0} | {1} | {2} | {3}".format(name, "PASS" if ok else "FAIL", ",".join(fns),
                                                         json.dumps(meas, default=str)[:600]))
        return res if ok else None

    def negcase(self, fns, name, fn, expect):
        """A NEGATIVE case (the plan's neg-double): expect(err, ops) -> (ok, measured). gscript outcomes inside it are
        judged by this prediction, not by the 'every outcome ok' rule."""
        self._in_neg = name
        try:
            res, err, ops = self._run(fn)
        finally:
            self._in_neg = None
        ok, m = expect(err, ops)
        m = dict(m, err=err, ops=ops)
        self.neg.append({"case": name, "ok": ok, "fns": fns})
        for f in fns:
            self.cases.setdefault(f, []).append({"case": name, "ok": bool(ok), "measured": m, "negative": True})
        self.s.fact("FNCASE {0} | NEG {1} | {2} | {3}".format(name, "PASS" if ok else "FAIL", ",".join(fns),
                                                             json.dumps(m, default=str)[:600]))
        return res

    def harness_err(self, name, e):
        self.harness.append({"case": name, "err": str(e)[:300]})
        self.s.fact("FNCASE {0} | HARNESS (no record) | {1}".format(name, str(e)[:300]))

    # ------------------------------------------------------------------ the records
    def verdicts(self):
        plan = set(R.plan_set())
        out = {}
        g = {}
        for neg, oc in self.calls:
            if neg is None and oc.get("fn") in plan:
                g.setdefault(oc["fn"], []).append(oc)
        for fn, ocs in g.items():
            bad = [o for o in ocs if o["outcome"] != "ok"]
            cnt = {}
            for o in ocs:
                cnt[o["outcome"]] = cnt.get(o["outcome"], 0) + 1
            out[fn] = {"status": "FAIL" if bad else "PASS", "measured": {"calls": len(ocs), "outcomes": cnt,
                       "first_bad": (bad[0].get("reason") if bad else None)}}
        for fn, cs in self.cases.items():
            if fn not in plan:
                continue
            fail = [c for c in cs if not c["ok"]]
            v = out.get(fn) if fn.startswith("gscript.") else None
            st = "FAIL" if fail or (v and v["status"] == "FAIL") else "PASS"
            m = dict((v or {}).get("measured") or {}, cases=[{"case": c["case"], "ok": c["ok"], "neg": bool(c.get("negative")),
                                                             "measured": c["measured"]} for c in cs])
            out[fn] = {"status": st, "measured": m}
        return out

    def commit(self, log, labview):
        os.makedirs(RUNS, exist_ok=True)
        v = self.verdicts()
        det = os.path.join(RUNS, "{0}_{1}.json".format(self.runner, self.s.stamp))
        json.dump({"runner": self.runner, "card": CARD, "log": R.rel(log), "labview": labview, "verdicts": v,
                   "harness": self.harness, "t": time.strftime("%Y-%m-%d %H:%M:%S")}, open(det, "w", encoding="utf-8"),
                  indent=1, default=str)
        rule = __doc__.split("STATUS RULE (stated in every record's `rule`):")[1].split('"""')[0].strip()[:900]
        for fn, x in sorted(v.items()):
            R.add_record(fn, x["status"], log, labview=labview, card=CARD)
            rec = R.load(fn)
            last = rec["records"][-1]
            last.update(runner=self.runner, detail=R.rel(det), rule=rule, measured=_short(x["measured"]))
            R.write_record(rec)
        n = dict((k, sum(1 for x in v.values() if x["status"] == k)) for k in ("PASS", "FAIL"))
        self.s.fact("FNRECORDS written: {0} PASS {1} FAIL {2} (detail {3})".format(len(v), n["PASS"], n["FAIL"], R.rel(det)))
        for fn, x in sorted(v.items()):
            self.s.fact("FNREC {0} {1} {2}".format(x["status"], fn, json.dumps(_short(x["measured"]), default=str)[:300]))
        return v


def _short(m):
    s = json.dumps(m, default=lambda o: sorted(o, key=str) if isinstance(o, (set, frozenset)) else str(o))
    return json.loads(s) if len(s) <= 1500 else {"truncated": s[:1500]}


def owners_of(objs):
    """str(diagram uid) -> [owner class, owner uid] from a read_live objs list (the Executor's PD185 owners map shape)."""
    cls = dict((o["uid"], o["class"]) for o in objs)
    return dict((str(o["uid"]), [cls.get(int(o["owner"] or 0), ""), int(o["owner"] or 0)]) for o in objs
                if o["class"] == "Diagram" and int(o["owner"] or 0) in cls)


def term(real, owner, name=None, src=None, cls=None):
    """THE one terminal row of node #owner with that name / direction / term class (harness lookup; raises if not one)."""
    r = [x for x in real if int(x["owner_uid"]) == int(owner) and (name is None or x["term_name"] == name)
         and (src is None or bool(x["is_source"]) == src) and (cls is None or x["term_class"] == cls)]
    if len(r) != 1:
        raise LookupError("term #{0} {1!r} src={2} cls={3}: {4} rows {5}".format(
            owner, name, src, cls, len(r), [(x["term_uid"], x["term_name"], x["is_source"], x["term_class"]) for x in r][:6]))
    return r[0]
