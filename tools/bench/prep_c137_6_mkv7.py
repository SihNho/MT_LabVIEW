"""Card 137-6 (offline, no LabVIEW): plan_ring_p4_v7.json = plan_ring_p4_v6.json with the placeholder
`decide p4_dec_reseed` (v6 #158) replaced by PD300(b) option 2 (PD308(a)):
  Select(valid = AND1, t = #9647 'x .and. y?' t9668 raw, f = Local read of 'autofocus reseed flag (1.2 to 1.1)')
  -> indicator terminal t25557; Tunnel #10465 (t10469) stays on the raw #9647 output (computation unchanged).
8 actions, as the decide's own count: delete w25415, re-wire #10465 raw, Select, Local read, t, f, s, out.
Then stagesim replay of v7 on graph_ring_p3b2b_20261002_133824.json and stagexec.compile_plan(v7).

Prior art checked: tools/bench/prep_c137_4_mkv6.py (v6 maker: meta step walk, simulate/compile calls - copied);
the action shapes are copied from v6's rollback groups A (#115-124: delete_wire, raw restore, Select, t/f/s/out) and
D (#145: Select out -> indicator terminal {uid=term_uid}); Local read shape from v6 #4 p4_lr_stop12 (on 23166).
stagesim.simulate (tools/stagesim.py:2264) and stagexec.compile_plan (tools/stagexec.py:639) used unchanged.

Prediction contract:
  - v7 has 165 - 1 + 8 = 172 actions; v7 minus the 8 new = v6 minus the decide (list equality); top-level keys unchanged.
  - new 'as' names RB7 / LRR1 unused in v6.
  - graph: #10465 is a Tunnel whose outer t10469 is on w25415; its inner terminals on Case #10445's frames are reported.
  - stagesim on v7: the 8 new actions replay ok; the stop moves to p4_x_n2_out (v7 #171, FS exit) as in v6 (#164).
  - compile_plan(v7): passes action 158 (no decide left); its result (ops or stop) reported as measured.
"""
import copy, hashlib, json, os, sys, traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
V6 = os.path.join(B, "plan_ring_p4_v6.json")
V7 = os.path.join(B, "plan_ring_p4_v7.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
SIMDIR = os.path.join(B, "sim", "ring_p4_v7")
DEC = "p4_dec_reseed"
FLAG = "autofocus reseed flag (1.2 to 1.1)"
SEL_TERMS = [{"name": "s? t:f", "is_source": True, "term_class": "ParameterTerminal"},
             {"name": "f", "is_source": False, "term_class": "ParameterTerminal"},
             {"name": "s", "is_source": False, "term_class": "ParameterTerminal"},
             {"name": "t", "is_source": False, "term_class": "ParameterTerminal"}]
DONOR = {"donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorErrSel_MergeErrors.vi",
         "uid": 529}
W = "PD300(b)/PD308(a) reseed flag t25557 (from #9647 'x .and. y?' t9668, w25415; not a register)"
NEW = [
    {"op": "delete_wire", "id": "p4_rbR_dw", "wire_uid": 25415,
     "why": "ROUTE delete_wire | MEASURED | " + W + ": detach w25415 (sinks t25557 + Tunnel #10465 t10469; no single-sink "
            "disconnect op exists); delete_wire route launched P2a (as v6 p4_rbA_dw)"},
    {"op": "wire", "id": "p4_rbR_re0", "src": {"uid": 9647, "term_uid": 9668}, "dst": {"uid": 10465, "term_uid": 10469},
     "why": "ROUTE connect | PRECEDENT | " + W + ": restore Tunnel #10465 t10469 RAW (PD308(a): computation unchanged; "
            "as v6 p4_rbA_re0)"},
    {"op": "create", "id": "p4_rbR_sel", "class": "Function", "diagram": 23166, "as": "RB7", "prim": "Select",
     "donor": DONOR, "terminals": SEL_TERMS,
     "why": "ROUTE create primitive | MEASURED | " + W + ": Select (vilib donor #529, scalar s; "
            "diag_c128_2_donors.log:61-63, P3b-1 p3b_sel launched)"},
    {"op": "create", "id": "p4_rbR_lr", "class": "Local", "diagram": 23166, "as": "LRR1", "label": FLAG, "mode": "read",
     "terminals": [{"name": FLAG, "is_source": True, "term_class": "Terminal"}],
     "why": "ROUTE local_read | PRECEDENT | " + W + ": f = Local read of the same indicator (keeps last); local_read on "
            "a base While body ran (plan_l2a3_in.json:16, as v6 p4_lr_stop12); 2nd Local of this indicator "
            "(#25576 on 639 exists, graph t25585)"},
    {"op": "wire", "id": "p4_rbR_t", "src": {"uid": 9647, "term_uid": 9668}, "dst": "new:RB7.t",
     "why": "ROUTE connect | PRECEDENT | " + W + ": new (raw #9647) -> Select t (as v6 p4_rbA_t)"},
    {"op": "wire", "id": "p4_rbR_f", "src": "new:LRR1." + FLAG, "dst": "new:RB7.f",
     "why": "ROUTE connect | PRECEDENT | " + W + ": old (Local read) -> Select f (same-diagram connect)"},
    {"op": "wire", "id": "p4_rbR_s", "src": "new:AND1.x .and. y?", "dst": "new:RB7.s",
     "why": "ROUTE connect | PRECEDENT | " + W + ": valid -> Select s (branch, as v6 p4_rbA_s)"},
    {"op": "wire", "id": "p4_rbR_out", "src": "new:RB7.s? t:f", "dst": {"uid": 25557, "term_uid": 25557},
     "why": "ROUTE connect | PRECEDENT | " + W + ": Select -> indicator terminal t25557 (as v6 p4_rbD_sel_t25573)"},
]


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

    print("v6 md5", md5(V6), "graph md5", md5(GRAPH))
    v6 = json.load(open(V6, encoding="utf-8"))
    A6 = v6["actions"]
    ids6 = [a.get("id") for a in A6]
    k = ids6.index(DEC)
    print("DECIDE v6 #{0} {1}".format(k + 1, json.dumps(A6[k])[:160]))
    gate(sum(1 for a in A6 if a.get("op") == "decide") == 1, "exactly one decide in v6")
    used = {a.get("as") for a in A6}
    gate("RB7" not in used and "LRR1" not in used and not (set(n["id"] for n in NEW) & set(ids6)), "new as/ids unused in v6")
    A7 = [copy.deepcopy(a) for a in A6[:k]] + copy.deepcopy(NEW) + [copy.deepcopy(a) for a in A6[k + 1:]]
    v7 = copy.deepcopy(v6)
    v7["actions"] = A7
    with open(V7, "w", encoding="utf-8") as f:
        json.dump(v7, f, indent=1, default=str)
    print("v6 actions", len(A6), "v7 actions", len(A7), "v7 md5", md5(V7))
    for i, a in enumerate(A7[k:k + len(NEW)], k + 1):
        print("NEW v7 #{0} {1} {2}".format(i, a["op"], a["id"]))
    gate(len(A7) == len(A6) - 1 + len(NEW), "v7 = v6 - 1 + 8 actions")
    gate([a for a in A7 if a["id"] not in {n["id"] for n in NEW}] == [a for a in A6 if a["id"] != DEC],
         "every other action identical to v6")
    top = sorted(x for x in set(v6) | set(v7) if x != "actions" and v6.get(x) != v7.get(x))
    gate(not top, "no top-level key changed ({0})".format(top))
    gate(json.load(open(V7, encoding="utf-8"))["actions"] == A7, "v7 re-read equals built")

    # graph facts: #10465 and the flag
    g = json.load(open(GRAPH, encoding="utf-8"))
    O = {o["uid"]: o for o in g["objs"]}
    for r in g["terminals"]:
        if r["owner_uid"] in (10465, 10445, 25557) or r.get("wire_uid") == 25415 or r["term_name"] == FLAG:
            print("GT", json.dumps(r))
    print("OBJ 10445", json.dumps(O.get(10445)), "owners", {x: g["owners"].get(str(x)) for x in (10453, 10459, 10445)})
    sel = [r for r in g["terminals"] if r["owner_uid"] == 10445 or r.get("owner_class") == "CaseSelector" and
           r.get("frame_diagram") == 23166]
    print("CASE10445 own terms", len(sel))
    inner = [r for r in g["terminals"] if r["owner_uid"] == 10465 and r["term_class"] == "InnerTerminal"]
    print("#10465 inner terms", [(r["term_uid"], r["frame_diagram"], r["wire_uid"]) for r in inner])

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
    print("decide meta step", stepof.get(DEC))
    for n in NEW:
        stepof[n["id"]] = stepof.get(DEC)
    cnt, nometa = {}, []
    for a in A7:
        s = stepof.get(a.get("id"))
        if s is None:
            nometa.append(a.get("id"))
            continue
        cnt[s] = cnt.get(s, 0) + 1
    print("v7 step counts", dict(sorted(cnt.items())), "no meta step", nometa)

    import stagesim as SS
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V7, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:  # report, no retry
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    if S is not None:
        print("SIM SUMMARY final={0} failed={1} end_cdiff_rows={2} first_divergent={3} candidates={4} plan_out={5}".format(
            S.get("final"), S.get("failed"), S.get("end_cdiff_rows"), S.get("first_divergent"), S.get("n_candidates"),
            S.get("plan_out")))

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
    comp("v7", v7)
    if S is not None and S.get("plan_out"):
        po = S["plan_out"]["path"] if isinstance(S["plan_out"], dict) else S["plan_out"]
        comp("v7-sim-rewritten", json.load(open(po, encoding="utf-8")))

    print(protocol.result_line(protocol.make_result(gates["pass"], gates["fail"], ff[0],
                                                    [{"path": "tools/bench/plan_ring_p4_v7.json", "md5": md5(V7)}])))


if __name__ == "__main__":
    main()
