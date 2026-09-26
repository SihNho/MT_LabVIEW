r"""diag_c101_op4 - card 101-3, after stage_d1_disp_r4.log:90 (op 4 move_in #8775: STEP-DIFF dangling_sim_only [8753]).
Pure Python, no LabVIEW, READ-ONLY: the simulated effect of plan action 4 and the rows of wire(s) touching #8775 / #8753
in step_03 vs step_04, the owner class of #8775, and stagesim's only-sink fate for that class. Facts only.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c101_op4.log -- py -u tools/bench/diag_c101_op4.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                               # noqa: E402
import stagesim as SS                                                              # noqa: E402
PL = json.load(open(os.path.join(HERE, "sim", "disp", "plan_disp.json"), encoding="utf-8"))
sf = dict((f["n"], f["path"]) for f in PL["finalized"]["step_files"])
s3 = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), sf[3]), encoding="utf-8"))
s4 = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), sf[4]), encoding="utf-8"))
print("  FACT action 4: {0}".format(PL["actions"][3]), flush=True)
print("  FACT step_04 effect: {0}".format(json.dumps(s4.get("effect"), default=str)[:1500]), flush=True)
for tag, st in (("step_03", s3["state"]), ("step_04", s4["state"])):
    ws = set(r["wire_uid"] for r in st["terminals"] if (r["owner_uid"] == 8775 or r["term_uid"] == 8753) and r["wire_uid"])
    for w in sorted(ws):
        print("  FACT {0} wire {1}: {2}".format(tag, w, [(r["term_uid"], r["owner_uid"], r["owner_class"], r["term_name"],
                                                          r["is_source"], r["frame_diagram"]) for r in st["terminals"]
                                                         if r["wire_uid"] == w]), flush=True)
    print("  FACT {0} #8753 rows: {1}".format(tag, [(r["wire_uid"], r["frame_diagram"]) for r in st["terminals"] if r["term_uid"] == 8753]), flush=True)
cls = sorted(set(r["owner_class"] for r in s3["state"]["terminals"] if r["owner_uid"] == 8775))
print("  FACT #8775 class {0}; only_sink_fate {1}; move_in params {2}".format(
    cls, [SS.only_sink_fate(dict(SS.PROVISIONAL["move_in"]["params"]), c) for c in cls], SS.PROVISIONAL["move_in"]["params"]), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
