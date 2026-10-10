# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_165-3-4.json
# ---
r"""diag_c165_a3_4_adopt - card 165-3-4 (OFFLINE, no LabVIEW; PD354(a), PD396(e), PD400(c)): ADOPT the PASSED P5-2 step-5 scratch work copy
claudeDev\D1_ring_p5s02e_<stamp>.vi (diag_c165_p5s02e_scratch_sum.json `final`/`final_md5`) through stagexec.adopt_scratch CALLED BY IMPORT.
COPY of tools/bench/diag_c164_a3_5_adopt.py (card 164-3-5, ran 3/0); changed lines: recipe / scratch recipe p5s02d -> p5s02e, log / sum
c164 p5s02d -> c165 p5s02e, input 564d8cbe -> p5s02d 6dcd5c3d, labels and note; NEW (brief_165-3-4.md delta 7, PD400(c)): when argv[2] == 'final'
(the run reached the plan's last checkpoint) a BYTE COPY claudeDev\D1_ring_p5_<same stamp>.vi is made (shutil.copyfile, md5 == the scratch file,
both kept) and THAT copy is the adopted artefact; otherwise the p5s02e file is adopted under its own name.
PREDICTION CONTRACT: S sum final is claudeDev\D1_ring_p5s02e_<stamp>.vi, md5 == file, != input 6dcd5c3d; C (final) copy md5 == scratch md5;
  A adopt_scratch ok (required gates PASS, input 6dcd5c3d unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c165_a3_4_adopt.log -- py -u tools/bench/diag_c165_a3_4_adopt.py <REQ> final"""
import json, os, shutil, sys                                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02e_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02e.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c165_p5s02e_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c165_p5s02e_scratch_sum.json"), encoding="utf-8"))
ART, ARTM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi"), "6dcd5c3d506f69947a5ce259ccbe2221"
REQ = (sys.argv[1] if len(sys.argv) > 1 else "E1,FR,D,TD,PB,PS").split(",")
FINAL = len(sys.argv) > 2 and sys.argv[2] == "final"
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


print("FACT sum card {0} rc {1} peak {2} x10 {3}; required {4}; final {5}".format(SUM.get("card"), SUM.get("rc"), SUM.get("peak_mb"), SUM.get("x10"),
      REQ, FINAL), flush=True)
gate("S sum final is claudeDev\\D1_ring_p5s02e_<stamp>.vi, md5 == file, != input 6dcd5c3d",
     bool(ART) and os.path.normcase(os.path.dirname(os.path.abspath(ART))) == os.path.normcase(CD)
     and os.path.basename(ART).startswith("D1_ring_p5s02e_") and SX.md5(ART) == ARTM and ARTM != INPM, (ART, ARTM))
ADV = ART
if FINAL and not G["fail"]:
    ADV = os.path.join(CD, os.path.basename(ART).replace("D1_ring_p5s02e_", "D1_ring_p5_", 1))
    if not os.path.exists(ADV):
        shutil.copyfile(ART, ADV)
    gate("C byte copy {0} md5 == scratch file md5 {1}; scratch file kept".format(os.path.basename(ADV), ARTM),
         SX.md5(ADV) == ARTM and SX.md5(ART) == ARTM, (SX.md5(ADV), SX.md5(ART)))
pm = SPR.plan_md5s(SCR)
prior = SX.adopted_launch(REC, pm)
print("FACT plan_md5s", pm, "| prior adoption", prior, flush=True)
if G["fail"]:
    ok, r = False, {}
elif prior and (prior.get("artefact") or {}).get("md5") == ARTM:
    ok, r = True, prior
    print("FACT already adopted - not appended twice", flush=True)
else:
    ok, r = SX.adopt_scratch(SCR, LOG, ADV, INP, INPM, pm, REQ,
                             note="card 165-3-4 PD354(a)/PD396(e)/PD400(c): P5-2 step-5 file = the ONE scratch work copy {0} (9 ops on "
                                  "plan_ring_p5s02e.json fd23974e, stagexec 1d5309f4, stagekit dd57c1ca){1}".format(
                                      os.path.basename(ART), "; reached the last checkpoint -> adopted as the byte copy {0} (P5 final, "
                                      "broken file 6 of 6), md5 equal, both kept".format(os.path.basename(ADV)) if ADV != ART else ""))
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == sum final_md5, input 6dcd5c3d, required " + ",".join(REQ), ok and (r.get("artefact") or {}).get("md5") == ARTM
     if isinstance(r, dict) else False, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p5s02e.py, plan md5s) returns the record (launch gate refuses a 2nd run)",
     bool(ad) and isinstance(r, dict) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print("FACT adopted {0} md5 {1}; scratch file {2} md5 {3}; input {4} md5 {5}".format(ADV, SX.md5(ADV), ART, SX.md5(ART), INP, SX.md5(INP)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
