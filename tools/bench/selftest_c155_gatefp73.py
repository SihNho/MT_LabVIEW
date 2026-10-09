# ---
# labview: none
# hardware: none
# ---
r"""selftest_c155_gatefp73 - card 155-a5-1 (fp-73): stage_prerun.vi_modifying_calls / is_vi_modifying no longer call a
script VI-modifying when its ONLY MODIFY_VERBS hit is discard_work (stagekit.Stage.discard_work, tools/stagekit.py:577, marks
the work copy a scratch close() deletes). RingSession.executor (tools/stagekit.py:1968) joined MODIFY_VERBS so the ring
recipes (whose only other hit was discard_work) stay classified. OFFLINE: no LabVIEW, no COM; this file does not import the
Stage library itself - the fixtures are TEMP .py files handed to stage_prerun's own functions.
FOUND FIRST: selftest_prerun_diag.py (D1-D4 fixture pattern), selftest_c121_3_gatefp.py F3/F3b.
PREDICTION (10 gates, 0 fail):
  G1 discard-only fixture -> [] / False          G2 discard_work + save -> True, both verbs listed
  G3 discard_work + plan_rows -> True            G4 discard_work without the library import -> False
  G5 executor + discard_work -> True             G6 RingSession() alone (no executor call) -> False (selftest_t7_ring shape)
  G7 diag_c153_a2_2_queue_hygiene.py -> False    G8 stage_d1_ring_p5s01b.py -> True   G9 stage_d1_ring_p5s02.py -> True
  G10 stage_template_ring.py -> True"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import protocol  # noqa: E402
import stage_prerun as SP  # noqa: E402

RES = {"pass": 0, "fail": 0, "first": None}
TMP = tempfile.mkdtemp(prefix="c155_fp73_")
LIB = "stage" + "kit"            # spelled apart so this file's own ast never holds the import


def gate(label, ok, info=""):
    RES["pass" if ok else "fail"] += 1
    if not ok and RES["first"] is None:
        RES["first"] = label
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, info), flush=True)


def fixture(name, body):
    p = os.path.join(TMP, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


try:
    imp = "import %s as K\n" % LIB
    f1 = fixture("fx_discard_only.py", imp + "s = K.Stage('x')\ns.start()\ns.discard_work()\ns.close()\n")
    gate("G1 discard-only -> [] / False", SP.vi_modifying_calls(f1) == [] and SP.is_vi_modifying(f1) is False,
         SP.vi_modifying_calls(f1))
    f2 = fixture("fx_discard_save.py", imp + "s = K.Stage('x')\ns.discard_work()\ns.save()\n")
    gate("G2 discard_work + save -> True", SP.vi_modifying_calls(f2) == ["discard_work", "save"], SP.vi_modifying_calls(f2))
    f3 = fixture("fx_discard_plan.py", imp + "s = K.Stage('x')\ns.discard_work()\ns.plan_rows([])\n")
    gate("G3 discard_work + plan_rows -> True", SP.is_vi_modifying(f3) is True, SP.vi_modifying_calls(f3))
    f4 = fixture("fx_noimport.py", "s = object()\ns.discard_work()\ns.save()\n")
    gate("G4 no library import -> False", SP.is_vi_modifying(f4) is False, SP.vi_modifying_calls(f4))
    f5 = fixture("fx_executor.py", imp + "RS = K.RingSession('a', 'b', 'c', 'd')\ns = K.Stage('x')\ns.discard_work()\n"
                 "RS.executor(s)\nRS.run(s)\n")
    gate("G5 executor + discard_work -> True", SP.vi_modifying_calls(f5) == ["discard_work", "executor"],
         SP.vi_modifying_calls(f5))
    f6 = fixture("fx_ringsession_only.py", "def t():\n    " + imp + "    rs = K.RingSession('a', 'b', 'c', 'd')\n"
                 "    return rs.NC\n")
    gate("G6 RingSession() without executor -> False", SP.is_vi_modifying(f6) is False, SP.vi_modifying_calls(f6))
    for lab, rel, want in (("G7", "tools/bench/diag_c153_a2_2_queue_hygiene.py", False),
                           ("G8", "tools/recipes/stage_d1_ring_p5s01b.py", True),
                           ("G9", "tools/recipes/stage_d1_ring_p5s02.py", True),
                           ("G10", "tools/recipes/stage_template_ring.py", True)):
        p = os.path.join(os.path.dirname(TOOLS), rel)
        gate("%s %s -> %s" % (lab, os.path.basename(rel), want), os.path.isfile(p) and SP.is_vi_modifying(p) is want,
             SP.vi_modifying_calls(p))
finally:
    shutil.rmtree(TMP, ignore_errors=True)

ok = RES["fail"] == 0
print(protocol.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": RES["pass"], "fail": RES["fail"]},
                            "first_fail": RES["first"]}))
sys.exit(0 if ok else 1)
