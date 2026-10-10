# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_162-a2-1.md
# ---
r"""prep_c162_a2_1_pinsweep - card 162-a2-1 step 1 (OFFLINE, no LabVIEW, no COM): ONE pin sweep BEFORE any edit
(retrospective-cycle160 finding 1, archive/peer/2026-10-10-retrospective-cycle160.md:545). A MEASUREMENT: stale pins are listed, not fixed.

Scope (brief_162-a2-1.md step 1): the scripts cards 162-a2-1 / 162-a2-2 edit or call - selftest_c157_innerface, selftest_c160_regface,
selftest_c160_l0stem, selftest_chat_p1, prep_c156_a1_1_licence, prep_c156_a1_1_pred, selftest_c161_delckpt (run by this card) - plus every
selftest_c15* / selftest_c16* that names one of them (grep at card time: selftest_c158_runcheck, selftest_c158_wire0face, selftest_c159_a4_1,
selftest_c160_l0stem_regress). Pins are read from the SOURCE by ast (the self-tests are not imported - importing runs them):
  (a) dict literals {path: "<hex 8-32>"}; (b) md5(<path>).startswith("<hex>") / md5(<path>) == "<hex>"; (c) tuple assigns X, X_PIN = <path>, "<hex>".
Paths resolve from module-level str / '+' / os.path.join assignments (ROOT -> '', HERE/BENCH -> tools/bench, TOOLS -> tools).
TARGET = stagekit / stagexec / stagesim / stage_prerun / plan_ring_p5s02b*.json / docs/d1/ring-p5b.md (the brief's list); other pins are listed too.
Prior art: no pin-sweep script exists (glob tools/**/*pin*sweep* empty); md5 + gate counter are CALLED from tools/invcheck.py (md5, Gates).
PREDICTION CONTRACT: S1 all 11 scope scripts parse; S2 the anchor pins are found (selftest_c157_innerface.py:72 stagesim,
selftest_c161_delckpt.py:137 stagekit, selftest_c159_a4_1.py:300 stagexec); S3 every TARGET pin's path exists. Expected (grep before the run):
selftest_c157_innerface:72 stagesim pin already 95a162ba in the working tree (EQUAL); selftest_c159_a4_1:300 stagexec 7a712ccb STALE (file a4df7e15).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c162_a2_1_pinsweep.log -- py -u tools/bench/prep_c162_a2_1_pinsweep.py"""
import ast
import fnmatch
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck as IC                                                                       # noqa: E402  md5 + Gates (shared)

SCOPE = ["selftest_c157_innerface", "selftest_c160_regface", "selftest_c160_l0stem", "selftest_chat_p1", "prep_c156_a1_1_licence",
         "prep_c156_a1_1_pred", "selftest_c161_delckpt", "selftest_c158_runcheck", "selftest_c158_wire0face", "selftest_c159_a4_1",
         "selftest_c160_l0stem_regress"]
TARGETS = ["tools/stagekit.py", "tools/stagexec.py", "tools/stagesim.py", "tools/stage_prerun.py", "tools/bench/plan_ring_p5s02b*.json",
           "docs/d1/ring-p5b.md"]
ANCHORS = [("selftest_c157_innerface", 72, "tools/stagesim.py"), ("selftest_c161_delckpt", 137, "tools/stagekit.py"),
           ("selftest_c159_a4_1", 300, "tools/stagexec.py")]
HEX = re.compile(r"^[0-9a-f]{8,32}$")
KNOWN = {"ROOT": "", "HERE": "tools/bench", "BENCH": "tools/bench", "TOOLS": "tools"}


def norm(p):
    return os.path.normpath(p).replace("\\", "/").lstrip("./") if p else p


def resolve(node, env):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id, KNOWN.get(node.id))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = resolve(node.left, env), resolve(node.right, env)
        return None if a is None or b is None else a + b
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join":
        parts = [resolve(x, env) for x in node.args]
        return None if any(x is None for x in parts) else "/".join(x for x in parts if x)
    return None


def hexval(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) and HEX.match(node.value) else None


def pins_of(src):
    """[(line, path or None, pinned)] from one script's source."""
    tree, env, out = ast.parse(src), {}, []
    for st in tree.body:                                         # module-level path names (single and tuple assigns)
        if isinstance(st, ast.Assign) and len(st.targets) == 1:
            t, v = st.targets[0], st.value
            if isinstance(t, ast.Name):
                r = resolve(v, env)
                if r is not None:
                    env[t.id] = r
            elif isinstance(t, ast.Tuple) and isinstance(v, ast.Tuple) and len(t.elts) == len(v.elts):
                for i, (tn, vn) in enumerate(zip(t.elts, v.elts)):
                    if isinstance(tn, ast.Name):
                        r = resolve(vn, env)
                        if r is not None and not hexval(vn):
                            env[tn.id] = r
                        if hexval(vn) and re.search(r"(_PIN|_MD5)$", tn.id) and i > 0:
                            out.append((vn.lineno, norm(resolve(v.elts[i - 1], env)), hexval(vn)))
    for nd in ast.walk(tree):
        if isinstance(nd, ast.Dict):
            for k, v in zip(nd.keys, nd.values):
                if k is not None and hexval(v):
                    out.append((v.lineno, norm(resolve(k, env)), hexval(v)))
        elif isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute) and nd.func.attr == "startswith" and nd.args \
                and hexval(nd.args[0]) and isinstance(nd.func.value, ast.Call) and "md5" in ast.dump(nd.func.value.func) \
                and nd.func.value.args:
            out.append((nd.args[0].lineno, norm(resolve(nd.func.value.args[0], env)), hexval(nd.args[0])))
        elif isinstance(nd, ast.Compare) and len(nd.comparators) == 1 and isinstance(nd.ops[0], ast.Eq) and hexval(nd.comparators[0]) \
                and isinstance(nd.left, ast.Call) and "md5" in ast.dump(nd.left.func) and nd.left.args:
            out.append((nd.comparators[0].lineno, norm(resolve(nd.left.args[0], env)), hexval(nd.comparators[0])))
    return sorted(set(out), key=lambda x: (x[0], x[1] or ""))


g = IC.Gates()
rows, parsed = [], 0
for s in SCOPE:
    p = os.path.join(ROOT, "tools", "bench", s + ".py")
    try:
        found = pins_of(open(p, encoding="utf-8").read())
        parsed += 1
    except Exception as e:                                       # noqa: BLE001 - reported as a gate
        print("FACT parse error {0}: {1}".format(s, e), flush=True)
        continue
    print("FACT {0}.py md5 {1} pins found {2}".format(s, IC.md5(p)[:8], len(found)), flush=True)
    for line, path, pinned in found:
        cur = IC.md5(os.path.join(ROOT, path)) if path else "UNRESOLVED"
        tgt = bool(path) and any(fnmatch.fnmatch(path, t) for t in TARGETS)
        rows.append((s, line, path or "?", pinned, cur, cur.startswith(pinned), tgt))
g("S1 all {0} scope scripts parse".format(len(SCOPE)), parsed == len(SCOPE), parsed)
for s, ln, tp in ANCHORS:
    g("S2 anchor pin {0}.py:{1} {2} found".format(s, ln, tp), any(r[0] == s and r[1] == ln and r[2] == tp for r in rows))
miss = [r for r in rows if r[6] and r[4] in ("MISSING", "UNRESOLVED")]
g("S3 every TARGET pin's path exists", not miss, miss)
print("TABLE script:line | pin label (path) | pinned | current | equal | target", flush=True)
for s, ln, path, pinned, cur, eq, tgt in rows:
    print("PIN | {0}.py:{1} | {2} | {3} | {4} | {5} | {6}".format(s, ln, path, pinned, cur[:8] if cur not in ("MISSING", "UNRESOLVED") else cur,
                                                                  "EQUAL" if eq else "STALE", "TARGET" if tgt else "other"), flush=True)
tr = [r for r in rows if r[6]]
st = [r for r in tr if not r[5]]
print("FACT TARGET pins {0}: equal {1}, stale {2}: {3}".format(len(tr), len(tr) - len(st), len(st),
      ["{0}.py:{1} {2} {3}->{4}".format(r[0], r[1], r[2], r[3], r[4][:8]) for r in st]), flush=True)
ot = [r for r in rows if not r[6] and not r[5]]
print("FACT other pins {0}: not equal {1}: {2}".format(len(rows) - len(tr), len(ot),
      ["{0}.py:{1} {2} {3}->{4}".format(r[0], r[1], r[2], r[3], r[4][:8]) for r in ot]), flush=True)
print("FACT current md5: " + ", ".join("{0} {1}".format(t, IC.md5(os.path.join(ROOT, t))[:8]) for t in TARGETS[:4] + TARGETS[5:]), flush=True)
print(g.result([{"path": "tools/bench/prep_c162_a2_1_pinsweep.py", "md5": IC.md5(os.path.abspath(__file__))}]), flush=True)
sys.exit(1 if g.failed else 0)
