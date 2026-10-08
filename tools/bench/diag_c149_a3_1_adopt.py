# ---
# labview: read
# hardware: none
# ---
r"""diag_c149_a3_1_adopt - card 149-a3-1 (OFFLINE, no LabVIEW; PD329(a), PD354(a), PD358(e), PD363(b)): ADOPT the s06v18 scratch's saved work copy
claudeDev\D1_ring_p4s06_<stamp>.vi (path + md5 from diag_c147_p4s06v18_scratch_sum.json `final`/`final_md5`) as P4 session 6's file through
stagexec.adopt_scratch CALLED BY IMPORT (the CLI form is refused, fp-39). COPIED from tools/bench/diag_c149_a1_2_adopt.py (card 149-a1-2, unrun)
with only the card id / note changed. adopt_scratch reads the scratch log's LAST segment (stagexec rfind('BGRUN START')), i.e. card 148-a2-4's run.
PREDICTION CONTRACT: S sum final under claudeDev, md5 == file, != b58046e3; A adopt_scratch ok (required E1,FR,D,TD,PB,PS PASS, input s05
  3f9ac26b unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c149_a3_1_adopt.log -- py -u tools/bench/diag_c149_a3_1_adopt.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s06v18_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s06v18.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c147_p4s06v18_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c147_p4s06v18_scratch_sum.json"), encoding="utf-8"))
ART, ARTM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"), "3f9ac26b69179eb53c202d90407ce7ee"
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


gate("S sum final is under claudeDev, named D1_ring_p4s06_*, md5 == file, not 147-a1-4's stopped copy b58046e3",
     bool(ART) and os.path.dirname(os.path.abspath(ART)).lower() == CD.lower() and os.path.basename(ART).startswith("D1_ring_p4s06_")
     and SX.md5(ART) == ARTM and not ARTM.startswith("b58046e3"), (ART, ARTM))
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
                             note="card 149-a3-1 PD329(a)/PD354(a)/PD358(e)/PD363(b): P4 session 6 file, ONE scratch (card 148-a2-4, new gate API) structural PASS "
                                  "incl. sink gate SG-p4_rbA_re1; Error List recorded 51 items (tools/bench/diag_c149_a1_2_el.log), item 6 void->I32 unidentified "
                                  "(tools/bench/diag_c149_a1_3_facts.md); adopt_cli form refused (fp-39)")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == scratch final, input 3f9ac26b, required E1,FR,D,TD,PB,PS", ok and (r.get("artefact") or {}).get("md5") == ARTM, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p4_s06v18.py, plan md5s) returns the record (launch gate refuses a 2nd run)", bool(ad) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
