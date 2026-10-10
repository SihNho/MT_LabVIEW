# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_162-a2-3.md
# ---
r"""selftest_c162_stage_shared - card 162-a2-3 step 5 (OFFLINE, no LabVIEW, no COM). Under test (called, not copied): tools/stage_shared.py
base_sink_renames / checkpoint_step_table / insert_stub_deletes. Data: tools/bench/prep_c162_a2_3_equiv.json - per copy the real inputs and the
OLD block's output, recorded by prep_c162_a2_3_equiv.py BEFORE any caller was rewritten (15 records: 8 L, 5 P, 2 S).
PREDICTION: R each function on each record's inputs == the recorded old-block output (JSON); A each rewritten caller calls stage_shared once with the
recorded argument (why template / constant; `actions` passed only by prep_c160_c3_1_pred) and no longer holds the block's distinctive line;
C every caller compiles; M the module is labview none and imports only collections."""
import ast, json, os, py_compile, sys                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck as IC                                                                       # noqa: E402
import stage_shared as SH                                                                   # noqa: E402

g = IC.Gates()
D = lambda x: json.dumps(x, sort_keys=True, default=sorted)                                 # noqa: E731 - as prep_c162_a2_3_equiv.py
EQ = os.path.join(ROOT, "tools", "bench", "prep_c162_a2_3_equiv.json")
REC = json.load(open(EQ, encoding="utf-8"))["records"]
FN = {"L": "base_sink_renames", "P": "checkpoint_step_table", "S": "insert_stub_deletes"}
MARK = {"L": 'own[int(r["owner_uid"])].add(int(r["term_uid"]))', "P": 'an = max(ops[k - 1]["acts"]) if k else 0', "S": '"dw_" + a["id"][2:]'}
print("FACT equiv record {0} md5 {1}; stage_shared md5 {2}".format(os.path.relpath(EQ, ROOT), IC.md5(EQ), IC.md5(SH.__file__)), flush=True)
g("R0 15 records (8 L, 5 P, 2 S)", sorted(r["block"] for r in REC) == ["L"] * 8 + ["P"] * 5 + ["S"] * 2, [r["block"] for r in REC])


def run(r):
    i, a = r["inputs"], r["args"]
    if r["block"] == "L":
        ren, own, wr = SH.base_sink_renames(i["actions"], dict((int(u), t) for u, t in i["base_terms"].items()), a["why_fmt"])
        return {"ren": ren, "own": dict(own), "wr": dict(wr)}
    if r["block"] == "P":
        return SH.checkpoint_step_table(i["ops"], i["cps"], dict((int(k), v) for k, v in i["sfn"].items()), i["actions"])
    return SH.insert_stub_deletes(i["actions"], i["wire_by_id"], a["why"])


def calls(src):
    """[(fn name, [resolved positional args])] of every SH.<fn>(...) call; a Name argument resolves to its module-level string constant."""
    tree, env = ast.parse(src), {}
    for st in tree.body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name) and isinstance(st.value, ast.Constant):
            env[st.targets[0].id] = st.value.value
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == "SH":
            out.append((n.func.attr, [x.value if isinstance(x, ast.Constant) else env.get(x.id, "<" + x.id + ">") if isinstance(x, ast.Name)
                                      else "<expr>" for x in n.args]))
    return out


for r in REC:
    f = os.path.join(ROOT, r["file"])
    new = run(r)
    g("R {0} {1} == recorded old-block output".format(r["block"], r["file"]), json.loads(D(new)) == r["old_out"], "{0} chars".format(len(D(new))))   # parsed: int keys -> str
    src = open(f, encoding="utf-8").read()
    cs = [c for c in calls(src) if c[0] == FN[r["block"]]]
    if r["block"] == "L":
        ok = len(cs) == 1 and len(cs[0][1]) == 3 and cs[0][1][2] == r["args"]["why_fmt"]
    elif r["block"] == "P":
        ok = len(cs) == 1 and (len(cs[0][1]) == 4) == bool(r["args"]["actions"])
    else:
        ok = len(cs) == 1 and len(cs[0][1]) == 3 and cs[0][1][2] == r["args"]["why"]
    g("A {0} {1} calls SH.{2} once with the recorded argument; block line gone".format(r["block"], r["file"], FN[r["block"]]),
      ok and MARK[r["block"]] not in src, [(c[0], len(c[1])) for c in cs])
    try:
        py_compile.compile(f, doraise=True, cfile=os.path.join(os.environ.get("TEMP", "."), "c162_a2_3_pyc.tmp"))
        cok = True
    except py_compile.PyCompileError as e:
        cok = str(e)[:300]
    g("C {0} compiles; md5 {1}".format(r["file"], IC.md5(f)[:8]), cok is True, cok)
msrc = open(SH.__file__, encoding="utf-8").read()
imps = sorted(set(a.name for n in ast.walk(ast.parse(msrc)) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names))
g("M stage_shared header labview none, imports only collections", "# labview: none" in msrc.splitlines()[1] and imps == ["collections"], imps)
print(g.result([{"path": "tools/stage_shared.py", "md5": IC.md5(SH.__file__)}, {"path": "tools/bench/prep_c162_a2_3_equiv.json", "md5": IC.md5(EQ)}]),
      flush=True)
sys.exit(1 if g.failed else 0)
