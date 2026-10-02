r"""selftest_c134_2_gates - card 134-2 (PD288(b)(c)): gate B SCOPED (stagesim.fs_border_gate) and check_launch's dry_rule == 2.
OFFLINE: no LabVIEW, no COM; records live in a %TEMP% sandbox (PRERUN_RECORDS / PRERUN_LOG_DIR / STAGE_RUNS), as
selftest_launch_gate.py does. EXISTING FIRST: stagesim.fs_measured_state (card 134-1), selftest_launch_gate.py's sandbox pattern.
PREDICTION:
  B1 the measured graph graph_ring_p3b2a_fs_20261002_102553.json lists exactly 7 UNMEASURED border tunnels (nested FS 14682)
  B2 uses = {} -> PASS (unused UNMEASURED borders do not fail)
  B3 uses = FS 27509's classified borders (tunnel uids + faces + its border entries) -> PASS
  B4 an action naming an UNMEASURED tunnel uid -> FAIL naming it; B5 a route naming one of its FACE terminals -> FAIL
  B6 a carried entry key '<face>|<frame>' -> FAIL; B7 a graph without fs_measured -> PASS, nothing listed
  D1 a dry PASS record without dry_rule (old rule) -> check_launch refused, text names PD288(c) and 'Re-dry'
  D2 the same with dry_rule 2 (write_record's default) -> allowed; D3 dry_rule 1 explicitly -> refused
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c134_2_gates.log -- py -u tools/bench/selftest_c134_2_gates.py"""
import atexit, json, os, shutil, sys, tempfile, time                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
SAND = tempfile.mkdtemp(prefix="c134_2_selftest_")
atexit.register(shutil.rmtree, SAND, True)
os.makedirs(os.path.join(SAND, "tools", "recipes"), exist_ok=True)
os.makedirs(os.path.join(SAND, "logs"), exist_ok=True)
os.environ["PRERUN_RECORDS"] = os.path.join(SAND, "records.jsonl")
os.environ["PRERUN_LOG_DIR"] = os.path.join(SAND, "logs")
os.environ["STAGE_RUNS"] = os.path.join(SAND, "stage_runs.jsonl")
os.environ["STAGE_RUNS_CYCLE"] = "cycle 902"
sys.path.insert(0, TOOLS)
import stagesim as SS, stage_prerun as SP, protocol as P     # noqa: E402,E401
G = []


def gate(label, ok, d=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:500]), flush=True)


GR = json.load(open(os.path.join(HERE, "graph_ring_p3b2a_fs_20261002_102553.json"), encoding="utf-8"))
m = SS.fs_measured_state(GR)
um = dict((u, b) for u, b in m["borders"].items() if b.get("fs") is None)
allfr = m["frame_owner"]          # card 134-2: the 7 are NESTED-FS tunnels (every face on an FS frame), not all FS 14682's
gate("B1 7 UNMEASURED border tunnels, EVERY face on a measured FS frame (nested FS), status UNMEASURED",
     len(um) == 7 and all(all(f[1] in allfr for f in b["faces"]) and b.get("status") == "UNMEASURED" for b in um.values()),
     dict((u, [(f[0], f[1], allfr.get(f[1])) for f in b["faces"]]) for u, b in sorted(um.items())))
r2 = SS.fs_border_gate(GR, {})
gate("B2 uses {} -> PASS, the 7 listed unmeasured", r2["status"] == "PASS" and len(r2["unmeasured"]) == 7, r2)
ok27 = dict((u, b) for u, b in m["borders"].items() if b.get("fs") == 27509)
uses3 = {"actions": [{"op": "wire", "src": {"term_uid": b["outer_face"]}, "dst": {"term_uid": b["inner_face"]}, "via": u}
                     for u, b in ok27.items()],
         "carried": dict((k, v) for k, v in m["fs_border_entries"].items())}
r3 = SS.fs_border_gate(GR, uses3)
gate("B3 FS 27509's {0} classified borders + {1} entries -> PASS".format(len(ok27), len(m["fs_border_entries"])),
     ok27 and r3["status"] == "PASS", r3["used"])
u0 = sorted(um)[0]
b0 = um[u0]
r4 = SS.fs_border_gate(GR, {"actions": [{"op": "wire", "id": "x", "via": u0}]})
gate("B4 an action naming UNMEASURED tunnel {0} -> FAIL naming it".format(u0), r4["status"] == "FAIL" and str(u0) in r4["used"], r4["used"])
r5 = SS.fs_border_gate(GR, {"route_check": [{"id": "y", "route": "cfw", "terms": [b0["faces"][1][0]]}]})
gate("B5 a route naming face terminal {0} -> FAIL".format(b0["faces"][1][0]), r5["status"] == "FAIL" and str(u0) in r5["used"], r5["used"])
r6 = SS.fs_border_gate(GR, {"carried": {"{0}|{1}".format(b0["faces"][0][0], b0["faces"][0][1]): {"face": 1, "act": "x"}}})
gate("B6 a carried entry key '<face>|<frame>' -> FAIL", r6["status"] == "FAIL", r6["used"])
g7 = dict(GR)
g7.pop("fs_measured")
r7 = SS.fs_border_gate(g7, {"actions": [{"via": u0}]})
gate("B7 a graph without fs_measured -> PASS, nothing listed", r7["status"] == "PASS" and not r7["unmeasured"], r7)

# ---- D: check_launch requires dry_rule == 2
REC = os.environ["PRERUN_RECORDS"]
STG = os.path.join(SAND, "tools", "recipes", "stage_c134_2test.py")
open(STG, "w", encoding="utf-8").write("print('stage body')\n")
LAUNCH = 'py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "{0}"'.format(STG)


def records(rule):
    if os.path.exists(REC):
        os.remove(REC)
    SP.write_record("dry", STG, "PASS", None)
    SP.write_record("prerun", STG, "PASS", None)
    lines = [json.loads(x) for x in open(REC, encoding="utf-8").read().splitlines()]
    for d in lines:
        d["t"] = time.time() - 100
        if d["kind"] == "dry":
            if rule is None:
                d.pop("dry_rule", None)
            else:
                d["dry_rule"] = rule
    open(REC, "w", encoding="utf-8").write("\n".join(json.dumps(d) for d in lines) + "\n")
    return lines


lines = records(None)
ok, why = SP.check_launch(LAUNCH)
gate("D1 dry PASS without dry_rule -> refused, names PD288(c) + Re-dry", not ok and "PD288(c)" in why and "Re-dry" in why,
     why.splitlines()[0] if why else "")
lines = records(2)
ok, why = SP.check_launch(LAUNCH)
gate("D2 dry_rule 2 -> allowed (write_record default {0})".format(SP.DRY_RULE), ok, why)
records(1)
ok, why = SP.check_launch(LAUNCH)
gate("D3 dry_rule 1 -> refused", not ok and "PD288(c)" in why, why.splitlines()[0] if why else "")
if os.path.exists(REC):
    os.remove(REC)
SP.write_record("dry", STG, "PASS", None)
gate("D4 write_record('dry') stamps dry_rule == DRY_RULE", json.loads(open(REC).read().splitlines()[-1]).get("dry_rule") == SP.DRY_RULE)
np_, nf = sum(1 for _l, c in G if c), sum(1 for _l, c in G if not c)
print("=== GATES: {0} pass / {1} fail".format(np_, nf), flush=True)
print(P.result_line(P.make_result(np_, nf, next((l for l, c in G if not c), None))), flush=True)
sys.exit(1 if nf else 0)
