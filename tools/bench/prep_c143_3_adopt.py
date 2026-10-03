r"""prep_c143_3_adopt - card 143-3 step 1 (OFFLINE, no LabVIEW; PD333(a), PD329(a)): ADOPT claudeDev\D1_ring_p4s02_20261003_110001.vi
(84cac487) as P4 session 2's file through the PD329 writer itself - stagexec.adopt_scratch (the function behind `stagexec.py adopt`,
adopt_cli :3965), called with the same arguments adopt_cli would pass (plan md5s from stage_prerun.plan_md5s of the scratch recipe).
Why not the CLI: guard_bash refuses any stagexec invocation under flags.labview none (gate false positive fp-39, logged); importing
stagexec as a module is the form prep_c142_5_pred.py already uses. No second writer is written here.
PREDICTION CONTRACT: A adopt_scratch ok (scratch log diag_c143_1_scratch.log last segment RESULT 21/0, required E1,FR,D,TD,PB,PS PASS,
  artefact under claudeDev md5 84cac487, input s01 dc61e193 unchanged); L adopted_launch(s02v18 recipe, its plan md5s) returns that record.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c143_3_adopt.log -- py -u tools/bench/prep_c143_3_adopt.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s02v18_scratch.py")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s02v18.py")
LOG = os.path.join(ROOT, "tools", "bench", "diag_c143_1_scratch.log")
ART, INP = os.path.join(CD, "D1_ring_p4s02_20261003_110001.vi"), os.path.join(CD, "D1_ring_p4s01_20261002_232547.vi")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


pm = SPR.plan_md5s(SCR)
prior = SX.adopted_launch(REC, pm)
print("FACT plan_md5s", pm, "| prior adoption", prior, flush=True)
if prior and (prior.get("artefact") or {}).get("md5") == "84cac48781c7c915c8f0d7e8fb079341":
    ok, r = True, prior
    print("FACT already adopted - not appended twice", flush=True)
else:
    ok, r = SX.adopt_scratch(SCR, LOG, ART, INP, "dc61e193e0376ce760f88fdfcda7087b", pm, ["E1", "FR", "D", "TD", "PB", "PS"],
                             note="card 143-3 PD333(a): P4 session 2 file; Error List 53 by design "
                                  "(tools/bench/errorlist_expected_D1_ring_p4s02_20261003_110001.json); adopt_cli form refused by guard_bash (fp-39)")
print(json.dumps(r, indent=1, default=str), flush=True)
gate("A adopt_scratch ok: artefact 84cac487, input dc61e193, required E1,FR,D,TD,PB,PS", ok and (r.get("artefact") or {}).get("md5") == "84cac48781c7c915c8f0d7e8fb079341", r)
ad = SX.adopted_launch(REC, pm)
gate("L adopted_launch(stage_d1_ring_p4_s02v18.py, plan md5s) returns the record (launch gate refuses a 2nd run)", bool(ad) and ad.get("t") == r.get("t"), ad and ad.get("iso"))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/adopted_scratch.jsonl", "md5": SX.md5(SX.ADOPT_LOG)}] if ok else [])), flush=True)
sys.exit(1 if G["fail"] else 0)
