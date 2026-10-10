# ---
# labview: none
# hardware: none
# evidence: tools/stagekit.py:1821-2032
# ---
"""prep_c161_b1_2_measure - card 161-b1-2 (OFFLINE, no LabVIEW, no edits): why gate PB of the p5s02b dry
(tools/bench/prep_c161_b1_1_dry.log:55) counts 31 rows when the pred has 26 and the plan 24 open pairs.
Existing functions CALLED (none copied, docs/script-writing.md): stagekit.s1_frame_graph / pred_end_graph / pb_check /
pb_check_bound / case_move_frames / pos_convert_open_rows, stagexec.bind_state, vigraph.computation_diff_frame /
computation_diff / key_parts, stagesim.load_s1 / graph / cdiff_inputs (the pred's own cdiff route, stagesim.py:2629-2690).
Found before writing: diag_c158_a2_3_measure.py (same PB recompute on p5s02a data; its inputs differ, so called-not-copied here).
Inputs: plan_ring_p5s02b.json f4520b10 (finalized step files), pred 18729409, the dry's bindings from prep_c161_b1_1_dry.log:24-41.
G1 is approximated by the sim end re-keyed by the bindings (Gsimb): the dry logged eq_diff [] between them (:55).
PREDICTION: frame-keyed cdiff(S1f, sim end) has 31 sinks, the pred's 26 (= stagesim's NON-frame computation_diff end rows) is a
subset, and the 5 extra sinks are the 5 logged pairs on #376; the old-checkpoint question is independent of PB's inputs."""
import os, sys, json, glob                                                                 # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                       # noqa: E402
import protocol                                                                            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
V, SX, SS, JC = K.pure("vigraph"), K.pure("stagexec"), K.pure("stagesim"), K.pure("jev_candidates")
P = K.jload(os.path.join(B, "plan_ring_p5s02b.json"))
PRED = K.jload(os.path.join(B, "plan_ring_p5s02b_pred.json"))
BASE = K.jload(ROOT, P["finalized"]["base"]["path"])
LAB, FS = JC.node_labels_default(), BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
FLAT = {-1: 10000003, -7: 10000008, -12: 10000014, -19: 10000020, -24: 10000026}   # dry log bound {...} lines (obj binds)
FIVE = ["376|Terminal|cal cluster path|0", "376|Terminal|error in|0", "376|Terminal|file size|0",
        "376|Terminal|selected path|0", "376|Terminal|total data array in|0"]
out, fails = {}, []


def say(k, v):
    out[k] = v
    print("FACT", k, json.dumps(v, default=str)[:1800], flush=True)


steps = sorted(glob.glob(os.path.join(B, "sim", "ring_p5s02b", "step_*.json")))
say("step_files", [os.path.basename(p) for p in steps])
say("last_step_md5_vs_plan", [K.md5(steps[-1]), P["finalized"]["last_step"]["md5"]])
S1f = K.s1_frame_graph(LAB)
S1n = SS.load_s1(P)
pred_rows = list(PRED["cdiff_rows"])
say("pred_rows_n", len(pred_rows))
say("pred_rows_eq_plan_end_cdiff_rows", sorted(pred_rows) == sorted(P["finalized"]["end_cdiff_rows"]))
first_seen, per_step = {}, []
for p in steps:
    rec = K.jload(p)
    st = rec["state"]
    G = K.pred_end_graph(st, LAB, FS)
    cf = sorted(set(r["sink"] for r in V.computation_diff_frame(S1f, G)["rows"]))
    lab, fs, _r = SS.cdiff_inputs(P, st, None)
    cn = sorted(set(r["sink"] for r in V.computation_diff(S1n, SS.graph(st, lab, fs))["rows"]))
    n = rec.get("n")
    per_step.append([n, (rec.get("action") or {}).get("id"), len(cf), len(cn), [s for s in FIVE if s in cf]])
    for s in FIVE:
        if s in cf and s not in first_seen:
            first_seen[s] = [n, (rec.get("action") or {}).get("id")]
    last = (st, G, cf, cn)
say("per_step [n, action id, frame-cdiff rows, nonframe-cdiff rows, FIVE present]", per_step)
say("FIVE first step present in frame cdiff", first_seen)
L, Gpred, cf, cn = last
say("end frame cdiff n", len(cf))
say("end nonframe cdiff n (stagesim route)", len(cn))
say("nonframe == pred rows", sorted(cn) == sorted(pred_rows))
say("rows only in frame cdiff (31 side)", sorted(set(cf) - set(pred_rows)))
say("rows only in pred (26 side)", sorted(set(pred_rows) - set(cf)))
cdf = dict((r["sink"], r) for r in V.computation_diff_frame(S1f, Gpred)["rows"])
for s in FIVE:
    say("row " + s, {"before": cdf.get(s, {}).get("before"), "after": cdf.get(s, {}).get("after")})
# PB recompute (G1 := Gsimb, which the dry logged eq_diff [] against)
Lb, unbound = SX.bind_state(L, {"obj": FLAT, "term": {}, "diag": {}})
Gsimb = K.pred_end_graph(Lb, LAB, FS)
mf = K.case_move_frames(P, L, FLAT)
r = K.pb_check_bound(S1f, Gsimb, Gpred, Gsimb, pred_rows, P["open_rows"], mf, (), V)    # (S1f, G1, Gpred, Gsimb, ...)
o = r["old"]
say("PB n_rows", r["n_rows"])
say("PB pred_rows/slots_want/slots_got", [o["pred_rows"], o["slots_want"], o["slots_got"]])
say("PB extra_sinks", o["extra_sinks"])
say("PB missing_sinks", o["missing_sinks"])
say("PB pairs_want/pairs_got", [o["pairs_want"], o["pairs_got"]])
say("PB open pairs (converted) n", len(o["open_rows"]))
say("PB pairs_extra_left", r["pairs_extra_left"])
say("PB blocked whys", [[b["sink"], b["why"]] for b in r["blocked"]])
say("PB move_frames", dict((k, sorted(v)) for k, v in mf.items()))
say("PB unbound", sorted(unbound)[:10])
# plan actions touching the five (node 376, term) and the S1 / base presence
acts = [[k, a.get("id"), a["op"]] for k, a in enumerate(P["actions"], 1)
        if isinstance(a.get("dst"), dict) and a["dst"].get("uid") == 376 and any(("|" + a["dst"].get("term", "") + "|") in s for s in FIVE)]
say("actions with dst #376 on a FIVE term", acts)
say("FIVE in S1f rows (sink key exists)", dict((s, s in S1f["rows"]) for s in FIVE))
# doubled source uids: the sink's wire(s) at the sim end and whether the 3 deleted wires survive
T = L["terminals"]
for nm in ("error in", "total data array in"):
    rows = [t for t in T if int(t.get("owner_uid") or 0) == 376 and t.get("term_name") == nm]
    say("L #376 '{0}' terminal rows [term uid, wire uid]".format(nm), [[t.get("term_uid"), t.get("wire_uid")] for t in rows])
dw = [a["wire_uid"] for a in P["actions"] if a["op"] == "delete_wire"]
say("deleted wire uids still on a terminal at sim end", sorted(set(int(t.get("wire_uid") or 0) for t in T) & set(dw)))
for s in ("376|Terminal|error in|0", "376|Terminal|total data array in|0"):
    say("effective_sources S1f " + s, sorted(V.effective_sources(S1f, s)) if hasattr(V, "effective_sources") else "n/a")
    say("effective_sources Gpred " + s, sorted(V.effective_sources(Gpred, s)) if hasattr(V, "effective_sources") else "n/a")
chk = {"31": r["n_rows"] == [31, 31], "26": len(pred_rows) == 26, "extra==FIVE": o["extra_sinks"] == FIVE,
       "left==FIVE": [list(x) for x in r["pairs_extra_left"]] == [[int(s.split("|")[0]), s.split("|")[2]] for s in FIVE]}
say("prediction checks", chk)
fails = [k for k, v in chk.items() if not v]
with open(os.path.join(B, "diag_c161_b1_2_measure.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
jp = os.path.join(B, "diag_c161_b1_2_measure.json")
print(protocol.result_line(protocol.make_result(len(chk) - len(fails), len(fails), fails[0] if fails else None,
                                                [{"path": "tools/bench/diag_c161_b1_2_measure.json", "md5": K.md5(jp)}])), flush=True)
