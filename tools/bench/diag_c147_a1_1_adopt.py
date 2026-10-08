# ---
# labview: read
# hardware: none
# ---
r"""diag_c147_a1_1_adopt - card 147-a1-1 step 2 (OFFLINE, no LabVIEW; PD354(c), PD353(d), PD329(a)): ADOPT the s05v18 scratch's saved work copy
claudeDev\D1_ring_p4s05_20261008_002621.vi (path + md5 from diag_c145_p4s05v18_scratch_sum.json `final`/`final_md5`) as P4 session 5's file through
stagexec.adopt_scratch CALLED BY IMPORT (the CLI form is refused, fp-39). Nothing copied or renamed (stagexec.py:4027: the work copy IS the stage file).
COPIED from tools/bench/diag_c146_a1_4_adopt.py (md5 7e476ab9, card input) with ONLY the card id / note changed; the header keeps `labview: read`
as the copied file does (stagexec import), no LabVIEW is started.
PREDICTION CONTRACT: S sum final under claudeDev, md5 3f9ac26b == file; A adopt_scratch ok (scratch log diag_c145_p4s05v18_scratch.log last
  segment, required E1,FR,D,TD,PB,PS PASS, input s04 95e408ff unchanged); L adopted_launch returns it.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c147_a1_1_adopt.log -- py -u tools/bench/diag_c147_a1_1_adopt.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s05v18_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s05v18.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c145_p4s05v18_scratch.log")
SUM = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c145_p4s05v18_scratch_sum.json"), encoding="utf-8"))
ART, ARTM = SUM["final"], SUM["final_md5"]
INP, INPM = os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"), "95e408ff14a406edd3f16b32ba7324f1"
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


gate("S sum final is under claudeDev, md5 == file == 3f9ac26b", bool(ART) and os.path.dirname(os.path.abspath(ART)).lower() == CD.lower()
     and SX.md5(ART) == ARTM == "3f9ac26b69179eb53c202d90407ce7ee", (ART, ARTM))
pm = SPR.plan_md5s(SCR)
prior = SX.adopted_launch(REC, pm)
print("FACT plan_md5s", pm, "| prior adoption", prior, flush=True)
if prior and (prior.get("artefact") or {}).get("md5") == ARTM:
    ok, r = True, prior
    print("FACT already adopted - not appended twice", flush=True)
else:
    ok, r = SX.adopt_scratch(SCR, LOG, ART, INP, INPM, pm, ["E1", "FR", "D", "TD", "PB", "PS"],
                             note="card 147-a1-1 PD354(c)/PD353(d): P4 session 5 file, adopted without a rerun; Error List measured by "
                                  "errorlist_check --role final (tools/bench/diag_c147_a1_1_el.log); adopt_cli form refused (fp-39)")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact md5 == scratch final, input 95e408ff, required E1,FR,D,TD,PB,PS", ok and (r.get("artefact") or {}).get("md5") == ARTM, r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p4_s05v18.py, plan md5s) returns the record (launch gate refuses a 2nd run)", bool(ad) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
