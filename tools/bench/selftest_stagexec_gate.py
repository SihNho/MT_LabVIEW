r"""selftest_stagexec_gate - card chat-S3: the LAUNCH GATE for `tools/stagexec.py run <plan>` (tools/stage_prerun.py
launched_plan_runs / plan_record / check_launch; guard_bash.prerun_gate delegates to it). No LabVIEW; records and logs in
a %TEMP% sandbox (PRERUN_RECORDS / PRERUN_LOG_DIR / STAGE_RUNS), never in tools/bench.
Card 80-3 adds G8-G13: stagexec's wire_indicators whitelist removed; an op error stops unless the recipe declares a
named gate reading that exact sink (tools/stagexec.py check_sink_gates / sink_gate_for / LVBackend.run_deferred).
PREDICTION: G1-G13 PASS.
    MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_stagexec_gate.log -- py -u tools/bench/selftest_stagexec_gate.py"""
import json, os, shutil, sys, time                                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
SAND = os.path.join(os.environ.get("TEMP", "."), "sxg_selftest_{0}".format(os.getpid()))
os.makedirs(os.path.join(SAND, "logs"), exist_ok=True)
os.environ["PRERUN_RECORDS"] = os.path.join(SAND, "records.jsonl")
os.environ["PRERUN_LOG_DIR"] = os.path.join(SAND, "logs")
os.environ["STAGE_RUNS"] = os.path.join(SAND, "stage_runs.jsonl")
os.environ["STAGE_RUNS_CYCLE"] = "cycle 902"
sys.path.insert(0, TOOLS)
import stage_prerun as SP   # noqa: E402
import protocol as P        # noqa: E402
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


plan = os.path.join(SAND, "plan_x.json")
shutil.copyfile(os.path.join(HERE, "plan_l7_split.json"), plan)
cmd = "MATERIAL=1 py tools/bgrun.py --max-min 60 --log tools/bench/x.log -- py -u tools/stagexec.py run {0}".format(plan)
u = SP.launched_plan_runs(cmd)
gate("G1 a bgrun'd `stagexec.py run <plan>` is ONE plan launch", len(u) == 1 and u[0][1] == os.path.normpath(plan), u)
gate("G2 reading/grepping stagexec.py or running its dry/prerun is not a launch",
     not SP.launched_plan_runs("grep run tools/stagexec.py") and not SP.launched_plan_runs("py tools/stagexec.py prerun " + plan)
     and not SP.launched_plan_runs("py tools/stagexec.py dry " + plan))
ok, why = SP.check_launch(cmd)
gate("G3 no dry/prerun record for the plan => refused, naming the plan", not ok and "plan_x.json" in why, why.splitlines()[0] if why else "")
SP.plan_record("dry", plan, "PASS", None)
ok, why = SP.check_launch(cmd)
gate("G4 dry only => still refused (prerun missing)", not ok and "prerun" in why, why.splitlines()[0] if why else "")
SP.plan_record("prerun", plan, "PASS", None)
ok, why = SP.check_launch(cmd)
gate("G5 dry + prerun PASS for this stagexec sha256 and plan md5 => allowed", ok, why)
with open(plan, "a", encoding="utf-8") as f:
    f.write(" ")
ok, why = SP.check_launch(cmd)
gate("G6 the plan changed after its records (md5) => refused", not ok and "no dry + prerun" in why, why.splitlines()[0] if why else "")
SP.plan_record("dry", plan, "PASS", None)
SP.plan_record("prerun", plan, "PASS", None)
time.sleep(1.1)
with open(os.path.join(SAND, "logs", "stagexec_x.log"), "w", encoding="utf-8") as f:
    f.write("BGRUN START 2026-09-24 00:00:00 limit 60.0 min: py -u tools/stagexec.py run {0}\n".format(plan))
    f.write(P.result_line(P.make_result(3, 1, "STEP-DIFF after real op 3")) + "\nBGRUN END rc=1 after 5s\n")
ok, why = SP.check_launch(cmd)
gate("G7 a FAILED stagexec run after the records => refused until re-pre-run (decision 4)", not ok and "FAILED" in why,
     why.splitlines()[0] if why else "")

# ---- card 80-3: SINK GATES replace the wire_indicators whitelist (retrospective-cycle79 device-failed) --------------
import stagexec as SX       # noqa: E402
ERR = "RuntimeError: wire_indicators: target BROKEN after wiring - a source terminal was probably unwired"


class FakeStage(object):
    def __init__(self):
        self.facts, self.gates, self.purged = [], [], []

    def wire_indicators(self, *a, **k):
        return {"err": ERR, "s": 0.1}

    def junk_purge(self, tag=""):
        self.purged.append(tag)

    def uid_index(self, cls, uid):
        return 0

    def gate(self, label, ok, detail="", fatal=False):
        self.gates.append((label, bool(ok)))

    def fact(self, line):
        self.facts.append(line)


class FakeB(object):
    work = None

    def diag_index(self, work, uid):
        return 0


def backend(sink_gates=None, gates=None):
    be = object.__new__(SX.LVBackend)          # no stagekit/gscript import: the backend's own indicator path, COM faked
    be.s, be.B = FakeStage(), FakeB()
    be.s.work = None
    be._init_sink_gates(sink_gates, gates)
    return be


RS = {"wire_uid": 77, "frame_diagram": 686, "owner_class": "SubVI", "owner_uid": 5058, "term_name": "pos in cal image out", "term_uid": 1}
RD = {"owner_uid": 900, "term_name": "Pos within cal image", "term_uid": 2}
src = open(SX.__file__, encoding="utf-8").read()
gate("G8 the whitelist is gone: no 'target BROKEN after wiring' special case left in stagexec.py",
     "target BROKEN after wiring" not in src and 'rec["err"] = None' not in src)
be = backend()
try:
    be.indicator(RS, RD)
    gate("G9 T1 wire_indicators error, NO declared gate -> ExecStop (the run stops)", False, "no stop")
except SX.ExecStop as e:
    gate("G9 T1 wire_indicators error, NO declared gate -> ExecStop (the run stops)", "no declared gate reads that sink" in str(e), e)
reads = []
rd_gate = lambda e: (reads.append(e["sink"]) or True, "read sink {0}".format(e["sink"]))   # noqa: E731
be = backend([{"gate": "W pos_ind", "sink": [900, "Pos within cal image"]}], {"W pos_ind": rd_gate})
try:
    r = be.indicator(RS, RD)
    be.run_deferred()
    gate("G10 T2 error WITH a declared gate on that exact sink -> continues, logged, and the gate READS that sink at run end",
         r.get("deferred_to") == "W pos_ind" and any("DEFERRED" in f for f in be.s.facts) and reads == [[900, "Pos within cal image"]]
         and be.s.gates == [(be.s.gates[0][0], True)] and be.deferred[0]["gate_ok"] is True, (r, be.s.facts, reads, be.s.gates))
except SX.ExecStop as e:
    gate("G10 T2 error WITH a declared gate on that exact sink -> continues", False, e)
try:
    backend([{"gate": "W missing", "sink": [900, "Pos within cal image"]}], {"W pos_ind": rd_gate})
    gate("G11 T2 a declaration naming an ABSENT gate -> refused", False, "accepted")
except SX.ExecStop as e:
    gate("G11 T2 a declaration naming an ABSENT gate -> refused", "no such gate" in str(e), e)
be = backend([{"gate": "W pos_ind", "sink": [900, "Pos: Diffraction Pattern"]}], {"W pos_ind": rd_gate})
try:
    be.indicator(RS, RD)
    gate("G12 T2 a declaration naming ANOTHER sink -> the error still stops", False, "no stop")
except SX.ExecStop as e:
    gate("G12 T2 a declaration naming ANOTHER sink -> the error still stops", "no declared gate reads that sink" in str(e), e)
be = backend([{"gate": "W pos_ind", "sink": [900, "Pos within cal image"]}], {"W pos_ind": lambda e: (False, "sink unwired")})
be.indicator(RS, RD)
try:
    be.run_deferred()
    gate("G13 a declared gate that FAILS its read stops the run", False, "no stop")
except SX.ExecStop as e:
    gate("G13 a declared gate that FAILS its read stops the run", "failed" in str(e) and be.s.gates[-1][1] is False, e)
n_pass = sum(1 for _l, o in G if o)
first = next((l for l, o in G if not o), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(G) - n_pass, "; failing: " + first if first else ""))
print(P.result_line(P.make_result(n_pass, len(G) - n_pass, first)))
shutil.rmtree(SAND, ignore_errors=True)
sys.exit(0 if n_pass == len(G) else 1)
