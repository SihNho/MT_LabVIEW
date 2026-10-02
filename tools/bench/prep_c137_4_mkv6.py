"""Card 137-4 (offline, no LabVIEW): plan_ring_p4_v6.json = plan_ring_p4_v5.json minus the two RLE actions
p4_rle_x_fd / p4_rle_x_dt; stagesim replay of v6 on graph_ring_p3b2b_20261002_133824.json; stagexec.compile_plan on v5
as-is and on v6.

Prior art checked: tools/bench/prep_c137_p3_mkv5.py (v5 maker: json.dump indent=1, meta step walk - copied here);
stagesim.simulate (tools/stagesim.py:2264) and stagexec.compile_plan (tools/stagexec.py:639) used unchanged.

Prediction contract:
  - v5 has 167 actions; v6 has 165; every remaining action identical to v5; top-level keys unchanged.
  - step counts (v3 meta cut) v6 {1:33, 2:35, 3:41, 4:36, 5:20}.
  - stagesim on v6 passes step 104 (was p4_rle_x_fd on v5); last step / stop reported as measured (no prediction on
    whether it completes).
  - compile_plan(v5) stops at the p4_t_fd tunnel (inner wire is 3 actions after the tunnel, stagexec.py:678-685);
    compile_plan(v6) passes that tunnel group (prediction for the rest: unknown, reported).
"""
import copy, hashlib, json, os, sys, traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
V5 = os.path.join(B, "plan_ring_p4_v5.json")
V6 = os.path.join(B, "plan_ring_p4_v6.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
SIMDIR = os.path.join(B, "sim", "ring_p4_v6")
DROP = ["p4_rle_x_fd", "p4_rle_x_dt"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    gates = {"pass": 0, "fail": 0}
    ff = [None]

    def gate(ok, label):
        gates["pass" if ok else "fail"] += 1
        if not ok and ff[0] is None:
            ff[0] = label
        print("GATE {0} | {1}".format("PASS" if ok else "FAIL", label))

    print("v5 md5", md5(V5), "graph md5", md5(GRAPH))
    v5 = json.load(open(V5, encoding="utf-8"))
    A5 = v5["actions"]
    ids5 = [a.get("id") for a in A5]
    for d in DROP:
        i = ids5.index(d)
        print("DROP v5 #{0} {1}: {2}".format(i + 1, d, json.dumps(A5[i])[:200]))
    A6 = [copy.deepcopy(a) for a in A5 if a.get("id") not in DROP]
    v6 = copy.deepcopy(v5)
    v6["actions"] = A6
    with open(V6, "w", encoding="utf-8") as f:
        json.dump(v6, f, indent=1, default=str)
    print("v5 actions", len(A5), "v6 actions", len(A6), "v6 md5", md5(V6))
    gate(len(A6) == len(A5) - 2, "v6 = v5 - 2 actions")
    rest5 = [a for a in A5 if a.get("id") not in DROP]
    gate(rest5 == A6, "every remaining action identical to v5")
    top = sorted(k for k in set(v5) | set(v6) if k != "actions" and v5.get(k) != v6.get(k))
    gate(not top, "no top-level key changed ({0})".format(top))
    v6r = json.load(open(V6, encoding="utf-8"))
    gate(v6r["actions"] == A6, "v6 re-read equals built")

    meta = json.load(open(META, encoding="utf-8"))
    stepof = {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "step" in o and "unit" in o:
                stepof[o["id"]] = o["step"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(meta)
    for x, t, w in (("p4_x_fd", "p4_t_fd", "p4_w_fd_in"), ("p4_x_dt", "p4_t_dt", "p4_w_dt_in")):
        stepof[t] = stepof[w] = stepof.get(x)
    cnt = {}
    nometa = []
    for a in A6:
        s = stepof.get(a.get("id"))
        if s is None:
            nometa.append(a.get("id"))
            continue
        cnt[s] = cnt.get(s, 0) + 1
    print("v6 step counts", dict(sorted(cnt.items())), "no meta step", nometa)
    gate(cnt.get(3) == 41, "v6 step 3 == 41")

    # stagesim replay
    import stagesim as SS
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V6, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:  # report, no retry
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    if S is not None:
        print("SIM SUMMARY final={0} failed={1} end_cdiff_rows={2} first_divergent={3} candidates={4} plan_out={5}".format(
            S.get("final"), S.get("failed"), S.get("end_cdiff_rows"), S.get("first_divergent"), S.get("n_candidates"),
            S.get("plan_out")))
        gate(bool(S.get("final")), "stagesim v6 final")

    # compile_plan
    import stagexec as SX

    def comp(tag, plan):
        try:
            ops = SX.compile_plan(plan)
        except SX.ExecStop as e:
            print("COMPILE {0} STOP: {1}".format(tag, e))
            return None
        per = {}
        for o in ops:
            s = stepof.get(plan["actions"][o["acts"][0] - 1].get("id"))
            per[s] = per.get(s, 0) + 1
        print("COMPILE {0} OK ops={1} per meta step {2}".format(tag, len(ops), dict(sorted(per.items(), key=str))))
        return ops
    comp("v5", v5)
    o6 = comp("v6", v6)
    gate(o6 is not None, "compile_plan(v6) compiles")
    if S is not None and S.get("plan_out"):
        po = S["plan_out"]["path"] if isinstance(S["plan_out"], dict) else S["plan_out"]
        comp("v6-sim-rewritten", json.load(open(po, encoding="utf-8")))

    print(protocol.result_line(protocol.make_result(gates["pass"], gates["fail"], ff[0],
                                                    [{"path": "tools/bench/plan_ring_p4_v6.json", "md5": md5(V6)}])))


if __name__ == "__main__":
    main()
