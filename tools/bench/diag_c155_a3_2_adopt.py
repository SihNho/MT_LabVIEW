# ---
# labview: read
# hardware: none
# ---
r"""diag_c155_a3_2_adopt - card 155-a3-2 (OFFLINE, no LabVIEW; PD354(a), PD378(c)): BYTE-COPY the PASSED P5-1b scratch work copy
claudeDev\D1_ring_p5s01b_20261009_123319.vi (7f2582ae, diag_c155_p5s01b_scratch_sum.json `final`/`final_md5`) to claudeDev\D1_ring_p5s01_<stamp>.vi
(shutil.copyfile, md5 equal; the p5s01b file is never touched) and ADOPT the copy through stagexec.adopt_scratch CALLED BY IMPORT (fp-39).
COPIED from tools/bench/diag_c154_a3_3_adopt.py (a8ad90b8, card 154-a3-3, ran 3/0) with names / ids / paths changed (P5-1a -> P5-1b; input
s09 eb1d0f31 -> P5-1a 2482fe7b; required gate list unchanged E1,FR,D,TD,PB,PS = the PASS lines of diag_c155_p5s01b_scratch.log:148-169) and the
copy step added (C1/C2): lines 5-16, 21-31, 39-46, 51-52, 57-59. The rename is an assumption of the assignment session (brief_155-a3-2.md:9).
adopt_scratch reads the scratch log's LAST segment (stagexec rfind('BGRUN START')), i.e. card 155-a3-1's run.
PREDICTION CONTRACT: S sum final == the p5s01b file, md5 7f2582ae; C1 target does not exist yet; C2 copy md5 == 7f2582ae, source md5 unchanged;
  A adopt_scratch ok (required E1,FR,D,TD,PB,PS PASS, input 2482fe7b unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c155_a3_2_adopt.log -- py -u tools/bench/diag_c155_a3_2_adopt.py"""
import json, os, shutil, sys, time                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01b_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01b.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c155_p5s01b_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c155_p5s01b_scratch_sum.json"), encoding="utf-8"))
SRC, SRCM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"), "2482fe7bf3426e18b0801c77ec629073"
ART = os.path.join(CD, "D1_ring_p5s01_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


gate("S sum final is claudeDev\\D1_ring_p5s01b_20261009_123319.vi, md5 7f2582ae == file, not the input 2482fe7b",
     os.path.normcase(os.path.abspath(SRC)) == os.path.normcase(os.path.join(CD, "D1_ring_p5s01b_20261009_123319.vi"))
     and SRCM.startswith("7f2582ae") and SX.md5(SRC) == SRCM and SRCM != INPM, (SRC, SRCM))
gate("C1 target {0} does not exist yet".format(os.path.basename(ART)), not os.path.exists(ART), ART)
if not G["fail"]:
    shutil.copyfile(SRC, ART)
ARTM = SX.md5(ART) if os.path.isfile(ART) else "MISSING"
gate("C2 byte copy md5 {0} == source {1}; source md5 unchanged; sizes equal".format(ARTM, SRCM),
     ARTM == SRCM and SX.md5(SRC) == SRCM and os.path.getsize(ART) == os.path.getsize(SRC), (ART, ARTM, os.path.getsize(SRC)))
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
                             note="card 155-a3-2 PD354(a)/PD378(c): P5-1 in-between file = byte copy of the P5-1b scratch work copy "
                                  "D1_ring_p5s01b_20261009_123319.vi (7f2582ae, card 155-a3-1 ONE scratch 20/0, 12 actions, 8 ops); "
                                  "renamed by copy (assignment-session assumption, brief_155-a3-2.md:9); adopt_cli form refused (fp-39)")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == 7f2582ae, input 2482fe7b, required E1,FR,D,TD,PB,PS", ok and (r.get("artefact") or {}).get("md5") == ARTM, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p5s01b.py, plan md5s) returns the record (launch gate refuses a 2nd run)", bool(ad) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print("FACT adopted {0} md5 {1}; source {2} md5 {3}".format(ART, ARTM, SRC, SX.md5(SRC)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
