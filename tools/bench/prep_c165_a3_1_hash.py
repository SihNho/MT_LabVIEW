# ---
# labview: none
# hardware: none
# offline-args: pre
# evidence: tools/bench/cards/brief_165-3-1.md
# ---
r"""prep_c165_a3_1_hash - card 165-3-1 step 1 (OFFLINE, file reads only): md5 of every card input (pins from task_165-3-1.json) plus the VI
claudeDev\D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d (bytes only, never opened), plus the untouched-set (hooks digest, plan doc, memory_model).
Arg 'pre' writes tools/bench/prep_c165_a3_1_hash_pre.json; arg 'post' compares the untouched-set against it (stagexec is EXPECTED to differ post).
PREDICTION (pre): every card pin equal, VI 6dcd5c3d -> 17 PASS / 0 FAIL. (post): untouched-set equal to pre, stagexec differs.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c165_a3_1_hash.log -- py -u tools/bench/prep_c165_a3_1_hash.py pre"""
import glob, json, os, sys                                                                    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_c156_a1_1_lib as L                                                               # noqa: E402
ROOT, md5, J = L.ROOT, L.md5, L.J
MODE = (sys.argv[1:] or ["pre"])[0]
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
VI = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi")
SNAP = os.path.join(B, "prep_c165_a3_1_hash_pre.json")
EXPECT_CHANGED = {"tools/stagexec.py", "tools/bench/selftest_c165_innerface.py"}   # the second: --pre option added (B0-B2 vs 6ea6637f)


def untouched():
    """Return {relpath: md5} of the files this card must not change (card inputs except outputs, hooks, plan doc, memory model, VI)."""
    d = {i["path"]: md5(os.path.join(ROOT, i["path"])) for i in J("tools/bench/cards/task_165-3-1.json")["inputs"]}
    for p in sorted(glob.glob(os.path.join(ROOT, "tools", "hooks", "*.py"))) + [os.path.join(ROOT, "tools", "bench", "memory_model.json")]:
        d[os.path.relpath(p, ROOT).replace("\\", "/")] = md5(p)
    d["VI:" + os.path.basename(VI)] = md5(VI)
    return d


gate = L.Gate(fatal_default=False)
if MODE == "arts":                                     # md5 of this card's output files, for the result file
    for p in ("tools/stagexec.py", "tools/bench/selftest_c165_prime.py", "tools/bench/selftest_c165_innerface.py", "tools/bench/diag_c165_a3_1_facts.md",
              "tools/bench/selftest_c165_prime.log", "tools/bench/prep_c165_a3_1_hash.py"):
        print("ART", md5(os.path.join(ROOT, p)), p)
    sys.exit(gate.result())
if MODE == "pre":
    for i in J("tools/bench/cards/task_165-3-1.json")["inputs"]:
        h = md5(os.path.join(ROOT, i["path"]))
        gate("M {0} md5 {1} == pin {2}".format(i["path"], h, i["md5"][:8]), h == i["md5"], h)
    h = md5(VI)
    gate("M VI {0} md5 {1} == 6dcd5c3d".format(os.path.basename(VI), h), h.startswith("6dcd5c3d"), h)
    json.dump(untouched(), open(SNAP, "w", encoding="utf-8"), indent=1)
    print("SNAP", SNAP, md5(SNAP))
    PRE = os.path.join(os.environ["TEMP"], "c165_a3_1", "stagexec_pre.py")     # pre-change copy for the byte-equal checks
    if not os.path.exists(PRE) and md5(os.path.join(ROOT, "tools", "stagexec.py")).startswith("6ea6637f"):
        os.makedirs(os.path.dirname(PRE), exist_ok=True)
        open(PRE, "wb").write(open(os.path.join(ROOT, "tools", "stagexec.py"), "rb").read())
    gate("P pre-change copy {0} md5 {1} == 6ea6637f".format(PRE, md5(PRE)), md5(PRE).startswith("6ea6637f"), PRE)
else:
    pre, now = J(SNAP), untouched()
    for k in sorted(pre):
        same = pre[k] == now.get(k)
        if k in EXPECT_CHANGED:
            gate("C {0} {1} -> {2} (changed by this card)".format(k, pre[k][:8], now[k][:8]), not same, now[k])
        else:
            gate("U {0} {1} UNCHANGED".format(k, now.get(k, "")[:8]), same, now.get(k))
sys.exit(gate.result())
