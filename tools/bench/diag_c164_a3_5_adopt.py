# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/task_164-3-5.json
# ---
r"""diag_c164_a3_5_adopt - card 164-3-5 (OFFLINE, no LabVIEW; PD354(a), PD396(e)): ADOPT the PASSED P5-2 step-4 scratch work copy
claudeDev\D1_ring_p5s02d_<stamp>.vi (diag_c164_p5s02d_scratch_sum.json `final`/`final_md5`, written by this card's ONE scratch run) through
stagexec.adopt_scratch CALLED BY IMPORT. The saved file IS the adopted name - no copy, no rename.
COPY of tools/bench/diag_c163_a2_2_adopt.py (card 163-a2-2, ran 3/0); changed lines ONLY: recipe / scratch recipe p5s02c -> p5s02d, log / sum
c163 p5s02c -> c164 p5s02d (the recipe's own LOG constant), input f9ae7751 -> p5s02c 564d8cbe, labels and the note text.
PREDICTION CONTRACT: S sum final is claudeDev\D1_ring_p5s02d_<stamp>.vi, md5 == file, != input 564d8cbe;
  A adopt_scratch ok (required gates PASS, input 564d8cbe unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c164_a3_5_adopt.log -- py -u tools/bench/diag_c164_a3_5_adopt.py [E1,FR,...]"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02d_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02d.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c164_p5s02d_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c164_p5s02d_scratch_sum.json"), encoding="utf-8"))
ART, ARTM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"), "564d8cbec316ea95f29f49d25ba5713e"
REQ = (sys.argv[1] if len(sys.argv) > 1 else "E1,FR,D,TD,PB,PS").split(",")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


print("FACT sum card {0} rc {1} peak {2} x10 {3}; required {4}".format(SUM.get("card"), SUM.get("rc"), SUM.get("peak_mb"), SUM.get("x10"), REQ), flush=True)
gate("S sum final is claudeDev\\D1_ring_p5s02d_<stamp>.vi, md5 == file, != input 564d8cbe",
     bool(ART) and os.path.normcase(os.path.dirname(os.path.abspath(ART))) == os.path.normcase(CD)
     and os.path.basename(ART).startswith("D1_ring_p5s02d_") and SX.md5(ART) == ARTM and ARTM != INPM, (ART, ARTM))
pm = SPR.plan_md5s(SCR)
prior = SX.adopted_launch(REC, pm)
print("FACT plan_md5s", pm, "| prior adoption", prior, flush=True)
if G["fail"]:
    ok, r = False, {}
elif prior and (prior.get("artefact") or {}).get("md5") == ARTM:
    ok, r = True, prior
    print("FACT already adopted - not appended twice", flush=True)
else:
    ok, r = SX.adopt_scratch(SCR, LOG, ART, INP, INPM, pm, REQ,
                             note="card 164-3-5 PD354(a)/PD396(e): P5-2 step-4 in-between file = the ONE scratch work copy "
                                  "(15 ops on plan_ring_p5s02d.json, stagexec a4df7e15, stagekit dd57c1ca); saved name is the adopted name")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == sum final_md5, input 564d8cbe, required " + ",".join(REQ), ok and (r.get("artefact") or {}).get("md5") == ARTM
     if isinstance(r, dict) else False, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p5s02d.py, plan md5s) returns the record (launch gate refuses a 2nd run)",
     bool(ad) and isinstance(r, dict) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print("FACT adopted {0} md5 {1}; input {2} md5 {3}".format(ART, ARTM, INP, SX.md5(INP)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
