# ---
# labview: read
# hardware: none
# ---
r"""diag_c154_a3_3_adopt - card 154-a3-3 (OFFLINE, no LabVIEW; PD329(a), PD354(a), PD374(e)(f), PD376): ADOPT the P5-1a scratch's saved
work copy claudeDev\D1_ring_p5s01a_<stamp>.vi (path + md5 from diag_c154_p5s01a_scratch_sum.json `final`/`final_md5`) as P5-1a's in-between file
through stagexec.adopt_scratch CALLED BY IMPORT (the CLI form is refused, fp-39). COPIED from tools/bench/diag_c152_b3_1_adopt.py (2b452095,
card 152-b3-1, ran 3/0) with only the card id / names / note changed (s09 -> P5-1a, input s08 f99e8414 -> s09 eb1d0f31): lines 5-13, 21-26,
36-38, 49-50, 52, 54.
adopt_scratch reads the scratch log's LAST segment (stagexec rfind('BGRUN START')), i.e. this card's run.
PREDICTION CONTRACT: S sum final under claudeDev, md5 == file, != eb1d0f31; A adopt_scratch ok (required E1,FR,D,TD,PB,PS PASS, input s09
  eb1d0f31 unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c154_a3_3_adopt.log -- py -u tools/bench/diag_c154_a3_3_adopt.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c154_p5s01a_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c154_p5s01a_scratch_sum.json"), encoding="utf-8"))
ART, ARTM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"), "eb1d0f3107bbba49c9ae67a47c0ee50f"
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


gate("S sum final is under claudeDev, named D1_ring_p5s01a_*, md5 == file, not the input eb1d0f31",
     bool(ART) and os.path.dirname(os.path.abspath(ART)).lower() == CD.lower() and os.path.basename(ART).startswith("D1_ring_p5s01a_")
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
                             note="card 154-a3-3 PD329(a)/PD354(a)/PD374(e)(f)/PD376: P5-1a in-between file, ONE scratch structural PASS "
                                  "(20 actions, 14 ops, 0 sink gates); adopt_cli form refused (fp-39)")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == scratch final, input eb1d0f31, required E1,FR,D,TD,PB,PS", ok and (r.get("artefact") or {}).get("md5") == ARTM, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p5s01a.py, plan md5s) returns the record (launch gate refuses a 2nd run)", bool(ad) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
