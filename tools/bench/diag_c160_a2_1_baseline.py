# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-a2-1.md
# ---
r"""diag_c160_a2_1_baseline - card 160-a2-1 Step 0 (docs/d1/ring-p5b.md PD391(b)(c)), OFFLINE, run BEFORE stagesim/stagexec are edited.
Writes tools/bench/diag_c160_a2_1_baseline.json: (1) the CURRENT stagexec.compile_plan op lists (kind + all args) of plan_ring_p5s01a.json,
plan_ring_p5s01b.json and plan_ring_p5s02b_in.json, each compiled as selftest_c158_runcheck.py:63 does (compile_plan(P): owners from the
plan's own pinned base graph, not a stub); (2) per plan, every tunnel group's OUTSIDE end (the end compile_plan pairs with the tunnel's outer
face, stagexec.py:865) with its base-graph row and whether it is a register inner face; (3) the CURRENT stagesim.op_delete_wire result for
w10394 / w24264 / w24300 / w24285 / w32594 on the 94ffff94 graph (objs presence, rows, effect, termless_wire after). It also keeps byte copies
of the unedited tools as tools/bench/selftest_c160_delwire_stagesim_a3261b56.txt / _stagexec_c4a6e0b6.txt (the pre-edit side of the delwire
and regface self-tests, as card 160-a1-1 kept eb99c6ba / 7a712ccb).
PREDICTION: pins stagesim a3261b56 / stagexec c4a6e0b6 / plans ed62e8d6, 75a77a00, 56bfddd3; the three plans compile (no ExecStop);
p5s02b_in's groups t_go / t_ho have an RSR InnerTerminal outside end and compile to kind 'tunnel'; t_gi / t_hi have an LSR InnerTerminal
(wired source) outside end and compile to 'tunnel'; w24264 / w24300 have one sink row and no source row."""
import copy, hashlib, json, os, shutil, sys  # noqa: E401

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
B = "tools/bench/"
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
jl = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))              # noqa: E731


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


PINS = {"tools/stagesim.py": "a3261b56", "tools/stagexec.py": "c4a6e0b6", B + "plan_ring_p5s01a.json": "ed62e8d6",
        B + "plan_ring_p5s01b.json": "75a77a00", B + "plan_ring_p5s02b_in.json": "56bfddd3",
        B + "graph_ring_p5s02a_20261010_032547.json": "7ac24924"}
got = dict((p, md5(p)[:8]) for p in PINS)
gate("P0 pins (unedited stagesim / stagexec, the three plans, the 94ffff94 graph)", got == PINS, got)
for m, h in (("stagesim", "a3261b56"), ("stagexec", "c4a6e0b6")):
    dst = os.path.join(HERE, "selftest_c160_delwire_{0}_{1}.txt".format(m, h))
    if got["tools/{0}.py".format(m)] == h:
        shutil.copy(os.path.join(ROOT, "tools", m + ".py"), dst)
    gate("C copy of unedited {0}.py kept as {1}".format(m, os.path.basename(dst)), os.path.isfile(dst) and md5(B + os.path.basename(dst))[:8] == h)

ROWF = ("term_uid", "owner_uid", "owner_class", "term_class", "term_name", "is_source", "wire_uid", "frame_diagram")
STATES = {}


def base_state_of(plan):
    ref = plan.get("base") or (plan.get("finalized") or {}).get("base")
    if ref["path"] not in STATES:
        STATES[ref["path"]] = SS.base_state(jl(ref["path"]))
    return STATES[ref["path"]]


def outside_ends(plan, ops):
    """[{op index, tunnel id, side, end, row, register_face}] - the outside end of every tunnel group, chosen as stagexec.py:865 does."""
    A, st, out = plan["actions"], base_state_of(plan), []
    regs = SX.base_registers(st)
    for k, o in enumerate(ops, 1):
        if o["kind"] not in ("tunnel", "connect_term_uid") or "in_act" not in o:
            continue
        ai, ao = A[o["in_act"] - 1], A[o["out_act"] - 1]
        side = "src" if SX._sym_of(ai["dst"])[1] == "outer" else "dst"
        end = ai["src"] if side == "src" else ao["dst"]
        row = None
        if not SX._sym_of(end)[0]:
            try:
                r = SS.resolve_addr(st, end, side == "src")
                row = dict((f, r.get(f)) for f in ROWF)
            except SS.SimError as e:
                row = {"error": str(e)}
        reg = bool(row and row.get("owner_class") in SX.SR_CLS and row.get("term_class") == "InnerTerminal" and row.get("owner_uid") in regs)
        out.append({"op": k, "kind": o["kind"], "tunnel_id": A[o["acts"][0] - 1].get("id"), "side": side, "end": end, "row": row,
                    "register_face": reg})
    return out


RES = {"card": "160-a2-1", "pins": got, "plans": {}, "delete": {}}
for name in ("plan_ring_p5s01a.json", "plan_ring_p5s01b.json", "plan_ring_p5s02b_in.json"):
    P = jl(B + name)
    try:
        ops = SX.compile_plan(P)
        err = None
    except SX.ExecStop as e:
        ops, err = None, str(e)
    oe = outside_ends(P, ops) if ops else []
    RES["plans"][name] = {"md5": md5(B + name), "ops": ops, "compile_error": err, "ops_md5": hashlib.md5(json.dumps(
        ops, sort_keys=True, default=str).encode()).hexdigest() if ops else None, "outside_ends": oe,
        "not_register_face": [x for x in oe if not x["register_face"]]}
    print("FACT {0}: {1} ops, kinds {2}; ops_md5 {3}; outside ends {4}".format(name, len(ops or []), sorted(set(
        o["kind"] for o in ops or [])), RES["plans"][name]["ops_md5"], [(x["tunnel_id"], x["kind"], (x["row"] or {}).get(
            "owner_class"), (x["row"] or {}).get("term_class"), (x["row"] or {}).get("is_source"), (x["row"] or {}).get("wire_uid"),
        x["register_face"]) for x in oe]), flush=True)
    gate("K {0} compiles with the current stagexec".format(name), err is None and ops, err)

pin = RES["plans"]["plan_ring_p5s02b_in.json"]["outside_ends"]
want = dict((x["tunnel_id"], (x["kind"], (x["row"] or {}).get("owner_class"), x["register_face"])) for x in pin)
gate("K4 p5s02b_in: t_go / t_ho -> tunnel with an RSR inner outside end; t_gi / t_hi -> tunnel with an LSR inner outside end",
     want.get("t_go") == ("tunnel", "RightShiftRegister", True) and want.get("t_ho") == ("tunnel", "RightShiftRegister", True)
     and want.get("t_gi") == ("tunnel", "LeftShiftRegister", True) and want.get("t_hi") == ("tunnel", "LeftShiftRegister", True), want)

GR = jl(B + "graph_ring_p5s02a_20261010_032547.json")
BASE = SS.base_state(GR)
MP = SS.model_for("delete_wire", SS.load_models())[0]
for w in (10394, 24264, 24300, 24285, 32594):
    st = copy.deepcopy(BASE)
    rows = [dict((f, r.get(f)) for f in ROWF) for r in SS.wire_rows(st, w)]
    in_objs = [o for o in st["objs"] if int(o["uid"]) == w]
    try:
        eff, err = SS.op_delete_wire(st, {"op": "delete_wire", "wire_uid": w}, MP, None, {})[0], None
    except SS.SimError as e:
        eff, err = None, str(e)
    RES["delete"][str(w)] = {"rows": rows, "in_objs": in_objs, "effect": eff, "error": err,
                             "in_objs_after": [o for o in st["objs"] if int(o["uid"]) == w],
                             "termless_after": SS.termless_wire(st, w), "rows_after": [r["term_uid"] for r in SS.wire_rows(st, w)]}
    print("FACT delete w{0}: rows {1}; in objs {2}; effect {3}; err {4}; in objs after {5}; termless_wire after {6}".format(
        w, [(r["term_uid"], r["owner_class"], r["term_class"], r["is_source"]) for r in rows], bool(in_objs), eff, err,
        bool(RES["delete"][str(w)]["in_objs_after"]), RES["delete"][str(w)]["termless_after"]), flush=True)
d = RES["delete"]
gate("D w24264 / w24300 have one sink row and no source row; w24285 has a source row; w32594 has a source and a sink row",
     all(len(d[k]["rows"]) == 1 and not d[k]["rows"][0]["is_source"] for k in ("24264", "24300"))
     and any(r["is_source"] for r in d["24285"]["rows"]) and len(set(r["is_source"] for r in d["32594"]["rows"])) == 2,
     dict((k, [(r["term_uid"], r["is_source"]) for r in v["rows"]]) for k, v in d.items()))

out = os.path.join(HERE, "diag_c160_a2_1_baseline.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(RES, f, indent=1, sort_keys=True, default=str)
print("FACT baseline json {0} md5 {1}".format(B + os.path.basename(out), md5(B + os.path.basename(out))), flush=True)
gate("P1 stagesim / stagexec still unedited after the run", dict((p, md5(p)[:8]) for p in ("tools/stagesim.py", "tools/stagexec.py"))
     == {"tools/stagesim.py": "a3261b56", "tools/stagexec.py": "c4a6e0b6"})
print("RESULT {0}/{1}".format(G["pass"], G["fail"]), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": B + os.path.basename(out),
                                                                                   "md5": md5(B + os.path.basename(out))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
