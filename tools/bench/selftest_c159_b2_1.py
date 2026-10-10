# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-b2-1.md
# ---
r"""selftest_c159_b2_1 - card 159-b2-1 (PD388(d)): tools/stage_prerun.py DRY_RULE 2 -> 3; check_launch refuses a dry recorded under rule 2.
OFFLINE: no LabVIEW, no COM. Every record lives in a %TEMP% sandbox (PRERUN_RECORDS / PRERUN_LOG_DIR / STAGE_RUNS / SCRATCH_SKIP_LOG,
fn_records.GATE_LOG), the pattern of selftest_c134_2_gates.py D1-D4. The real tools/bench/prerun_records.jsonl is READ only (md5 before == after).
Called, not copied: stage_prerun.check_launch / write_record / read_records. Launch command (fixture):
  py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "<SAND>/tools/recipes/stage_c159b21test.py"
PREDICTION (gates):
  R0 SP.DRY_RULE == 3; R0b the file with that one line put back to 2 hashes to the card pin 9ea1bdeb.  R1 a stored real dry record (newest kind=dry status=PASS dry_rule=2 with a prerun PASS of the same sha256/plan md5s)
     exists.  T1 that dry + prerun, rebound to the sandbox fixture (script/sha256/plan_md5s only), dry_rule 2 -> check_launch REFUSED with the
     old-rule text (PD288(c), 'dry rule 2', 'dry_rule == 3').  T2 the same records with dry_rule 3 -> ALLOWED.  T3 the two dry records differ
     in dry_rule only.  T4 write_record('dry') stamps dry_rule 3.  M1 MUTANT (stage_prerun source with the dry_rule filter line replaced by
     `m = m`, executed in memory under the real __file__) ALLOWS the T1 records: T1 discriminates the comparison.
  C1 real records: counts with dry_rule != 3 (all records / dry records) printed; zero dry records carry dry_rule 3.
  C2 p5s02a MAIN and scratch recipes over a TEMP copy of the real records, ADOPT_LOG pointed at an empty sandbox path (run 1 showed the
     chat-S4 A adoption gate refuses both first, adopted_scratch.jsonl): check_launch REFUSED for want of a valid dry (PD288(c) / no dry).
     The as-is verdict (real ADOPT_LOG) is printed as FACT C2a.
  C3 real prerun_records.jsonl md5 before == after.
Usage: py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c159_b2_1.log -- py -u tools/bench/selftest_c159_b2_1.py"""
import atexit, hashlib, json, os, shutil, sys, tempfile, time, types           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
SAND = tempfile.mkdtemp(prefix="c159_b2_1_")
atexit.register(shutil.rmtree, SAND, True)
os.makedirs(os.path.join(SAND, "tools", "recipes"), exist_ok=True)
os.makedirs(os.path.join(SAND, "logs"), exist_ok=True)
os.environ.update({"PRERUN_RECORDS": os.path.join(SAND, "records.jsonl"), "PRERUN_LOG_DIR": os.path.join(SAND, "logs"),
                   "STAGE_RUNS": os.path.join(SAND, "stage_runs.jsonl"), "STAGE_RUNS_CYCLE": "cycle 903",
                   "SCRATCH_SKIP_LOG": os.path.join(SAND, "skip.log")})
sys.path.insert(0, TOOLS)
import stage_prerun as SP, protocol as P, fn_records as FR      # noqa: E402,E401
FR.GATE_LOG = os.path.join(SAND, "fn_gate.log")
REAL = os.path.join(HERE, "prerun_records.jsonl")
G = []


def gate(label, ok, d=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


real_md5 = md5f(REAL)
print("stage_prerun.py md5 {0}; real prerun_records.jsonl md5 {1}".format(md5f(SP.__file__), real_md5), flush=True)
gate("R0 SP.DRY_RULE == 3", SP.DRY_RULE == 3, SP.DRY_RULE)
_b = open(SP.__file__, "rb").read()
_rev = hashlib.md5(_b.replace(b"\nDRY_RULE = 3\r\n", b"\nDRY_RULE = 2\r\n").replace(b"\nDRY_RULE = 3\n", b"\nDRY_RULE = 2\n")).hexdigest()
gate("R0b the file differs from the card pin 9ea1bdeb by the DRY_RULE line only (that line reverted -> pin md5)",
     _rev == "9ea1bdeb8afcd2eef4abfe6b3531f66f" and _b.count(b"\nDRY_RULE = ") == 1, _rev)
SP.RECORDS = REAL
real = SP.read_records()
SP.RECORDS = os.environ["PRERUN_RECORDS"]
pr = dict(((r["sha256"], json.dumps(r.get("plan_md5s"), sort_keys=True)), r) for r in real
          if r.get("kind") == "prerun" and r.get("status") == "PASS" and r.get("sha256"))
src = [r for r in real if r.get("kind") == "dry" and r.get("status") == "PASS" and r.get("dry_rule") == 2
       and (r.get("sha256"), json.dumps(r.get("plan_md5s"), sort_keys=True)) in pr]
dry0 = max(src, key=lambda r: r["t"]) if src else None
gate("R1 stored dry PASS (dry_rule 2) with a matching prerun PASS", dry0, dry0 and (dry0["script"], dry0["iso"], dry0["sha256"][:12]))
STG = os.path.join(SAND, "tools", "recipes", "stage_c159b21test.py")
open(STG, "w", encoding="utf-8").write("print('stage body')\n")
LAUNCH = 'py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "{0}"'.format(STG)
bind = {"script": SP.rel(STG), "sha256": SP.sha256(STG), "plan_md5s": SP.plan_md5s(STG), "t": time.time() - 100}
pre0 = pr[(dry0["sha256"], json.dumps(dry0.get("plan_md5s"), sort_keys=True))] if dry0 else {}


def records(rule):
    d, p = dict(dry0 or {}, **bind), dict(pre0, **bind)
    d["dry_rule"] = rule
    open(SP.RECORDS, "w", encoding="utf-8").write(json.dumps(d) + "\n" + json.dumps(p) + "\n")
    return d


d2 = records(2)
ok1, why1 = SP.check_launch(LAUNCH)
gate("T1 dry_rule 2 -> REFUSED, old-rule text", not ok1 and "PD288(c)" in why1 and "dry rule 2" in why1 and "dry_rule == 3" in why1,
     why1.splitlines()[0] if why1 else "(allowed)")
d3 = records(3)
ok2, why2 = SP.check_launch(LAUNCH)
gate("T2 dry_rule 3, otherwise identical -> ALLOWED", ok2, why2)
gate("T3 the two dry records differ in dry_rule only", [k for k in set(d2) | set(d3) if d2.get(k) != d3.get(k)] == ["dry_rule"])
os.remove(SP.RECORDS)
SP.write_record("dry", STG, "PASS", None)
gate("T4 write_record('dry') stamps dry_rule 3", json.loads(open(SP.RECORDS).read().splitlines()[-1]).get("dry_rule") == 3)
# M1: mutant = the real source with check_launch's dry_rule filter removed, executed in memory (nothing written)
code = open(SP.__file__, encoding="utf-8").read()
LINE = 'm = [r for r in m if r.get("dry_rule") == DRY_RULE]'
mut = types.ModuleType("stage_prerun_mut")
mut.__file__ = SP.__file__
if code.count(LINE) == 1:
    exec(compile(code.replace(LINE, "m = m"), SP.__file__, "exec"), mut.__dict__)
    mut.RECORDS = SP.RECORDS
    records(2)
    okm, whym = mut.check_launch(LAUNCH)
else:
    okm, whym = False, "filter line found {0}x".format(code.count(LINE))
gate("M1 mutant without the dry_rule filter ALLOWS the dry_rule-2 records (T1 discriminates)", okm, whym)
# C: the real records, read only
ne_all = sum(1 for r in real if r.get("dry_rule") != 3)
dry = [r for r in real if r.get("kind") == "dry"]
ne_dry = sum(1 for r in dry if r.get("dry_rule") != 3)
print("C1 real records {0}: dry_rule != 3 in {1} (all kinds) / {2} of {3} dry records; dry_rule values {4}".format(
    len(real), ne_all, ne_dry, len(dry), sorted(set(str(r.get("dry_rule")) for r in dry))), flush=True)
gate("C1 no real dry record carries dry_rule 3", ne_dry == len(dry), ne_dry)
shutil.copyfile(REAL, SP.RECORDS)
ADOPT_REAL = SP.ADOPT_LOG
for name in ("stage_d1_ring_p5s02a.py", "stage_d1_ring_p5s02a_scratch.py"):
    rp = os.path.join(TOOLS, "recipes", name)
    cmd = 'py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "{0}"'.format(rp)
    SP.ADOPT_LOG = ADOPT_REAL           # as the real gate sees it (run 1 of this test: refused by the chat-S4 A adoption gate first)
    oka, whya = SP.check_launch(cmd)
    print("FACT C2a {0} as-is: {1} | {2}".format(name, "ALLOWED" if oka else "REFUSED", (whya.splitlines() or [""])[0][:160]), flush=True)
    SP.ADOPT_LOG = os.path.join(SAND, "no_adopt.jsonl")   # adoption gate isolated so the dry filter is the one that decides
    okr, whyr = SP.check_launch(cmd)
    gate("C2 {0} over the TEMP copy of the real records, adoption isolated -> REFUSED, no valid dry".format(name),
         not okr and ("PD288(c)" in whyr or "has no dry" in whyr), whyr.splitlines()[0] if whyr else "(allowed)")
SP.ADOPT_LOG = ADOPT_REAL
gate("C3 real prerun_records.jsonl md5 before == after", md5f(REAL) == real_md5, (real_md5, md5f(REAL)))
np_, nf = sum(1 for _l, c in G if c), sum(1 for _l, c in G if not c)
print("=== GATES: {0} pass / {1} fail".format(np_, nf), flush=True)
print(P.result_line(P.make_result(np_, nf, next((l for l, c in G if not c), None))), flush=True)
sys.exit(1 if nf else 0)
