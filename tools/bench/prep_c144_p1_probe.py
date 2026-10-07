# ---
# labview: none
# hardware: none
# ---
r"""prep_c144_p1_probe - card 144-P1 (OFFLINE, read-only, no LabVIEW). COPIED from prep_c143_p1_probe.py (s02 -> s03v18, op 58 -> 78).
Reads plan_ring_p4_s03v18.json's finalized block and its END step state's sym/neg, the real-graph base's sym (if any), and lists the `new:`
symbols referenced by v18 actions after op 78 with the session that creates them (s01 / s02 / s03 / later); prints ops 75..115 and the PS1/SQ1
actions. PREDICTION CONTRACT: P1 inputs on the card md5; P2 s03v18 last step file has a state with 'sym'; facts printed only.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c144_p1_probe.log -- py -u tools/bench/prep_c144_p1_probe.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                     # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V18, S03, S02, S01 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s03v18.json", "plan_ring_p4_s02v18.json", "plan_ring_p4_s01.json"))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


gate("P1 inputs on the card md5", md5(V18) == "2ea6cafa7d368dc7a054346d398daa3e" and md5(S03) == "da66a0300851133d93881be3c28f2fdc", (md5(V18), md5(S03)))
s03, v18, s02, s01 = J(S03), J(V18), J(S02), J(S01)
fz = s03.get("finalized") or {}
sf = fz.get("step_files") or []
print("FACT step_files", len(sf), "first", sf[:1], "last", sf[-1:], "| on-disk md5 last", sf and md5(os.path.join(ROOT, sf[-1]["path"])), flush=True)
last = J(sf[-1]["path"]) if sf else {}
st = last.get("state") or {}
gate("P2 last step file has a state with sym", "sym" in st, sorted(last)[:20])
print("FACT END state keys", sorted(st), flush=True)
print("FACT END sym", json.dumps(st.get("sym")), "| neg", st.get("neg"), "| vi", st.get("vi"), "| md5", st.get("md5"), flush=True)
st0 = J(sf[0]["path"])["state"]
print("FACT step0 sym", json.dumps(st0.get("sym")), "| neg", st0.get("neg"), flush=True)
bse = J(fz["base"]["path"])
print("FACT real base keys", sorted(bse), "| sym", json.dumps(bse.get("sym"))[:1500], "| vi", bse.get("vi"), "| md5", bse.get("md5"), flush=True)
print("FACT s03 actions refs to known uids (first 3)", json.dumps(s03["actions"][:3])[:1500], flush=True)
A = v18["actions"]
OPS = SX.compile_plan(v18)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
maker = {}
for n, a in enumerate(A, 1):
    if a.get("as"):
        maker["new:" + a["as"]] = (act2op[n], a["id"])
ids = [a["id"] for a in A]
prev = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
S3N = max(act2op[n] for n in range(1, len(prev) + 1))
print("FACT v18 actions", len(A), "ops", len(OPS), "| s01+s02+s03 ids", len(prev), "== v18 prefix", ids[:len(prev)] == prev, "| last op of s03", S3N, flush=True)
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
refs = collections.defaultdict(set)
for n, a in enumerate(A, 1):
    if act2op[n] <= S3N:
        continue
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if isinstance(s, str) and s.startswith("new:"):
            root = s.split(".")[0]
            m = maker.get(root) or maker.get(root[:-1])
            refs["s01" if m and m[0] <= 24 else "s02" if m and m[0] <= 58 else "s03" if m and m[0] <= S3N else "later" if m else "unknown"].add((root, m and m[0], a["id"], f))
for k in sorted(refs):
    print("FACT refs from ops>{0} to symbols made in".format(S3N), k, len(refs[k]), sorted(refs[k], key=str)[:60], flush=True)
for k in range(S3N - 3, min(len(OPS), S3N + 40) + 1):
    o = OPS[k - 1]
    print("OP {0} {1} acts {2}".format(k, o["kind"], [A[n - 1]["id"] for n in o["acts"]]), flush=True)
for i in ("p4_s1_pickslot", "p4_s2_seqcheck"):
    if i in ids:
        print("FACT subVI action", i, "op", act2op[ids.index(i) + 1], json.dumps(A[ids.index(i)])[:800], flush=True)
print("FACT kinds of ops {0}..".format(S3N + 1), dict(collections.Counter(o["kind"] for o in OPS[S3N:])), "BIND_KINDS", sorted(SX.BIND_KINDS), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
