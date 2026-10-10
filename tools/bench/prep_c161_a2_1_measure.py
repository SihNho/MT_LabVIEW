# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c161_b1_2_facts.md
# ---
"""prep_c161_a2_1_measure - card 161-a2-1 steps 1-2 MEASUREMENT before any edit (OFFLINE, no LabVIEW, no stagekit edit).
(1) Walk the adopt chain (adopted_scratch.jsonl, artefact md5 -> input md5) back from p5s02b's base VI; per record: plan md5 now vs
recorded, scratch json, its `stagexec` bound dicts (stagekit.run_bind), and stagekit.case_move_frames(plan, plan's sim end, bindings).
(2) Evaluate PD394(a) (i)(ii)(iii) on the 5 #376 rows of the p5s02b sim end (G1 := Gsimb with the dry's bindings, as 161-b1-2 did).
Functions CALLED (none copied): stagekit.run_bind / case_move_frames / s1_frame_graph / pred_end_graph / pb_bound_rows / frame_tag_map /
frame_src_resolve, stagexec.bind_state, vigraph.computation_diff_frame.
PREDICTION: chain p5s02a <- p5s01b <- p5s01a <- p4...; only p5s02a has case moves (376, 3052, 3453 -> frame 31506); every 5 row meets
(i)(ii)(iii) -> RECORDABLE 5/5. Any row failing = the brief's hand-back."""
import os, sys, json                                                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                       # noqa: E402
import protocol                                                                            # noqa: E402

B = K.BENCH
V, SX, JC = K.pure("vigraph"), K.pure("stagexec"), K.pure("jev_candidates")
P = K.jload(os.path.join(B, "plan_ring_p5s02b.json"))
FIVE = ["376|Terminal|cal cluster path|0", "376|Terminal|error in|0", "376|Terminal|file size|0",
        "376|Terminal|selected path|0", "376|Terminal|total data array in|0"]
FLAT = {-1: 10000003, -7: 10000008, -12: 10000014, -19: 10000020, -24: 10000026}   # dry bindings (prep_c161_b1_2_measure.py:27)
out = {}


def say(k, v):
    out[k] = v
    print("FACT", k, json.dumps(v, default=str)[:2400], flush=True)


say("plan base", P.get("base"))
say("finalized base", P["finalized"].get("base"))
recs = [json.loads(x) for x in open(os.path.join(B, "adopted_scratch.jsonl"), encoding="utf-8") if x.strip()]
by_art = dict((r["artefact"]["md5"], (i + 1, r)) for i, r in enumerate(recs))
base_md5 = None
for v in (P.get("base") or {}, P["finalized"].get("base") or {}):
    if isinstance(v, dict):
        base_md5 = base_md5 or v.get("vi_md5") or v.get("md5_vi")
say("base vi md5 field", base_md5)
cur = base_md5 if base_md5 in by_art else next((m for m in by_art if m.startswith("94ffff94")), None)
inh, chain = {}, []
while cur in by_art:
    ln, r = by_art[cur]
    pp, pm = list(r["plan_md5s"].items())[0]
    pl = K.jload(K.ROOT, pp)
    sj = os.path.join(K.ROOT, r["log"].replace("\\", "/")[:-4] + ".json")
    sx = K.jload(sj).get("stagexec") if os.path.exists(sj) else None
    flat = K.run_bind(report=sx or [])
    se = K.jload(K.ROOT, pl["finalized"]["step_files"][-1]["path"])["state"]
    mf = K.case_move_frames(pl, se, flat)
    moves = [a.get("id") for a in pl["actions"] if a.get("op") == "move_in"]
    chain.append({"line": ln, "plan": pp, "plan_md5_rec": pm[:8], "plan_md5_now": K.md5(os.path.join(K.ROOT, pp))[:8], "json": os.path.relpath(sj, K.ROOT),
                  "json_exists": os.path.exists(sj), "n_bound_ops": len(sx or []), "n_flat": len(flat), "move_in": moves,
                  "move_frames": dict((n, sorted(f)) for n, f in mf.items())})
    for n, fs in mf.items():
        inh.setdefault(n, set()).update(fs)
    cur = r["input"]["md5"]
say("adopt chain (newest first)", chain)
say("inherited frames", dict((n, sorted(f)) for n, f in inh.items()))
say("inherited frames negative (unbound sim uid)", sorted(u for f in inh.values() for u in f if u < 0))
steps = P["finalized"]["step_files"]
L = K.jload(K.ROOT, steps[-1]["path"])["state"]
L0 = K.jload(K.ROOT, steps[0]["path"])["state"]
LAB, FS = JC.node_labels_default(), K.jload(K.ROOT, P["finalized"]["base"]["path"]).get("fs_tunnel_pairs")
S1f = K.s1_frame_graph(LAB)
Lb = SX.bind_state(L, {"obj": FLAT, "term": {}, "diag": {}})[0]
Ge, G0 = K.pred_end_graph(Lb, LAB, FS), K.pred_end_graph(L0, LAB, FS)
cde, cd0 = V.computation_diff_frame(S1f, Ge), V.computation_diff_frame(S1f, G0)
Re, R0 = K.pb_bound_rows(cde, Ge, V), K.pb_bound_rows(cd0, G0, V)
ye = dict((y["sink"], y) for y in cde["rows"])
fm = K.frame_tag_map(Ge)
tu = lambda G, k: K._iv((G["rows"].get(k) or {}).get("term_uid"))                         # noqa: E731
verdict = {}
for s in FIVE:
    y = ye[s]
    res = [K.frame_src_resolve(x, fm) for x in y["after"]]
    nodes = set([K._iv(s.split("|", 1)[0])]) | set(K._iv(b.split("|", 1)[0]) for b, _t in res)
    allowed = set().union(*[inh.get(n, set()) for n in nodes])
    tags = set(t for _b, ts in res for t in ts)
    su, eu = sorted(tu(S1f, b) for b in y["before"]), sorted(tu(Ge, b) for b, _t in res)
    c1, c2m, c2s = Re.get(s) == R0.get(s), su == eu, sorted(set(su)) == sorted(set(eu))
    c3 = bool(tags) and all(f in allowed for _tn, f in tags)
    verdict[s] = c1 and c2m and c3
    say("row " + s, {"i_base_eq_end": c1, "ii_multiset": c2m, "ii_set": c2s, "iii": c3, "tags": sorted(tags, key=str), "allowed": sorted(allowed),
                     "nodes": sorted(nodes), "S1 uids": su, "end uids": eu, "end bound": sorted(map(str, Re.get(s) or [])),
                     "base bound": sorted(map(str, R0.get(s) or [])), "base after": (dict((z["sink"], z) for z in cd0["rows"]).get(s) or {}).get("after")})
say("frame_tag_map end (tunnels of the 5)", dict((str(k), v) for k, v in fm.items() if k[0] in (31546, 31557, 10000003, 10000008, 10000014, 10000020, 10000026)))
say("RECORDABLE under PD394(a) as written", verdict)
ok = all(verdict.values())
jp = os.path.join(B, "diag_c161_a2_1_measure.json")
with open(jp, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
fails = [s for s, v in verdict.items() if not v]
print(protocol.result_line(protocol.make_result(5 - len(fails), len(fails), ("not recordable: " + ", ".join(fails)) if fails else None,
                                                [{"path": "tools/bench/diag_c161_a2_1_measure.json", "md5": K.md5(jp)}])), flush=True)
