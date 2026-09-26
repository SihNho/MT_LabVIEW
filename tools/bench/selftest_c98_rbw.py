r"""selftest_c98_rbw - card 98-3 (PD208(c)(d)): SELF-TEST of gscript.move_into_frame's NEW contract (ExecState-1
precondition + VI-level Remove Bad Wires after the move + gates) IN THE STAGE'S OWN PATH, on the never-saved Moving-Objects
work copy of S1 (a scratch: nothing is saved, S1 md5 3e3d23ce gated). A NEW file because selftest_c98_stage.py (98-2) tested
the termless-deletion contract and must keep matching its log. Same shape: stage_d1_fgate.body imported UNCHANGED, the verb
wrapped:
  call 1 (case A), in order:
    SAN  NEGATIVE: real verb, _skip_rbw=True, expect_broken False -> MUST raise MoveIntoFrameBroken (98-1/98-2: move A
         leaves 8 termless wires + loose ends), termless_left non-empty, ExecState 0
    SAP  PRECONDITION: the verb called again on that ExecState-0 state -> MUST raise MoveIntoFrameRefused BEFORE any edit
         (Wire and Node counts unchanged)
    SAF  finish = move_into_frame_finish(e.result, expect_broken as the stage passes = True): Remove Bad Wires ran, removed
         uids all pre-existing, no data edge lost (across RBW, and non-member since the move), 0 termless, edges equal
    -> the stage then sets Use Default and gates F4e = ExecState 1 after move A
  call 2 (case B) = the real verb exactly as the stage calls it (strict): SB ExecState 1 in-verb, RBW fields clean
E3: SE3 ExecState 1 + 0 termless. The stage then runs its read-only F5 gates (census, owners, F5d, cdiff F5c); at the tag
'warm, before save' SH20 = 20 calls of the post-move reader bundle (remove_bad_wires_scripted + read_terms + all_wire_uids
+ exec_state) with handles flat +-100, no wire removed, ExecState 1 each; then STOP - nothing is saved.
PREDICTION: every S* gate and F4e PASS; RBW after A removes the 98-1 orphans (8 uids, 98-2 saw [7931 9407 15847 24106 28139
28443 28509 33062]) and nothing new; after B about 1 (98-1: 10908); F5c cdiff 0 rows.
FOUND FIRST: selftest_c98_stage.py (wrapper shape), diag_c98_fgate.py, allterms, gscript.remove_bad_wires_scripted
(OpRemoveBadWires_v0 = VI method 410; no per-diagram method: archive/peer/2026-09-26-c98-rbw-scope.md). No new op.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/selftest_c98_rbw.log -- py -u tools/bench/selftest_c98_rbw.py"""
import os, subprocess, sys, time                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path[:0] = [TOOLS, os.path.join(TOOLS, "recipes")]  # noqa: E702
import stagekit as K, gscript as g, stage_d1_fgate as F                                         # noqa: E401,E402
PLAN = "plans/plan_fgate_97.json"; P, DRY, W = F.P, F.DRY, g.MOVE_DST                             # noqa: E702
REAL = g.move_into_frame
Done = type("Done", (Exception,), {})
ST = {}


def H():
    return K.mod("bench_prep").labview_handles()


def clean(r):
    return (r["rbw_ran"] and not r["rbw_new_uid_removed"] and not r["rbw_appeared"] and not r["lost_edges"]
            and not r["lost_nonmember_since_move"] and not r["termless_left"] and not r["missing"] and not r["extra"])


def show(r):
    return {"removed": r["rbw_removed"], "new_uid_removed": r["rbw_new_uid_removed"], "appeared": r["rbw_appeared"],
            "lost_rbw": len(r["lost_edges"]), "lost_since_move": len(r["lost_nonmember_since_move"]),
            "termless_left": r["termless_left"], "missing": r["missing"], "extra": r["extra"],
            "es": (r.get("exec_state_before"), r["exec_state"])}


def wrapped(target, frame, members, spot=(0, 0), log=None, expect_broken=False):
    s = ST["s"]; n = s.R.setdefault("mif_calls", 0); s.R["mif_calls"] = n + 1                     # noqa: E702
    if DRY:
        return REAL(target, frame, members, spot, log, expect_broken)
    if n == 0:
        e = None
        try:
            REAL(target, frame, members, spot, log, False, _skip_rbw=True)
        except g.MoveIntoFrameBroken as x:
            e = x
        s.gate("SAN case A NEGATIVE: Remove Bad Wires skipped + expect_broken False -> MoveIntoFrameBroken raised", e is not None, str(e)[:300], fatal=True)
        r = e.result; s.fact("SAN message: {0}".format(str(e)[:400])); s.R["negative_A"] = show(r)  # noqa: E702
        s.gate("SAN the move alone leaves termless wire(s) {0} and ExecState {1} (want 0)".format(r["termless_left"], r["exec_state"]),
               bool(r["termless_left"]) and r["exec_state"] == 0 and not r["rbw_ran"], show(r))
        wc, nc, ref = g.count(target, "Wire"), g.count(target, "Node"), None
        try:
            REAL(target, frame, members, spot, log, False)
        except (g.MoveIntoFrameRefused, ValueError) as x:
            ref = x
        wc2, nc2 = g.count(target, "Wire"), g.count(target, "Node")
        s.gate("SAP PRECONDITION on that ExecState-0 state -> MoveIntoFrameRefused before any edit (Wire {0}->{1}, Node {2}->{3})".format(wc, wc2, nc, nc2),
               isinstance(ref, g.MoveIntoFrameRefused) and "ExecState" in str(ref) and (wc, nc) == (wc2, nc2), "{0}: {1}".format(type(ref).__name__, str(ref)[:300]), fatal=True)
        r = g.move_into_frame_finish(target, frame, r, log, expect_broken); s.R["finish_A"] = show(r)   # noqa: E702
        s.gate("SAF case A finish (expect_broken {0}): RBW removed {1}, all pre-existing, no data edge lost, 0 termless, edges equal; ExecState {2} (0 by design until Use Default)".format(
            expect_broken, r["rbw_removed"], r["exec_state"]), clean(r) and bool(r["rbw_removed"]), show(r), fatal=True)
        return r
    r = REAL(target, frame, members, spot, log, expect_broken); s.R["strict_B"] = show(r)           # noqa: E702
    s.gate("SB case B (strict, as the stage calls it): ExecState {0} -> {1} in-verb, RBW removed {2}, all pre-existing, no data edge lost, 0 termless, edges equal".format(
        r["exec_state_before"], r["exec_state"], r["rbw_removed"]), r["exec_state_before"] == 1 and r["exec_state"] == 1 and clean(r), show(r))
    return r


class Sf(K.Stage):
    def es(self, tag, target=None):
        v = K.Stage.es(self, tag, target)
        if tag == "E3" and not DRY:
            h = g.wire_health(W)
            self.gate("SE3 E3 ExecState 1 and 0 termless wires (wires {0})".format(len(h["wires"])), v == 1 and h["exec_state"] == 1 and not h["termless"], (v, h["termless"]))
        if tag == "warm, before save":
            _x = DRY or self.h20()                                                                  # noqa: F841
            raise Done()
        return v

    def h20(self):
        AT = K.mod("allterms"); h1, m1, n0, es, t0 = H(), (K.private_bytes() or 0) / 1e6, g.count(W, "Wire"), [], time.time()   # noqa: E702
        for _k in range(20):
            g.remove_bad_wires_scripted(W); AT.read_terms(W); AT.all_wire_uids(W); es.append(g.exec_state(W))   # noqa: E702
            if (K.private_bytes() or 0) / 1e6 > P["memstop_mb"] - 10:
                self.fact("SH20 stopped after {0} calls: private MB above {1}".format(len(es), P["memstop_mb"] - 10)); break   # noqa: E702
        h2, m2, n1 = H(), (K.private_bytes() or 0) / 1e6, g.count(W, "Wire")
        self.fact("SH20 {0} calls in {1:.0f} s; handles {2} -> {3}; private MB {4:.1f} -> {5:.1f}; Wire {6} -> {7}; ExecState {8}".format(
            len(es), time.time() - t0, h1, h2, m1, m2, n0, n1, sorted(set(es))))
        self.R["h20"] = {"calls": len(es), "handles": [h1, h2], "mb": [round(m1, 1), round(m2, 1)], "wires": [n0, n1], "es": es}
        self.gate("SH20 20 calls of the post-move reader bundle: handles flat +-100, no wire removed, ExecState 1 each",
                  len(es) == 20 and abs(h2 - h1) <= 100 and n1 == n0 and set(es) == {1}, (h1, h2, n0, n1, sorted(set(es))))

    def close(self, expect_files=None):
        return K.Stage.close(self, [])


def body(s):
    s.gate("P0 {0} is the plan stage_d1_fgate.body reads".format(PLAN), F.P == F.J(K.BENCH, PLAN), fatal=True)
    ST["s"] = s; g.move_into_frame = wrapped                                                        # noqa: E702
    try:
        F.body(s); s.gate("warm-before-save stop reached", False)                                   # noqa: E702
    except Done:
        s.fact("STOPPED at 'warm, before save' by design (card 98-3 self-test): nothing saved")


if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()                                              # noqa: E702
    st = Sf(os.path.join(K.CLAUDEDEV, P["input"]["vi"]), P["input"]["md5"], "selftest_c98_rbw", preload=False, deadline_min=40,
            work_dir=os.path.dirname(W), work_name=os.path.basename(W), task="card 98-3 self-test", out_json=os.path.join(K.BENCH, "selftest_c98_rbw.json"))
    rc = K.run(body, st)
    if not DRY:
        K.mod("bench_prep").restart_labview(); g.reset(); g.restore_move_fixtures()                   # noqa: E702
        st.gate("FX Moving-Objects fixtures restored", K.fixtures_check((st.input_md5,), FXL))
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, timeout=60); time.sleep(4.0)   # noqa: E702
        st.gate("K9 S1 md5 unchanged", K.md5(st.input_vi) == st.input_md5, K.md5(st.input_vi))
        st.gate("LabVIEW gone at exit", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
        st.dump(); rc = st.summary()                                                                  # noqa: E702
    sys.exit(rc)
