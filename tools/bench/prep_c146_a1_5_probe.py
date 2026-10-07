# ---
# labview: none
# hardware: none
# ---
r"""prep_c146_a1_5_probe - card 146-a1-5 (OFFLINE, read-only). Prints the shape of the rebased s05 plan (1fc9b486), its sim END state,
the s04 creation map header and the v18 ops 115..150 symbols referenced, so the s06 maker can be a copy-edit of prep_c146_a1_3_mk.py.
PREDICTION CONTRACT: reads only; prints FACT lines; writes nothing.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c146_a1_5_probe.log -- py -u tools/bench/prep_c146_a1_5_probe.py"""
import json, os, sys, collections                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                 # noqa: E401,E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
B = os.path.join(ROOT, "tools", "bench")
p = J(os.path.join(B, "plan_ring_p4_s05v18.json"))
print("FACT s05 keys", list(p.keys()))
print("FACT s05 base", p.get("base"))
fz = p["finalized"]
print("FACT fz keys", list(fz.keys()))
print("FACT fz base", fz.get("base"))
print("FACT step first/last", fz["step_files"][0], fz["step_files"][-1], len(fz["step_files"]))
print("FACT rebase", str(fz.get("rebase"))[:2500])
print("FACT open_rows", len(p.get("open_rows") or []), json.dumps(p.get("open_rows"))[:2500])
e = J(fz["step_files"][-1]["path"])["state"]
print("FACT END5 keys", list(e.keys()))
print("FACT END5 sym", e.get("sym"), "neg", e.get("neg"), "md5", e.get("md5"), "vi", e.get("vi"))
s0 = J(fz["step_files"][0]["path"])["state"]
print("FACT S0 sym", s0.get("sym"), "neg", s0.get("neg"), "md5", s0.get("md5"))
for f in sorted(os.listdir(os.path.join(B, "creation_map"))):
    if "p4_s0" in f:
        hd, cm, st = SPR.read_creation_map(os.path.join(B, "creation_map", f))
        print("FACT CM", f, "header", hd, "sizes", dict((k, len(v)) for k, v in cm.items()))
s04 = J(os.path.join(B, "plan_ring_p4_s04v18.json"))
print("FACT s04 base", s04.get("base"), "fz base", (s04.get("finalized") or {}).get("base"), "last step", s04["finalized"]["step_files"][-1])
v18 = J(os.path.join(B, "plan_ring_p4_v18.json"))
A, OPS = v18["actions"], SX.compile_plan(v18)
ids = [a["id"] for a in A]
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
print("FACT v18 actions", len(A), "ops", len(OPS))
made = {}
for a in A:
    if a.get("as"):
        made["new:" + a["as"]] = act2op[ids.index(a["id"]) + 1]
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
refs = collections.defaultdict(list)
for k in range(115, min(len(OPS), 150) + 1):
    for n in OPS[k - 1]["acts"]:
        a = A[n - 1]
        for f in UIDF + ADDRF:
            y = a.get(f)
            s = y.get("uid") if isinstance(y, dict) else y
            if isinstance(s, str) and s.startswith("new:"):
                root = s.split(".")[0]
                mo = made.get(root) or made.get(root[:-1])
                refs[(root, mo)].append((k, a["id"], f))
for (r, mo), v in sorted(refs.items(), key=lambda x: (x[0][1] or 0)):
    print("FACT REF", r, "made at op", mo, "used", v[:4], len(v))
for k in range(115, 141):
    o = OPS[k - 1]
    print("FACT OP", k, o["kind"], [A[n - 1]["id"] for n in o["acts"]], [A[n - 1].get("of") for n in o["acts"]])
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
