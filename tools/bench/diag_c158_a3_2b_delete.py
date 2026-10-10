# ---
# labview: none
# hardware: none
# ---
r"""diag_c158_a3_2b_delete - card 158-a3-2b (OFFLINE, no LabVIEW; PD380(d), PD381(e), brief_158-a3-2.md item 6): AFTER the P5-2 step-1 file is
adopted (last adopt/1 record = claudeDev\D1_ring_p5s02a_20261010_023239.vi 94ffff94), delete the failed work copy
claudeDev\D1_ring_p5s02a_20261009_152721.vi (md5 verified == cac5236b first) and its resume record
tools/bench/resume/resume_plan_ring_p5s02a_20261009_153334.json (the only file under tools/bench/resume naming 152721). Nothing else is deleted.
PREDICTION: A adopted record present; M failed copy md5 cac5236b; R resume record names 152721; both deleted; X adopted file + P5-1 7f2582ae untouched.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c158_a3_2b_delete.log -- py -u tools/bench/diag_c158_a3_2b_delete.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
FAILED = os.path.join(CD, "D1_ring_p5s02a_20261009_152721.vi")
ADOPTED = os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
P51 = os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi")
RESD = os.path.join(ROOT, "tools", "bench", "resume")
RES = os.path.join(RESD, "resume_plan_ring_p5s02a_20261009_153334.json")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)
    return ok


rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
ok = gate("A last adopt/1 record = the P5-2a file 94ffff94", os.path.normcase((rec.get("artefact") or {}).get("path") or "") == os.path.normcase(ADOPTED)
          and (rec.get("artefact") or {}).get("md5", "").startswith("94ffff94") and SX.md5(ADOPTED).startswith("94ffff94"), rec.get("artefact"))
named = [f for f in sorted(os.listdir(RESD)) if "152721" in open(os.path.join(RESD, f), encoding="utf-8", errors="replace").read()]
ok = gate("R the resume records naming 152721 == [the one record]", named == [os.path.basename(RES)], named) and ok
ok = gate("M failed copy exists, md5 cac5236b", os.path.isfile(FAILED) and SX.md5(FAILED).startswith("cac5236b"),
          SX.md5(FAILED) if os.path.isfile(FAILED) else "missing") and ok
if ok:
    os.remove(FAILED)
    os.remove(RES)
gate("D both deleted", not os.path.exists(FAILED) and not os.path.exists(RES), (os.path.exists(FAILED), os.path.exists(RES)))
gate("X adopted 94ffff94 and P5-1 7f2582ae untouched", SX.md5(ADOPTED).startswith("94ffff94") and SX.md5(P51).startswith("7f2582ae"),
     (SX.md5(ADOPTED), SX.md5(P51)))
print("FACT deleted {0} and {1}".format(FAILED, os.path.relpath(RES, ROOT)) if ok else "FACT nothing deleted", flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
