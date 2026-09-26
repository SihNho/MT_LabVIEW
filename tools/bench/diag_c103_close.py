r"""diag_c103_close - card 103-1 P6 close-out, READ-ONLY, no LabVIEW: md5 of every artefact, the S1 input's md5 against the
plan's pinned base md5 (3e3d23ce...), the Wait donor against its registry pin, OpWaitDonor_cand* scratch copies gone, no
D1_s1_dispA_* file (no stage run in this card), LabVIEW not running.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c103_close.log -- py -u tools/bench/diag_c103_close.py"""
import glob, hashlib, json, os, subprocess, sys                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                               # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                      # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)


plan = json.load(open(os.path.join(HERE, "sim", "disp", "plan_disp.json"), encoding="utf-8"))
base = json.load(open(os.path.join(ROOT, plan["finalized"]["base"]["path"]), encoding="utf-8"))
reg = json.load(open(os.path.join(HERE, "facts_c100_oplabels.json"), encoding="utf-8"))["OpPrimCopyNested_v0"]["donors"]["Wait (ms)"]
s1 = os.path.join(CD, "D1_s1_copy.vi")
gate("C1 D1_s1_copy.vi md5 == the plan's pinned base md5", md5(s1) == base["md5"], (md5(s1), base["md5"]))
gate("C2 OpWaitDonor_v0.vi md5 == its registry pin", md5(reg["donor"]) == reg["md5"], (md5(reg["donor"]), reg))
gate("C3 no OpWaitDonor_cand* scratch left; no D1_s1_dispA_* file (no stage run in this card)",
     not glob.glob(os.path.join(CD, "OpWaitDonor_cand*")) and not glob.glob(os.path.join(CD, "D1_s1_dispA_*")),
     glob.glob(os.path.join(CD, "OpWaitDonor_*")))
gate("C4 LabVIEW not running", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
arts = []
for p in ("tools/bench/cards/split_plan_103.md", "tools/bench/facts_c103_donor.json", "tools/bench/facts_c100_oplabels.json",
          "tools/bench/sim/disp/plan_disp.json", "tools/bench/sim/disp/stageplan_disp_r4_open.json", "tools/stagexec.py",
          "tools/stage_prerun.py", "tools/recipes/stage_d1_disp.py", reg["donor"]):
    ap = p if os.path.isabs(p) else os.path.join(ROOT, p)
    arts.append({"path": p, "md5": md5(ap)})
    print("  FACT md5 {0}  {1}".format(md5(ap), p), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((l for l, ok in gates if not ok), None)
print(P.result_line(P.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
