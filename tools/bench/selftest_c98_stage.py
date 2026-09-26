r"""selftest_c98_stage - card 98-2 (PD207(d)): SELF-TEST of the patched gscript.move_into_frame IN THE STAGE'S OWN PATH, on the
never-saved Moving-Objects work copy of S1 (a scratch: nothing is saved, S1 md5 3e3d23ce gated). Why this shape: the
gscript-level self-test selftest_c98_move.py stopped at its own setup (E1 ExecState 0 with 0 termless wires, selectors fed
by #11639 instead of the stage's upd chain, selftest_c98_move.log:17) - so the setup is taken from the stage that reached
E1 = 1 twice (fgate_97_stage2.log, diag_c98_fgate.log:288): stage_d1_fgate.body is imported UNCHANGED (diag_c98_fgate.py
pattern) and g.move_into_frame is wrapped:
  call 1 (case A) = the real patched verb (expect_broken=True as the stage passes it): >=1 orphan deleted, 0 termless left
  call 2 (case B) = NEGATIVE: real verb with _keep_orphans=1, expect_broken False -> MUST raise MoveIntoFrameBroken
          (98-1: B leaves 1 orphan); then the kept wire is deleted by uid -> wire_health: ExecState 1, 0 termless; the
          stage then continues with the cleaned result.
Stops at E3 (before any save): E3 ExecState 1 + 0 termless; 20 wire_health calls handles flat +-100.
FOUND FIRST: diag_c98_fgate.py (Dg subclass, Done at E3), allterms, gscript.delete_object('Wire'), no new op.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/selftest_c98_stage.log -- py -u tools/bench/selftest_c98_stage.py"""
import os, subprocess, sys, time                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path[:0] = [TOOLS, os.path.join(TOOLS, "recipes")]  # noqa: E702
import stagekit as K, gscript as g, stage_d1_fgate as F                                         # noqa: E401,E402
PLAN = "plans/plan_fgate_97.json"; P, DRY, W = F.P, F.DRY, g.MOVE_DST                             # noqa: E702
REAL = g.move_into_frame
Done = type("Done", (Exception,), {})
ST = {}


def H():
    return K.mod("bench_prep").labview_handles()


def wrapped(target, frame, members, spot=(0, 0), log=None, expect_broken=False):
    s = ST["s"]; n = s.R.setdefault("mif_calls", 0); s.R["mif_calls"] = n + 1                     # noqa: E702
    if DRY:
        return REAL(target, frame, members, spot, log, expect_broken)
    if n == 0:
        r = REAL(target, frame, members, spot, log, expect_broken)
        s.gate("SA case A: >=1 orphan deleted by uid (98-1: 8), 0 termless left, no other wire gone (ExecState {0}, expect_broken {1})".format(
            r["exec_state"], expect_broken), len(r["orphans_deleted"]) >= 1 and not r["termless_left"] and not r["wires_gone_unexpectedly"],
            (r["orphans_deleted"], r["orphan_owners"], r["termless_left"], r["wires_gone_unexpectedly"]))
        return r
    e = None
    try:
        REAL(target, frame, members, spot, log, False, _keep_orphans=1)
    except g.MoveIntoFrameBroken as x:
        e = x
    s.gate("SBN case B NEGATIVE: kept orphan + expect_broken False -> MoveIntoFrameBroken raised", e is not None, str(e)[:300], fatal=True)
    r = e.result; s.fact("SBN message: {0}".format(str(e)[:400])); s.R["negative_B"] = dict((k, v) for k, v in r.items() if k != "ops")  # noqa: E702
    s.gate("SBN termless_left == the kept orphan {0}, no other wire gone".format(r["orphans_kept"]),
           len(r["orphans_kept"]) == 1 and r["termless_left"] == r["orphans_kept"] and not r["wires_gone_unexpectedly"], r["termless_left"])
    for w in r["orphans_kept"]:
        g.delete_object(target, "Wire", [o["uid"] for o in g.report_all(target, "Wire")].index(w), verify=False)
    h = g.wire_health(target)
    s.gate("SBF kept orphan deleted by uid -> ExecState 1, 0 termless (wires {0})".format(len(h["wires"])), h["exec_state"] == 1 and not h["termless"], (h["exec_state"], h["termless"]))
    return dict(r, termless_left=[w for w in r["termless_left"] if w in h["termless"]], exec_state=h["exec_state"])


class Sf(K.Stage):
    def es(self, tag, target=None):
        v = K.Stage.es(self, tag, target)
        if tag == "E3" and not DRY:
            h = g.wire_health(W)
            self.gate("SE3 E3 ExecState 1 and 0 termless wires (wires {0})".format(len(h["wires"])), v == 1 and h["exec_state"] == 1 and not h["termless"], (v, h["termless"]))
            h1 = H(); [g.wire_health(W) for _k in range(20)]; h2 = H()                            # noqa: E702
            self.gate("SH20 20 wire_health calls: handles flat +-100", abs(h2 - h1) <= 100, (h1, h2))
        if tag == "E3":
            raise Done()
        return v

    def close(self, expect_files=None):
        return K.Stage.close(self, [])


def body(s):
    s.gate("P0 {0} is the plan stage_d1_fgate.body reads".format(PLAN), F.P == F.J(K.BENCH, PLAN), fatal=True)
    ST["s"] = s; g.move_into_frame = wrapped                                                        # noqa: E702
    try:
        F.body(s); s.gate("E3 stop reached", False)                                                 # noqa: E702
    except Done:
        s.fact("STOPPED AT E3 by design (card 98-2 self-test): nothing saved")


if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()                                              # noqa: E702
    st = Sf(os.path.join(K.CLAUDEDEV, P["input"]["vi"]), P["input"]["md5"], "selftest_c98_stage", preload=False, deadline_min=40,
            work_dir=os.path.dirname(W), work_name=os.path.basename(W), task="card 98-2 self-test", out_json=os.path.join(K.BENCH, "selftest_c98_stage.json"))
    rc = K.run(body, st)
    if not DRY:
        K.mod("bench_prep").restart_labview(); g.reset(); g.restore_move_fixtures()                   # noqa: E702
        st.gate("FX Moving-Objects fixtures restored", K.fixtures_check((st.input_md5,), FXL))
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, timeout=60); time.sleep(4.0)   # noqa: E702
        st.gate("K9 S1 md5 unchanged", K.md5(st.input_vi) == st.input_md5, K.md5(st.input_vi))
        st.gate("LabVIEW gone at exit", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
        st.dump(); rc = st.summary()                                                                  # noqa: E702
    sys.exit(rc)
