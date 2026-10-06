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
    def __init__(self, s, runner, card=CARD):
        self.s, self.runner, self.card = s, runner, card
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
        json.dump({"runner": self.runner, "card": self.card, "log": R.rel(log), "labview": labview, "verdicts": v,
                   "harness": self.harness, "t": time.strftime("%Y-%m-%d %H:%M:%S")}, open(det, "w", encoding="utf-8"),
                  indent=1, default=str)
        rule = __doc__.split("STATUS RULE (stated in every record's `rule`):")[1].split('"""')[0].strip()[:900]
        for fn, x in sorted(v.items()):
            R.add_record(fn, x["status"], log, labview=labview, card=self.card)
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


class Bed(object):
    """card chat-F3b: the live graph of a fntest scratch through stagexec.LVBackend, read the way the Executor reads it
    between ops (stagexec.py:2224-2317): read() = the whole-VI read (LVBackend.read) + the owners map (PD185 shape) + the
    register-face retrack (Addr.retrack). The lookups below are HARNESS lookups: a miss returns None and is printed as a
    LOOKUP fact, so the runner records the dependent case as HARNESS (no record), never as a function FAIL."""

    def __init__(self, s, be):
        self.s, self.be, self.real = s, be, []

    def read(self):
        self.real = self.be.read()
        self.be.addr.owners = owners_of(self.be.last_objs)
        lost = self.be.addr.retrack()
        if lost:
            self.s.fact("RETRACK lost register faces {0}".format(lost))
        return self.real

    def ts(self, owner, name=None, src=None, cls=None):
        """THE one terminal uid of node #owner with that name / direction / term class, else None."""
        if owner is None:
            return None
        try:
            return int(term(self.real, owner, name, src, cls)["term_uid"])
        except LookupError as e:
            self.s.fact("LOOKUP {0}".format(str(e)[:300]))
            return None

    def ct(self, label):
        """The ControlTerminal (front-panel terminal on a diagram) labelled `label`: its own uid (== term uid), else None."""
        r = [x for x in self.real if x.get("term_class") == "ControlTerminal" and x["term_name"] == label]
        if len(r) != 1:
            self.s.fact("LOOKUP ControlTerminal {0!r}: {1} rows".format(label, len(r)))
            return None
        return int(r[0]["term_uid"])

    def wire_of(self, term_uid):
        r = [x for x in self.real if term_uid is not None and int(x["term_uid"]) == int(term_uid)]
        return int(r[0]["wire_uid"] or 0) if len(r) == 1 else None

    def cls_of(self, uid):
        return dict((int(o["uid"]), o["class"]) for o in self.be.last_objs).get(int(uid)) if uid is not None else None

    def wired_after(self, *terms):
        """(ok, measured) after a fresh read: every terminal in `terms` carries a wire."""
        self.read()
        w = dict((t, self.wire_of(t)) for t in terms)
        return all(w.values()), {"wires": w}


class Kit(object):
    """card chat-F3b: the case builders of a fntest runner, every verb called with the stagexec Executor's call shapes
    (LVBackend.create / connect, stagexec.py:2377-2485). need() turns a missing input into a HARNESS line (no record);
    mk() = one create row (the class census +1 when `cls` is given, the returned uid when `uid`); con() = one connect row
    (both ends wired on the re-read). `LO` = the loop_of map (register uid -> loop uid) the connect routes read."""

    def __init__(self, T, B, be, W, g):
        self.T, self.B, self.be, self.W, self.g, self.LO = T, B, be, W, g, {}

    def need(self, name, *v):
        return all(x is not None for x in v) or self.T.harness_err(name, "an input was not created / not found: {0}".format(v))

    def cnt(self, c):
        return self.g.count(self.W, c)

    def mk(self, fns, name, route, a, args, cls=None, uid=True):
        if not self.need(name, *args.values()):
            return None
        c0 = self.cnt(cls) if cls else None
        return self.T.case(fns, name, lambda: self.be.create(route, dict(a, id=name), args, list(self.B.real), {}),
                           lambda o: ((not cls or self.cnt(cls) - c0 == 1) and (not uid or bool(o.get("uid"))),
                                      {"out": dict((k, o.get(k)) for k in ("uid", "body", "frames", "how")),
                                       "census": cls and (c0, self.cnt(cls))}))

    def prim(self, name, dg, donor, p, pos, cls_=None):
        a = dict({"prim": p, "donor": donor}, **({"class": cls_} if cls_ else {}))
        r = self.mk(["stagekit.op:create_primitive_nested"], name, "primitive", a, {"diagram": dg, "pos": pos})
        return int(r["uid"]) if r else None

    def con(self, fns, name, src, dst, op=None):
        return self.need(name, src, dst) and self.T.case(
            fns, name, lambda: self.be.connect(src, dst, list(self.B.real), self.LO, op or {}),
            lambda o: self.B.wired_after(src, dst))

    def add_sr(self, name, loop, parent):
        """The Executor's add_sr sequence (stagexec.py:2228-2316): snap the loop's Terminals[] (on its parent diagram), add
        the register, read the pair back (shift_reg / shift_reg_left index 0 - the loop's first and only register), bind
        loop_of, track the two outer faces. Returns ((right, left), right outer term, left outer term) or Nones."""
        s, g, W, be = self.T.s, self.g, self.W, self.be
        if not self.need(name, loop) or s.safe("snap_loop", lambda: be.addr.snap_loop(loop, parent))[1]:
            return None, None, None

        def _sr():
            be.add_sr(loop, 120, {})
            li = s.uid_index("WhileLoop", loop)
            return int(g.shift_reg(W, li, 0)["uid"]), int(g.shift_reg_left(W, li, 0)["left"]["uid"])
        sr = self.T.case(["stagekit.op:add_shift_reg"], name, _sr,
                         lambda r: (r[0] > 0 and r[1] > 0, {"right": r[0], "left": r[1]}))
        if not sr:
            return None, None, None
        self.LO.update({sr[0]: loop, sr[1]: loop})
        self.B.read()
        ro, lo = self.B.ts(sr[0], None, None, "OuterTerminal"), self.B.ts(sr[1], None, None, "OuterTerminal")
        s.fact("SR TRACK {0}".format(s.safe("track_new", lambda: be.addr.track_new(loop, ro, lo)) if ro and lo
                                     else "faces not found"))
        return sr, ro, lo

    def r0(self):
        """R0: count / report_all / uids / exec_state agree on the EMPTY scratch (one Diagram). Returns that Diagram's uid."""
        g, W = self.g, self.W
        self.T.case(["gscript.count", "gscript.report_all", "gscript.uids", "gscript.exec_state"], "R0 empty bed reads agree",
                    lambda: (self.cnt("Diagram"), g.report_all(W, "Diagram"), sorted(int(u) for u in g.uids(W, "Diagram")),
                             g.exec_state(W)),
                    lambda r: (r[0] == len(r[1]) == len(r[2]) == 1 and sorted(int(x["uid"]) for x in r[1]) == r[2] and
                               r[3] == 1, {"count": r[0], "report_all": len(r[1]), "uids": r[2], "exec_state": r[3]}))
        return int(g.report_all(W, "Diagram")[0]["uid"])

    def r1(self):
        """R1: the node / terminal / panel / wire reads on the built bed (Diagram[0] and [1], node 0)."""
        g, W = self.g, self.W
        return self.T.case(["gscript.node_labels", "gscript.node_terms_uid", "gscript.node_terms", "gscript.panel_wiring",
                            "gscript.wire_health"], "R1 reads on the built bed",
                           lambda: ([(g.node_labels(W, i), g.node_terms_uid(W, i, 0), g.node_terms(W, i, 0)) for i in range(2)],
                                    g.panel_wiring(W), g.exec_state(W), g.wire_health(W)),
                           lambda r: (all(len(a) >= 1 for a, _b, _c in r[0]) and len(r[1]) >= 1,
                                      {"panel": sorted(x["label"] for x in r[1]), "es": r[2], "wire_health": str(r[3])[:200]}))


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
