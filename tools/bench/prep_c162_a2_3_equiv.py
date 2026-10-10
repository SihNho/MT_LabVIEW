# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_162-a2-3.md
# ---
r"""prep_c162_a2_3_equiv - card 162-a2-3 step 3 (OFFLINE, BEFORE any caller is rewritten): for every copy listed in prep_c162_a2_3_copies.log,
run the OLD block text (read from the caller at its listed lines, exec'd on that caller's real inputs) and the NEW tools/stage_shared.py function on
the same inputs, compare by JSON equality. Writes prep_c162_a2_3_equiv.json = per copy {file, block, lines, inputs, args, old_out} - the record
selftest_c162_stage_shared.py replays. Inputs per caller are the files it reads: L its PLAN + finalized base graph; P its plan, stagexec.compile_plan,
its own checkpoint rule (checkpoint_ops for c160_c3_1, {0, last} | BIND_KINDS ops for the rest), step_files; S regface: plan_ring_p5s02b_in.json +
graph 7ac24924 stub wires; prep_c160_b3_1_mk: the same input, stub wires and FRESH ids derived as that script derives them (lines 113-132).
Info gates (non-gating 'INFO'): L ren == the stored licence json `renames`; P table == the stored pred json e1.checkpoints; S mk == stored in2 actions.
PREDICTION CONTRACT: E0 15 copies read; EQ every copy old == new (JSON); EQS mk full new expression (fresh pre-map + insert) == old block.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c162_a2_3_equiv.log -- py -u tools/bench/prep_c162_a2_3_equiv.py"""
import ast, collections, copy, json, os, re, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck as IC                                                                       # noqa: E402
import stagexec as SX, stagesim as SS                                                       # noqa: E401,E402
import stage_shared as SH                                                                   # noqa: E402
B = "tools/bench/"
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                     # noqa: E731
D = lambda x: json.dumps(x, sort_keys=True, default=sorted)                                 # noqa: E731 - sets -> sorted lists
g = IC.Gates()
COP = [re.match(r"COPY (\w) \| ([^:]+):(\d+)-(\d+) \|", ln) for ln in open(os.path.join(ROOT, B + "prep_c162_a2_3_copies.log"), encoding="utf-8")]
COP = sorted(set((m.group(1), m.group(2), int(m.group(3)), int(m.group(4))) for m in COP if m))
g("E0 copies read from prep_c162_a2_3_copies.log: {0}".format(len(COP)), len(COP) == 15, COP)


def src_of(f):
    return open(os.path.join(ROOT, f), encoding="utf-8").read()


def const_of(src, name):
    """value of a module-level `NAME = os.path.join(B, "x")` / tuple-assign path -> tools/bench/x."""
    for st in ast.parse(src).body:
        if isinstance(st, ast.Assign):
            t, v = st.targets[0], st.value
            pairs = zip(t.elts, v.elts) if isinstance(t, ast.Tuple) and isinstance(v, ast.Tuple) else [(t, v)]
            for tn, vn in pairs:
                if isinstance(tn, ast.Name) and tn.id == name and isinstance(vn, ast.Call) and vn.args and isinstance(vn.args[-1], ast.Constant):
                    return B + vn.args[-1].value


def why_of(txt):
    """the `why` value of the block's dict: a "...".format(...) template or a constant / Name."""
    for n in ast.walk(ast.parse(txt)):
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if isinstance(k, ast.Constant) and k.value == "why":
                    if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == "format":
                        return v.func.value.value
                    return v.value if isinstance(v, ast.Constant) else v.id


REC = []
for blk, f, a, b in COP:
    src = src_of(f)
    txt = "\n".join(src.splitlines()[a - 1:b])
    if blk == "L":
        plan = const_of(src, "PLAN")
        P = J(plan)
        bt = dict((int(r["term_uid"]), r) for r in J(P["finalized"]["base"]["path"])["terminals"])
        A = P["actions"]
        ns = {"collections": collections, "A": A, "bt": bt}
        exec(txt, ns)
        old = {"ren": ns["ren"], "own": dict(ns["own"]), "wr": dict(ns["wr"])}
        wf = why_of(txt)
        ren, own, wr = SH.base_sink_renames(A, bt, wf)
        new = {"ren": ren, "own": dict(own), "wr": dict(wr)}
        dst = set(int(x["dst"]["term_uid"]) for x in A if isinstance(x.get("dst"), dict) and x["dst"].get("term_uid") is not None)
        inputs = {"actions": A, "base_terms": dict((str(u), r) for u, r in bt.items() if u in dst)}
        args = {"why_fmt": wf}
        stored = J(const_of(src, "LIC")).get("renames")
        print("INFO L {0}: ren == stored licence renames: {1} ({2} entries)".format(f, D(stored) == D(ren), len(ren)), flush=True)
    elif blk == "P":
        plan = const_of(src, "RRP")
        p = J(plan)
        fz = p.get("finalized") or {}
        ops = SX.compile_plan(p)
        if "checkpoint_ops" in src:
            cps = list(SX.checkpoint_ops(ops))
        else:
            cps = sorted(set([0, len(ops)]) | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))
        SFN = dict((int(x["n"]), x) for x in fz.get("step_files") or [])
        A = p["actions"]
        ns = {"ops": ops, "cps": cps, "SFN": SFN, "A": A}
        exec(txt, ns)
        old = ns["cpe"]
        use_a = '"ids"' in txt
        new = SH.checkpoint_step_table(ops, cps, SFN, A if use_a else None)
        inputs = {"ops": ops, "cps": cps, "sfn": dict((str(k), v) for k, v in SFN.items()), "actions": A if use_a else None}
        args = {"actions": use_a}
        stored = (J(const_of(src, "PP")).get("e1") or {}).get("checkpoints")
        print("INFO P {0}: table == stored pred e1.checkpoints: {1} ({2} checkpoints)".format(f, D(stored) == D(new), len(new)), flush=True)
    else:
        PIN, GR = J(B + "plan_ring_p5s02b_in.json"), J(B + "graph_ring_p5s02a_20261010_032547.json")
        BASE = SS.base_state(GR)
        if f.endswith("regface.py"):
            A = PIN["actions"]
            sink = lambda wid: next(x["dst"] for x in A if x.get("id") == wid)                                        # noqa: E731
            wire_of = lambda e: next(r["wire_uid"] for r in BASE["terminals"] if r["term_uid"] == e["term_uid"])   # noqa: E731
            DW = {"t_go": wire_of(sink("w_gr")), "t_ho": wire_of(sink("w_hr"))}
            ns = {"TP": copy.deepcopy(PIN), "DW": DW}
            exec(txt, ns)
            old = ns["TP"]["actions"]
            wf = why_of(txt)
            new = SH.insert_stub_deletes(PIN["actions"], DW, wf)
            inputs, args = {"actions": PIN["actions"], "wire_by_id": DW}, {"why": wf}
        else:
            msrc = src_of(f)
            mod = {"re": re}
            for ln in msrc.splitlines():
                if ln.startswith(("WHY_ASSUME =", "WHY_FRESH =", "WHY_DEL =", "DEL_POS, STUB_UID =")):
                    exec(ln, mod)
            K1 = len(J(B + "plan_ring_p5s02a.json")["actions"])
            STUB = []
            for p_ in mod["DEL_POS"]:
                x = PIN["actions"][p_ - K1]
                ws = sorted(set(int(r.get("wire_uid") or 0) for r in GR["terminals"] if int(r["term_uid"]) == int(x["dst"]["term_uid"])))
                tsym = x["src"].split(":", 1)[1].split(".")[0] if isinstance(x["src"], str) else None
                tun = next((y for y in PIN["actions"] if y.get("op") == "tunnel" and y.get("as") == tsym), None)
                STUB.append({"id": x["id"], "wire": ws[0] if len(ws) == 1 else None, "tunnel": tun and tun["id"]})
            DEL_BEFORE, FRESH_IDS = dict((s["tunnel"], s) for s in STUB), set(s["id"] for s in STUB)
            ns = dict(mod, P2=copy.deepcopy(PIN), DEL_BEFORE=DEL_BEFORE, FRESH_IDS=FRESH_IDS)
            exec(txt, ns)
            old = ns["P2"]["actions"]
            WA, WF = mod["WHY_ASSUME"], mod["WHY_FRESH"]
            pre = [dict(x, why=WA.sub("", x.get("why") or "") + " | " + WF) if x.get("id") in FRESH_IDS else x for x in copy.deepcopy(PIN)["actions"]]
            wbi = dict((t, s["wire"]) for t, s in DEL_BEFORE.items())
            new = SH.insert_stub_deletes(pre, wbi, mod["WHY_DEL"])
            g("EQS {0}: fresh pre-map + insert_stub_deletes == the old loop ({1} actions)".format(f, len(new)), D(old) == D(new), len(old))
            inputs, args = {"actions": pre, "wire_by_id": wbi}, {"why": mod["WHY_DEL"]}
            print("INFO S {0}: == stored plan_ring_p5s02b_in2.json actions: {1}".format(f, D(J(B + "plan_ring_p5s02b_in2.json")["actions"]) == D(new)), flush=True)
    g("EQ {0} {1}:{2}-{3} old block == stage_shared (JSON)".format(blk, f, a, b), D(old) == D(new), "{0} chars".format(len(D(old))))
    REC.append({"block": blk, "file": f, "lines": [a, b], "file_md5": IC.md5(os.path.join(ROOT, f)), "inputs": inputs, "args": args, "old_out": json.loads(D(old))})
OUT = os.path.join(ROOT, B + "prep_c162_a2_3_equiv.json")
json.dump({"card": "162-a2-3", "stage_shared_md5": IC.md5(os.path.join(ROOT, "tools", "stage_shared.py")), "records": REC}, open(OUT, "w", encoding="utf-8"))
print("FACT equiv record {0} md5 {1}, {2} records".format(B + "prep_c162_a2_3_equiv.json", IC.md5(OUT), len(REC)), flush=True)
print(g.result([{"path": B + "prep_c162_a2_3_equiv.json", "md5": IC.md5(OUT)}]), flush=True)
sys.exit(1 if g.failed else 0)
