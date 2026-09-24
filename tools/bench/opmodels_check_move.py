r"""opmodels_check_move - card chat-S1 pass line "a written check that the move model reproduces the cut set L7-1a actually
observed". PURE PYTHON, no LabVIEW. Inputs: tools/bench/opmodels/bed_s3_loop15.json (the L7-1a INPUT, read on a scratch in
opmodels_read_bed.log), tools/bench/opmodels/bed_l7_1a.json (the saved L7-1a ARTEFACT 34aaadf1, opmodels_read_map.log), and
tools/bench/stage_d1_l7_1a.json (the uid-edge diff L7-1a printed itself, stage_d1_l7_1a.log:125 PD3).
Model: opmodels_lib.apply_move (R1 cut every wire end of the moved node, wires survive as half-wires; R2 a LoopTunnel fed only
by the moved node loses its direction). The 4 SR objects L7-1a ALSO added are excluded from the comparison (their own model is
add_shift_reg's).
PREDICTION: G1 predicted removed edges == observed (terminal dump) == the 16 of stage_d1_l7_1a.json, as (src_term, sink_term);
G2 no edge added; G3 predicted half-wires == observed half-wires (12); G4 predicted direction flips == observed ({2043, 5050});
G5 Wire object count unchanged (1913). Names are NOT compared (not modelled).
    MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/opmodels_check_move.log -- py -u tools/bench/opmodels_check_move.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import opmodels_lib as L, protocol as P                                            # noqa: E401,E402

J = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))            # noqa: E731
S3, A7, ST = J("opmodels/bed_s3_loop15.json"), J("opmodels/bed_l7_1a.json"), J("stage_d1_l7_1a.json")
SR_ADDED = {24083, 24133, 24150, 24187}
passes, fails = [], []


def gate(label, ok, detail=""):
    (passes if ok else fails).append(label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


print(__doc__)
pred, dead = L.apply_move(S3["terms"], 376)
obs = [r for r in A7["terms"] if r["owner_uid"] not in SR_ADDED]
EB, _w, _h = L.edges(S3["terms"])
EP, _w, HP = L.edges(pred)
EO, _w, HO = L.edges(obs)
rm_p, rm_o = sorted(set(EB) - set(EP)), sorted(set(EB) - set(EO))
fact = [x for x in ST["facts"] if "edges removed (16)" in x][0]
rm_s = sorted((int(t[2]), int(t[4])) for t in eval(fact.split("removed (16) ", 1)[1]))   # noqa: S307 - our own log line
print("  FACT  predicted removed {0}\n  FACT  observed  removed {1}\n  FACT  stage-log removed {2}".format(rm_p, rm_o, rm_s))
gate("G1 predicted cut set == terminal-dump cut set == stage_d1_l7_1a's 16 (src_term, sink_term)",
     rm_p == rm_o == rm_s and len(rm_p) == 16, {"pred-obs": sorted(set(rm_p) ^ set(rm_o)), "obs-stage": sorted(set(rm_o) ^ set(rm_s))})
gate("G2 no edge added (predicted and observed)", not (set(EP) - set(EB)) and not (set(EO) - set(EB)),
     (sorted(set(EP) - set(EB)), sorted(set(EO) - set(EB))))
gate("G3 predicted half-wires == observed half-wires", HP == HO, {"pred": HP, "obs": HO})
TB = dict((r["term_uid"], r) for r in S3["terms"])
fl_p = sorted(r["term_uid"] for r in pred if r["is_source"] != TB[r["term_uid"]]["is_source"])
fl_o = sorted(r["term_uid"] for r in obs if r["term_uid"] in TB and r["is_source"] != TB[r["term_uid"]]["is_source"])
gate("G4 predicted direction flips == observed", fl_p == fl_o, {"pred": fl_p, "obs": fl_o, "dead_tunnels": dead})
wb = sum(1 for o in S3["objs"] if o["class"] == "Wire")
wa = sum(1 for o in A7["objs"] if o["class"] == "Wire")
gate("G5 Wire object count unchanged by the move (wires survive as half-wires)", wb == wa, (wb, wa))
print("=== GATES: {0} pass / {1} fail".format(len(passes), len(fails)))
print(P.result_line(P.make_result(len(passes), len(fails), fails[0] if fails else None, [])))
sys.exit(1 if fails else 0)
