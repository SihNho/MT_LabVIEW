# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c147_b1_1_rescore2.log:3
# ---
r"""selftest_c147_b1_2 - card 147-b1-2 (PD356(b)): offline test of stagekit's D / TD / PB on the s06 retry end read (147-a1-8).
REWRITTEN by card chat-T6 (PD366, docs/d1/result-gates.md): the gates key terminals by POSITION and wires by their ends; a NAME
change is INFO (licensed or not), a re-used wire uid is INFO; a real loss / unwire / source change still FAILS. No LabVIEW, no COM:
stagekit / vigraph / jev_candidates / addrcheck are imported inside main() for their PURE functions only.
DATA: the 147-a1-8 end read = tools/bench/fixtures/t6_s06_a1_8_end.json (the live diag_c147_p4s06v18_scratch.json was overwritten by
the 147-c3 rerun); its 5 stored fields are joined, in READ order, with the sim end row bound to each real row (creation map + run
binding, then bound owner + direction + name - selftest_t6_poskey.enrich). Plan step files are md5-checked here (raw OR LF content:
a git worktree checked out with core.autocrlf=true holds CRLF text), not through stagexec.load_final_plan.
CASES (KEPT = still tests something true; REWRITTEN = same scenario, the new verdict; RETIRED = tested the removed licence rule):
  P0/P1 pins (raw or LF md5) KEPT; T0 the NAME key (stagekit.term_identity_names) reproduces the run's stored FAIL REWRITTEN (was:
  default call == pre-edit code); T0b licence file parses to the 5 renames KEPT, pb_rename_rows ignores the licence REWRITTEN (was:
  renames None -> rows untouched); R1 binding KEPT; T1 L5 D/TD/PB PASS, w23807 reuse noted KEPT; T1n the SAME with NO licence (new);
  T2 L3 (partial licence) -> TD PASS, 9505/9508 renames reported as INFO REWRITTEN (was: TD FAILS naming them); T3 w23807 keeps the
  removed sink 9519 -> D FAILS KEPT (RETIRED: `reuse_bad == [23807]`, no such list now); T4 renamed 2832 changes owner -> TD FAILS
  KEPT; T4b 2832 renamed to a name the licence does not give -> TD PASS, rename INFO REWRITTEN (was: FAIL); T5 s03/s04/s05 stored
  reads: name key == stored verdict and position key PASS REWRITTEN (was: default == pre-edit); F1/F2 stagekit format KEPT.
RETIRED assertions: T0 "default == pre-edit code", T0b "pb_rename_rows(.., None) returns the rows untouched", T2 "TD FAILS naming
9505/9508", T3 "reuse_bad == [23807]", T4b "TD FAILS on an unlicensed name"."""
import ast, collections, copy, hashlib, json, os, sys                             # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
PINS = {"tools/stagexec.py": "1d5309f4", "tools/gscript.py": "1a80236e", "tools/elrule.py": "a5ee7d5c", "tools/bench/memory_model.json": "d12bcd3b",
        "tools/bench/plan_ring_p4_s06v18.json": "cfbd9823", "tools/bench/plan_ring_p4_s06v18_pred.json": "c1bd6b3e",
        "tools/bench/plan_ring_p4_s06v18_licence.json": "7f70bbf9", "tools/bench/plan_ring_p4_s06v18_in.json": "db72d8af",
        "tools/recipes/stage_d1_ring_p4_s06v18.py": "d947df5d", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py": "31009bfc"}
FIX = os.path.join(BENCH, "fixtures", "t6_s06_a1_8_end.json")
T5 = (("s03", "plan_ring_p4_s03v18.json", "diag_c143_p4s03v18_scratch.json", "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl"),
      ("s04", "plan_ring_p4_s04v18.json", "diag_c144_p4s04v18_scratch.json", "plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl"),
      ("s05", "plan_ring_p4_s05v18.json", "diag_c145_p4s05v18_scratch.json", "plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl"))
L5 = {"renames": [{"node": 2626, "term_uids": [2832, 4160, 4165], "from": "array", "to": "element"}, {"node": 9503, "term_uids": [9505, 9508], "from": "Value", "to": ""}]}
L3 = {"renames": L5["renames"][:1]}
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def fact(s):
    print("  FACT  " + str(s)[:900], flush=True)


MAIN = ROOT.split(os.sep + ".claude" + os.sep + "worktrees")[0]


def data(p):
    """A project-relative data path: this tree's file, else the MAIN tree's (plan step files under tools/bench/sim are untracked,
    so a git worktree lacks them - measured 2026-10-08, sim/ring_p4_s06v18/step_25_wire.json)."""
    if os.path.isabs(p):
        return p
    q = os.path.join(ROOT, p)
    return q if os.path.exists(q) else os.path.join(MAIN, p)


def md5s(p):
    """(raw md5, LF-content md5) of a project file; a pin matches either."""
    b = open(data(p), "rb").read()
    return hashlib.md5(b).hexdigest(), hashlib.md5(b.replace(b"\r\n", b"\n")).hexdigest()


def pin_ok(p, pin):
    return any(m.startswith(pin) for m in md5s(p))


def load(plan, rows_json, cmap):
    """(P, BASE, L, rows5, ob, tb, pins_ok) - plan, base graph, sim end state (finalized step file, md5 raw-or-LF), the stored end read,
    the run's object binding (stagexec 'bound') and the creation map's term/obj binds."""
    P = J(BENCH, plan)
    fz = P["finalized"]
    BASE = J(data(fz["base"]["path"]))
    sf = fz["step_files"][len(P["actions"])]
    L = J(data(sf["path"]))["state"]
    ok = pin_ok(fz["base"]["path"], fz["base"]["md5"]) and pin_ok(sf["path"], sf["md5"])
    S = J(rows_json)
    ob, tb = {}, {}
    for e in S.get("stagexec") or []:
        ob.update((int(k), int(v)) for k, v in (e.get("bound") or {}).items())
    for line in open(os.path.join(BENCH, "creation_map", cmap), encoding="utf-8"):
        x = json.loads(line)
        if x.get("rec") == "bind":
            (ob if x["kind"] == "obj" else tb)[int(x["sim"])] = int(x["real"])
    return P, BASE, L, S, ob, tb, ok


def main():
    import stagekit as K, vigraph as V, jev_candidates as JC                     # noqa: E401  pure functions only
    import selftest_t6_poskey as T6                                               # enrich(): the read-order join, one copy
    md0 = dict((p, md5s(p)) for p in PINS)
    gate("P0 pins before == card inputs (raw or LF-content md5): " + ", ".join("{0} {1}".format(os.path.basename(p), PINS[p]) for p in PINS),
         all(pin_ok(p, v) for p, v in PINS.items()), dict((os.path.basename(p), [m[:8] for m in md0[p]]) for p in PINS if not pin_ok(p, PINS[p])))
    P, BASE, L, S, OB, TBc, sok = load("plan_ring_p4_s06v18.json", FIX, "plan_ring_p4_s06v18_cfbd9823_20261008_125817.jsonl")
    PRED = J(BENCH, "plan_ring_p4_s06v18_pred.json")
    B, SIM = BASE["terminals"], L["terminals"]
    REAL, unb = T6.enrich(B, SIM, S["real_end_rows"], OB, TBc)
    gate("R1 every sim end row binds to one real end row; base + step file md5 == the plan's pins", not unb and sok, unb[:6])
    BIND = {"term": TBc, "obj": OB}
    nm = K.term_identity_names(B, SIM, REAL)
    gate("T0 the NAME key reproduces the run's stored FAIL (td_ok {0}, d_ok {1})".format(nm["td_ok"], nm["d_ok"]),
         not nm["td_ok"] and not nm["d_ok"] and S["term_identity"]["td_ok"] is False and S["term_identity"]["d_ok"] is False)
    LF = J(BENCH, "plan_ring_p4_s06v18_licence.json")
    p_none, p_l5 = K.pb_rename_rows(B, SIM, REAL, None), K.pb_rename_rows(B, SIM, REAL, K.licence_renames(L5))
    gate("T0b today's licence file carries the 5 renames -> licence_renames == L5's (5 keys); pb_rename_rows gives the same rows with or without it",
         K.licence_renames(LF) == K.licence_renames(L5) and len(K.licence_renames(LF) or {}) == 5 and p_none == p_l5, sorted(K.licence_renames(LF) or {}))
    LAB, FSP = JC.node_labels_default(), BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    objs = [dict(o, uid=OB.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]
    want = set((int(y["node"]), y["term"]) for y in P["open_rows"])

    def pb(ren):
        rows, restored, bad = K.pb_rename_rows(B, SIM, REAL, ren, bind=BIND)
        # card chat-T7 (PD373(d), fp-70): the ONE library PB, stagekit.pb_check - it converts the STORED name-keyed pred explicitly; the
        # name compare `rk == PRED["cdiff_rows"]` and the `want` pair set stood here (git 18c241ec :120-123).
        r = K.pb_check(S1f, V.build4(rows, objs, copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True), K.pred_end_graph(L, LAB, FSP),
                       PRED["cdiff_rows"], P["open_rows"], bad)
        return r["ok"], {"extra": r["extra_sinks"], "missing": r["missing_sinks"], "pairs_missing": r["pairs_missing"], "slots": r["slots_want"],
                         "restored": restored[:6]}

    for tag, lic in (("T1 L5 (5 renames)", L5), ("T1n NO licence", None)):
        ren = K.licence_renames(lic) if lic else None
        t1, p1 = K.term_identity_gates(B, SIM, REAL, renames=ren, bind=BIND), pb(ren)
        gate("{0} D PASS: new {1} == sim {2}, lost {3} == sim {4}; reuse_noted (INFO) {5}".format(tag, t1["d_new"], len(t1["sim_new"]), t1["d_lost"],
             len(t1["sim_lost_w"]), [n["wire"] for n in t1["reuse_noted"]]), t1["d_ok"] and [n["wire"] for n in t1["reuse_noted"]] == [23807])
        gate("{0} TD PASS: lost {1} == gone {2}, unwired {3}, moved {4}; renames (INFO) {5}".format(tag, len(t1["lost"]), len(t1["gone"]), t1["unwired"],
             t1["moved"], len(t1["renames"])), t1["td_ok"] and t1["unlicensed_renames"] == [])
        gate("{0} PB PASS: cdiff == pred {1} rows and open pairs".format(tag, len(PRED["cdiff_rows"])), p1[0], p1[1])
    t2 = K.term_identity_gates(B, SIM, REAL, renames=K.licence_renames(L3), bind=BIND)
    named = sorted(x[0][0] for x in t2["renames"])
    gate("T2 L3 (2832/4160/4165 only): TD PASSES, the 9503 renames are INFO (renames on nodes {0}), unlicensed []".format(named),
         t2["td_ok"] and 9503 in named and t2["unlicensed_renames"] == [])
    fact("T2 L3 D {0}; PB {1}".format(t2["d_ok"], pb(K.licence_renames(L3))[0]))
    R3 = [dict(r, wire_uid=23807, is_source=False) if int(r["term_uid"]) == 9519 else r for r in REAL]
    t3 = K.term_identity_gates(B, SIM, R3, renames=K.licence_renames(L5), bind=BIND)
    gate("T3 w23807 keeps sink 9519 (the sim removed it) -> D FAILS: d_ok {0}, lost {1}/{2}".format(t3["d_ok"], t3["d_lost"], len(t3["sim_lost_w"])), not t3["d_ok"])
    t3b = K.term_identity_gates(B, SIM, R3)
    fact("T3 same rows, no bind: d_ok {0} new {1}/{2} lost {3}/{4}".format(t3b["d_ok"], t3b["d_new"], len(t3b["sim_new"]), t3b["d_lost"], len(t3b["sim_lost_w"])))
    t4 = K.term_identity_gates(B, SIM, [dict(r, owner_uid=9503) if int(r["term_uid"]) == 2832 else r for r in REAL], renames=K.licence_renames(L5), bind=BIND)
    gate("T4 renamed 2832 changes owner 2626 -> 9503: TD FAILS (lost {0}, moved {1})".format(t4["lost"][:3], t4["moved"][:3]), not t4["td_ok"])
    t4b = K.term_identity_gates(B, SIM, [dict(r, term_name="index") if int(r["term_uid"]) == 2832 else r for r in REAL], renames=K.licence_renames(L5), bind=BIND)
    gate("T4b 2832 renamed 'array'->'index' (the licence says 'element'): TD PASSES, the name is INFO {0}".format(
        [x for x in t4b["renames"] if x[2] == "index"]), t4b["td_ok"] and any(x[2] == "index" for x in t4b["renames"]))
    for tag, plan, scr, cmap in T5:
        Px, Bx, Lx, Sx, OBx, TBx, okx = load(plan, os.path.join(BENCH, scr), cmap)
        REx, unx = T6.enrich(Bx["terminals"], Lx["terminals"], Sx["real_end_rows"], OBx, TBx)
        nx = K.term_identity_names(Bx["terminals"], Lx["terminals"], REx)
        px = K.term_identity_gates(Bx["terminals"], Lx["terminals"], REx, bind={"term": TBx, "obj": OBx})
        st = Sx["term_identity"]["td_ok"] and Sx["term_identity"]["d_ok"]
        gate("T5 {0} ({1}): name key == stored run verdict ({2}) and the position key PASSES TD {3} D {4}".format(tag, scr, st, px["td_ok"], px["d_ok"]),
             okx and not unx and (nx["td_ok"] and nx["d_ok"]) == st and st and px["td_ok"] and px["d_ok"])
    path = os.path.join(ROOT, "tools", "stagekit.py")
    src = open(path, encoding="utf-8").read()
    bad = ["line {0}".format(nd.lineno) for nd in ast.walk(ast.parse(src, path)) if isinstance(nd, ast.BinOp) and isinstance(nd.op, ast.Mod)
           and isinstance(getattr(nd, "left", None), (ast.Constant, ast.JoinedStr)) and (not isinstance(nd.left, ast.Constant) or isinstance(nd.left.value, str))]
    gate("F1 stagekit builds no message with the `%` operator", not bad, bad[:3])
    gate("F2 stagekit's own source carries no bold-FAIL marker", ("*" * 2 + "FAIL" + "*" * 2) not in src.replace("`" + "*" * 2 + "FAIL" + "*" * 2 + "`", ""))
    md1 = dict((p, md5s(p)) for p in PINS)
    gate("P1 pins after == before", md1 == md0)


if __name__ == "__main__":
    sys.path.insert(0, BENCH)
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
