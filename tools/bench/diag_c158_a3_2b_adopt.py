# ---
# labview: read
# hardware: none
# ---
r"""diag_c158_a3_2b_adopt - card 158-a3-2b (OFFLINE, no LabVIEW; PD354(a), PD386(e)): ADOPT the PASSED P5-2 step-1 scratch work copy
claudeDev\D1_ring_p5s02a_<stamp>.vi (diag_c158_p5s02a_scratch_sum.json `final`/`final_md5`, written by this card's ONE scratch run) through
stagexec.adopt_scratch CALLED BY IMPORT. The saved file IS the adopted name - no copy, no rename.
COPY of tools/bench/diag_c158_a2_2_adopt.py (card 158-a2-2, unused there) with ONLY the log / sum names (c156 -> c158 retry log, lines 23-24)
and the note text (lines 52-53) changed. adopt_scratch reads the scratch log's LAST segment (stagexec.py:4310), i.e. this card's run.
PREDICTION CONTRACT: S sum final is claudeDev\D1_ring_p5s02a_<stamp>.vi, not the failed copy 152721, md5 == file, != input 7f2582ae;
  A adopt_scratch ok (required E1,FR,D,TD,PB,PS PASS, input 7f2582ae unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c158_a3_2b_adopt.log -- py -u tools/bench/diag_c158_a3_2b_adopt.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02a_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02a.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c158_p5s02a_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c158_p5s02a_scratch_sum.json"), encoding="utf-8"))
ART, ARTM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"), "7f2582ae54dc5bc42c3df0bdf3c72d2e"
FAILED = os.path.join(CD, "D1_ring_p5s02a_20261009_152721.vi")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


print("FACT sum card {0} rc {1} peak {2} x10 {3}".format(SUM.get("card"), SUM.get("rc"), SUM.get("peak_mb"), SUM.get("x10")), flush=True)
gate("S sum final is claudeDev\\D1_ring_p5s02a_<stamp>.vi (not the failed 152721 copy), md5 == file, != input 7f2582ae",
     bool(ART) and os.path.normcase(os.path.dirname(os.path.abspath(ART))) == os.path.normcase(CD)
     and os.path.basename(ART).startswith("D1_ring_p5s02a_") and os.path.normcase(os.path.abspath(ART)) != os.path.normcase(FAILED)
     and SX.md5(ART) == ARTM and ARTM != INPM, (ART, ARTM))
pm = SPR.plan_md5s(SCR)
prior = SX.adopted_launch(REC, pm)
print("FACT plan_md5s", pm, "| prior adoption", prior, flush=True)
if G["fail"]:
    ok, r = False, {}
elif prior and (prior.get("artefact") or {}).get("md5") == ARTM:
    ok, r = True, prior
    print("FACT already adopted - not appended twice", flush=True)
else:
    ok, r = SX.adopt_scratch(SCR, LOG, ART, INP, INPM, pm, ["E1", "FR", "D", "TD", "PB", "PS"],
                             note="card 158-a3-2b PD354(a)/PD379/PD386(e): P5-2 step-1 in-between file = the ONE retry scratch work copy "
                                  "(17 ops, actions 1..23, connect_term_uid on ops 16/17, stagexec 7a712ccb, stagekit 07f9e35f); saved name is the adopted name")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == sum final_md5, input 7f2582ae, required E1,FR,D,TD,PB,PS", ok and (r.get("artefact") or {}).get("md5") == ARTM
     if isinstance(r, dict) else False, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p5s02a.py, plan md5s) returns the record (launch gate refuses a 2nd run)",
     bool(ad) and isinstance(r, dict) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print("FACT adopted {0} md5 {1}; input {2} md5 {3}".format(ART, ARTM, INP, SX.md5(INP)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
