"""diag_c128_3_x5 - card 128-3 Step 1 (OFFLINE: no LabVIEW, no COM; stage_prerun stubs COM). MEASURE where X5's 123 comes from.
EXISTING FIRST: stage_prerun.main / x5_count / D.ops (stage_prerun.py:683-684, :1788-1821), stagexec.DryPlanBE._apply
(stagexec.py:3448-3450: ONE Stage._op per real op, verb 'wire_'+kind for REC_WIRING kinds). Nothing new is built; X5 untouched.
  M1 out-of-process --dry trace (diag_c128_3_recipe_dry.json, from a separate bgrun): verbs, groups (a) plan wiring
     (wire_<SP_WIRING kind>), (b) RLE (wire_remove_loose_ends), (c) read-only, (d) other X5-matched; per verb the plan acts
     from the dry log's `FACT  OP <verb> [acts]` lines.
  M2 IN-PROCESS repro of diag_c128_1_checks.py C4 (SP.main --dry recipe, then SP.main --prerun recipe, one process,
     --no-record): D.ops length / X5 count after each call; Stage._op wrapper depth after each install().
PREDICTION (judgement's claim + 128-1): M1 X5-matched = 16 RLE + 12 connect + 14 connect_term_uid = 42 (one _op per real op);
M2 reproduces 123 only in-process (D.ops not reset + _op wrapped again), i.e. 123 != one run's count.
    py tools/bgrun.py --material --max-min 8 --log tools/bench/diag_c128_3_x5.log -- py -u tools/bench/diag_c128_3_x5.py"""
import builtins, collections, contextlib, io, json, os, re, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stage_prerun as SP    # noqa: E402,E401
REAL_OPEN = builtins.open
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b.py")
PLAN = json.load(open(os.path.join(B, "plan_ring_p3b.json"), encoding="utf-8"))
ok, OUT = [], {}


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, str(d)[:1500]), flush=True)


WIRING = set("wire_" + k for k in SP.SP_WIRING)


def group(v):
    if not SP.WIRE_VERB_RE.search(v) or SP.DELETE_VERB_RE.search(v):
        return "not-counted"
    if v in WIRING:
        return "a"
    if v == "wire_remove_loose_ends":
        return "b"
    if re.search(r"read|census|is_broken|get_|list", v, re.I):
        return "c"
    return "d"


# ---- M1: out-of-process dry trace
tr = json.load(open(os.path.join(B, "diag_c128_3_recipe_dry.json"), encoding="utf-8"))
ops = tr["ops"]
acts = collections.defaultdict(list)
for ln in open(os.path.join(B, "diag_c128_3_recipe_dry.log"), encoding="utf-8", errors="replace"):
    m = re.match(r"\s*FACT  OP (\S+) \[([\d, ]+)\]", ln)
    if m:
        for a in m.group(2).split(","):
            acts[m.group(1)].append(PLAN["actions"][int(a) - 1].get("id"))
cnt = collections.Counter(ops)
grp = collections.Counter(group(v) for v in ops)
print("  FACT M1 out-of-process --dry: D.ops {0}; verbs {1}".format(len(ops), dict(cnt)), flush=True)
print("  FACT M1 groups: (a) plan wiring {0} | (b) RLE {1} | (c) read-only {2} | (d) other {3} | not X5-counted {4}".format(
    grp["a"], grp["b"], grp["c"], grp["d"], grp["not-counted"]), flush=True)
for v in sorted(cnt):
    print("    | {0:<26} x{1:<3} group {2:<12} acts {3}".format(v, cnt[v], group(v), acts.get(v, [])[:20]), flush=True)
x5 = SP.x5_count(ops, [], {os.path.join(B, "plan_ring_p3b.json"): (True, None, PLAN, __import__("stagexec").compile_plan(PLAN))})
print("  FACT M1 x5_count on the out-of-process trace: {0}".format(x5), flush=True)
OUT["M1"] = {"ops": len(ops), "verbs": dict(cnt), "groups": dict(grp), "x5": [x5[0], x5[1]]}
gate("M1 out-of-process X5-matched == 42 (16 RLE + 12 connect + 14 connect_term_uid)", grp["a"] + grp["b"] + grp["c"] + grp["d"] == 42,
     dict(grp))

# ---- M2: in-process repro of diag_c128_1_checks C4
depth = []


def wrapdepth():
    f, n = SP.__dict__.get("D"), 0
    import importlib
    S = importlib.import_module("stagekit").Stage._op
    while getattr(S, "__closure__", None):
        nxt = [c.cell_contents for c in S.__closure__ if isinstance(c.cell_contents, dict) and "_op" in c.cell_contents]
        if not nxt:
            break
        S, n = nxt[0]["_op"], n + 1
    return n


seq = []
for mode in ("--dry", "--prerun"):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = SP.main([mode, REC, "--no-record"])
        except SystemExit as e:
            rc = e.code
    out = buf.getvalue()
    x5l = [ln.strip() for ln in out.splitlines() if " X5 " in ln][:1]
    seq.append({"mode": mode, "rc": rc, "D.ops": len(SP.D.ops), "x5_matched_so_far": sum(1 for v in SP.D.ops if group(v) != "not-counted"),
                "op_wrap_depth": wrapdepth(), "open_is_real": builtins.open is REAL_OPEN, "x5_line": x5l})
    print("  FACT M2 after in-process {0}: {1}".format(mode, seq[-1]), flush=True)
builtins.open = REAL_OPEN
OUT["M2"] = seq
gate("M2 in-process dry->prerun reproduces 128-1's 123", any("ops 123 " in (s["x5_line"] or [""])[0] for s in seq), [s["x5_line"] for s in seq])
json.dump(OUT, REAL_OPEN(os.path.join(B, "diag_c128_3_x5.json"), "w", encoding="utf-8"), indent=1, default=str)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None),
                                  [{"path": "tools/bench/diag_c128_3_x5.json", "md5": SP.md5(os.path.join(B, "diag_c128_3_x5.json"))}])), flush=True)
os._exit(1 if nf else 0)
