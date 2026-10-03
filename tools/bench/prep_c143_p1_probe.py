r"""prep_c143_p1_probe - card 143-P1 (OFFLINE, read-only, no LabVIEW). Reads plan_ring_p4_s02v18.json's finalized block (base, rebase,
step_files) and the END step state's sym/neg, and lists the `new:` symbols referenced by v18 actions after op 58 with the session that
creates them (s01 / s02 / later). PREDICTION CONTRACT: P1 inputs on the card md5; P2 s02v18 has step_files and its last file has a
state with 'sym'; facts printed only.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c143_p1_probe.log -- py -u tools/bench/prep_c143_p1_probe.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                     # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V18, S02, S01 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s02v18.json", "plan_ring_p4_s01.json"))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


gate("P1 inputs on the card md5", md5(V18) == "2ea6cafa7d368dc7a054346d398daa3e" and md5(S02) == "e941ebbfaa3d98099bcd10d8c6237ef4", (md5(V18), md5(S02)))
s02, v18, s01 = J(S02), J(V18), J(S01)
fz = s02.get("finalized") or {}
print("FACT s02 top keys", sorted(s02), "| finalized keys", sorted(fz), flush=True)
print("FACT s02 base", json.dumps(s02.get("base")), "| fz.base", json.dumps(fz.get("base")), flush=True)
print("FACT s02 fz.rebase", json.dumps(fz.get("rebase"), default=str)[:3000], flush=True)
sf = fz.get("step_files") or []
print("FACT step_files", len(sf), "first", sf[:1], "last", sf[-1:], flush=True)
last = J(sf[-1]["path"]) if sf else {}
st = last.get("state") or {}
gate("P2 last step file has a state with sym", "sym" in st, sorted(last)[:20])
print("FACT END state keys", sorted(st), flush=True)
print("FACT END sym", json.dumps(st.get("sym")), "| neg", st.get("neg"), "| vi", st.get("vi"), "| md5", st.get("md5"), flush=True)
print("FACT summary", json.dumps(fz.get("summary")), flush=True)
A = v18["actions"]
OPS = SX.compile_plan(v18)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
maker = {}
for n, a in enumerate(A, 1):
    if a.get("as"):
        maker["new:" + a["as"]] = (act2op[n], a["id"])
print("FACT v18 actions", len(A), "ops", len(OPS), flush=True)
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
refs = collections.defaultdict(set)
for n, a in enumerate(A, 1):
    if act2op[n] <= 58:
        continue
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if isinstance(s, str) and s.startswith("new:"):
            root = s.split(".")[0]
            m = maker.get(root) or maker.get(root[:-1])
            refs["s01" if m and m[0] <= 24 else "s02" if m and m[0] <= 58 else "later" if m else "unknown"].add((root, m and m[0]))
for k in sorted(refs):
    print("FACT refs from ops>58 to symbols made in", k, len(refs[k]), sorted(refs[k], key=str)[:40], flush=True)
for k in range(55, min(len(OPS), 100) + 1):
    o = OPS[k - 1]
    print("OP {0} {1} acts {2}".format(k, o["kind"], [A[n - 1]["id"] for n in o["acts"]]), flush=True)
print("FACT kinds of ops 59..", dict(collections.Counter(o["kind"] for o in OPS[58:])), "BIND_KINDS", sorted(SX.BIND_KINDS), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
