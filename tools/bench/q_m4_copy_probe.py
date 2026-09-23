r"""q_m4_copy_probe - cycle 68 MATERIAL diagnostic, the discriminating test prior-art `archive/peer/2026-09-24-priorart-
c68-m4a.md` B2 names as its release: does the bed load at ExecState 1 FROM THE MOVE_DST PATH, and does copy_in (OpMoveByIndex
duplicate) + move_in into loop body #23058 work on the bed's bytes? NOTHING IS SAVED; fixtures restored after a restart.
Existing tools reused: stagekit.Stage (work_dir = the Moving-Objects folder), Stage.copy_in (cycle-68 creator row).
PREDICTION CONTRACT (facts first, each gate states what could falsify it):
  D1 ExecState at MOVE_DST, no preload = RECORDED (item (h) predicts 0 via ~94 unresolved subVI paths; 1 refutes it).
  D2 copy_in(Function #10382 Not) -> exactly one new Function uid, UID guard == #10382 (else the copier is unusable here).
  D3 after move_in the copy's owner is Diagram #23058 (A2's D2+D4 combination measured directly).
  D4 ExecState after the copy = RECORDED (an unwired Not is expected to break the VI: 0 does not indict the copier).
  D5 bed md5 + pins unchanged; files left in claudeDev == [].
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a4_20260923_185345.vi")
BED_MD5 = "fdd6d74ac8a5ba0c1a545ad89ff2996f"


def main(s):
    s.start()
    es0 = s.es("D1 bed opened FROM MOVE_DST, no preload")
    s.row("D1 ExecState at MOVE_DST (item (h) predicts 0)", es0, "recorded")
    shutil.copyfile(BED, g.MOVE_SRC)
    s.gate("K4 MOVE_SRC holds the bed's bytes", K.md5(g.MOVE_SRC) == BED_MD5, K.md5(g.MOVE_SRC), fatal=True)
    f0 = s.count("Function")
    new = s.copy_in("Function", 10382, 23058, (4760, 2960), "D2")
    s.gate("D2 copy_in -> one new Function (UID guard held)", bool(new) and s.count("Function") == f0 + 1,
           "new #{0}; Function {1} -> {2}".format(new, f0, s.count("Function")))
    oc, ou = K.mod("build_d1_v0").owner_of(s.work, new, strict=True)
    s.gate("D3 after move_in the copy is owned by Diagram #23058", ou == 23058, "{0}#{1}".format(oc, ou))
    _l, rows = s.wired_terminals(new, tag="copied Not")
    s.fact("copied Not terminals: {0!r}".format([(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows]))
    s.row("D4 ExecState after copy+move (unwired Not)", s.es("D4 after copy + move_in"), "recorded")
    s.gate("D5 bed md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))


if __name__ == "__main__":
    g.restore_move_fixtures()
    st = K.Stage(BED, BED_MD5, "q_m4_copy_probe", preload=False, deadline_min=15, reserve_s=200,
                 work_dir=os.path.dirname(g.MOVE_DST), work_name=os.path.basename(g.MOVE_DST),
                 pins=tuple(K.DEFAULT_PINS) + (("M3a-4 bed", BED, BED_MD5),),
                 task="cycle 68: bed ExecState at MOVE_DST + copy_in/move_in of Not into #23058 (prior-art B2)")
    st.close = lambda expect_files=None, c=st.close: c([])   # the work is the fixture, not a claudeDev file (run 1 H6)
    rc = K.run(main, st)
    K.mod("bench_prep").restart_labview()
    g.reset()
    g.restore_move_fixtures()
    print("  FACT  Moving-Objects fixtures restored after a restart", flush=True)
    sys.exit(rc)
