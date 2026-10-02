r"""prep_c138_1_replay - card 138-1 pass 3/5 (offline, no LabVIEW): stagexec.compile_plan(v7) per meta step and the stagesim
replay of plan_ring_p4_v7.json (01ab0893, NOT written) on graph_ring_p3b2b_20261002_133824.json (50595c62) with the fixed
simulator (FS-exit row + delete_wire case-tunnel keep). Output under tools/bench/sim/c138_1_v7.
Prior art: tools/bench/prep_c137_6_mkv7.py (meta step walk + simulate/compile calls - copied, v7 maker part dropped).
PREDICTION CONTRACT: inputs' md5 as the card; compile_plan(v7) OK, 160 ops, #171 = connect_term_uid fs_exit; the replay passes
step 159 (p4_rbR_re0) and step 171 (p4_x_n2_out, how fs_exit); last step / cdiff / first stop or END reported as measured.
"""
import hashlib
import json
import os
import sys
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                        # noqa: E402
import stagesim as SS                                                  # noqa: E402
import stagexec as SX                                                  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
V7 = os.path.join(B, "plan_ring_p4_v7.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
SIMDIR = os.path.join(B, "sim", "c138_1_v7")
WANT = {V7: "01ab0893f3a9440e02bbc180bc467bdf", GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
DEC = "p4_dec_reseed"
NEW = ["p4_rbR_dw", "p4_rbR_re0", "p4_rbR_sel", "p4_rbR_lr", "p4_rbR_t", "p4_rbR_f", "p4_rbR_s", "p4_rbR_out"]
G = {"pass": 0, "fail": 0, "first": None}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(ok, label, detail=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]))


def main():
    for p, w in WANT.items():
        gate(md5(p) == w, "input md5 " + os.path.basename(p), md5(p))
    v7 = json.load(open(V7, encoding="utf-8"))
    A = v7["actions"]
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
    for n in NEW:
        stepof[n] = stepof.get(DEC)
    cnt = {}
    for a in A:
        cnt[stepof.get(a.get("id"))] = cnt.get(stepof.get(a.get("id")), 0) + 1
    print("ACTIONS per meta step", dict(sorted(cnt.items(), key=str)), "total", len(A))
    try:
        ops = SX.compile_plan(v7)
        per, kinds = {}, {}
        for o in ops:
            s = stepof.get(A[o["acts"][0] - 1].get("id"))
            per[s] = per.get(s, 0) + 1
            kinds[o["kind"] + ("/" + o["variant"] if o.get("variant") else "")] = kinds.get(o["kind"] + (
                "/" + o["variant"] if o.get("variant") else ""), 0) + 1
        n171 = [o for o in ops if 171 in o["acts"]]
        print("COMPILE v7 OK ops={0} per meta step {1}".format(len(ops), dict(sorted(per.items(), key=str))))
        print("COMPILE kinds", dict(sorted(kinds.items())))
        print("COMPILE #171", n171)
        gate(len(n171) == 1 and n171[0]["kind"] == "connect_term_uid" and n171[0].get("variant") == "fs_exit",
             "compile v7 #171 p4_x_n2_out = connect_term_uid fs_exit", n171)
    except SX.ExecStop as e:
        gate(False, "compile_plan(v7)", e)
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V7, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:                                             # report, no retry
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    gate(md5(V7) == WANT[V7], "v7 not written by the replay", md5(V7))
    if S is None:
        gate(False, "simulate returned")
    else:
        keys = sorted(k for k in S if not isinstance(S[k], (list, dict)) or k in ("plan_out",))
        print("SIM SUMMARY", dict((k, S.get(k)) for k in keys))
        steps = S.get("steps") or []
        print("SIM steps recorded", len(steps))
        for s in steps:
            if s.get("n") in (158, 159, 165, 166, 167, 168, 169, 170, 171, 172) or s.get("error"):
                print("STEP", s.get("n"), s.get("op"), s.get("id"), "error" if s.get("error") else "ok",
                      str(s.get("error") or s.get("effect_summary"))[:500], "cdiff", s.get("cdiff_rows", s.get("cdiff")))
        last = steps[-1] if steps else {}
        print("SIM LAST", last.get("n"), last.get("id"), "error", last.get("error"))
        e159 = next((s for s in steps if s.get("n") == 159), {})
        e171 = next((s for s in steps if s.get("n") == 171), {})
        gate(e159 and not e159.get("error"), "replay step 159 p4_rbR_re0 ok", e159.get("error"))
        gate(e171 and not e171.get("error") and (e171.get("effect_summary") or {}).get("how") == "fs_exit",
             "replay step 171 p4_x_n2_out ok, how fs_exit", e171.get("error") or e171.get("effect_summary"))
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                    [{"path": "tools/bench/plan_ring_p4_v7.json", "md5": md5(V7)}])))
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
