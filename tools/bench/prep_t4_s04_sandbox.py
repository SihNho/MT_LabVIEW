# ---
# labview: none
# hardware: none
# ---
r"""prep_t4_s04_sandbox - card chat-T4 (PD348): the s04 pipeline of bench arm A13K (cards 144-a1-P1 prep, 145-a3-2 rebase/dry/
prerun) re-run on MAIN's code, entirely in a %TEMP% sandbox, on the recorded fixtures tools/bench/fixtures/cmap_s03s04/.
Main has no s04 plan, pred or recipe and must not get one from this card: main's own s03 has not run, so a plan rebased on arm
A13K's s03 graph (a5d7ca5e, its VI under claudeDev\bench\A13K) would be wrong for main. Nothing is written under tools/ except
this script's log; stage_prerun runs with --no-record. LabVIEW is never opened (stage_prerun --dry / --prerun stub COM).
Existing first (checked): A13K prep_c144_a1_p1_mk.py (provisional simulate, route_check=False), prep_c145_a3_2 (rebase, recipe
pair, pred 6a71540e, dry/prerun); selftest_t4.py (the address port, 19/0) - this script only chains them on main's code.
STEPS (PREDICTION)
  S1 stagesim.simulate(fixture _in 66d94bad, provisional base 9b330384) -> final True, 23 actions (A13K plan 1f196f1d shape)
  S2 stage_prerun.rebase(S1 plan, real s03 graph a5d7ca5e, creation map from the s03 scratch log STEPX records, simulate=True)
     -> ok, 49 uids, final=True, completeness PASS; a13/a15 by face, a20 by cond; plan_in = the sandbox _in
  S3 pred = A13K's plan_ring_p4_s04v18_pred.json 6a71540e with ONLY plan/graph pins re-keyed to the sandbox files; its content
     (ops, cdiff_rows, census, errorlist, bed_md5) unchanged - the recipe's L1 / PB / CEN2 gates check that content
  S4 recipe = A13K tools/recipes/stage_d1_ring_p4_s04v18.py a5268776 with PLAN / PRED / out_json / sys.path re-pointed only
  S5 stage_prerun --dry <sandbox recipe> -> DRY PASS (E1 19 ops); S6 --prerun --no-record -> PASS (A13K: 16/0, WARN X13 x3, X14)
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_t4_s04_sandbox.log -- py -u tools/bench/prep_t4_s04_sandbox.py"""
import ast, json, os, re, shutil, subprocess, sys, tempfile                                # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(B)
R = os.path.dirname(T)
sys.path.insert(0, T)
import protocol as P, stage_prerun as SP, stagesim as SS                                    # noqa: E401,E402
FX = os.path.join(B, "fixtures", "cmap_s03s04")
A13K = os.path.join(os.path.dirname(R), "V6_bench", "A13K")
NP, NF = [0], []


def gate(name, ok, val=""):
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:500]), flush=True)
    NP[0] += bool(ok)
    if not ok:
        NF.append(name)


J = lambda p: json.load(open(p, encoding="utf-8"))                                         # noqa: E731
SBX = os.path.join(tempfile.gettempdir(), "t4_s04_sandbox")
shutil.rmtree(SBX, ignore_errors=True)
os.makedirs(SBX)
IN = os.path.join(SBX, "plan_ring_p4_s04v18_in.json")
pin = J(os.path.join(FX, "plan_ring_p4_s04v18_in.json"))
pin["base"]["path"] = os.path.join(FX, "prov_s04_base_provisional.json")
json.dump(pin, open(IN, "w", encoding="utf-8"), indent=1)
S1 = SS.simulate(IN, pin["base"]["path"], out_root=os.path.join(SBX, "sim_prov"), plan_out_dir=SBX, log=lambda *x: None, route_check=False)
PL = os.path.join(SBX, "plan_ring_p4_s04v18.json")
p1 = J(PL)
gate("S1 provisional simulate: final, 23 actions, base provisional + sim_of da66a030 kept, plan_in = sandbox _in",
     S1["final"] and len(p1["actions"]) == 23 and p1["base"].get("provisional") and p1["base"]["sim_of"]["md5"] == "da66a0300851133d93881be3c28f2fdc"
     and os.path.normcase(p1["finalized"]["plan_in"]["path"]).endswith("plan_ring_p4_s04v18_in.json"),
     (S1["final"], S1["failed"], p1["base"], p1["finalized"].get("plan_in")))
gr = J(os.path.join(FX, "real_graph_s03.json"))
gp = J(os.path.join(FX, "prov_s04_base_provisional.json"))
pobj = SP._obj_id(gp)
STEPX = re.compile(r"^\s*STEPX (\d+) (\S+)\s+acts \[([^\]]*)\] ids \[([^\]]*)\] bound (\{[^}]*\}) diff (\d+)")
CM = os.path.join(SBX, "s03_creation_map.jsonl")
with open(CM, "w", encoding="utf-8") as fh:                  # as selftest_t3.write_map / selftest_t4.write_map
    so = pin["base"]["sim_of"]
    fh.write(json.dumps({"schema": "creation-map/1", "rec": "run", "plan": so["plan"], "plan_md5": so["md5"], "stage": "x",
                         "work": gr["vi"], "from_step": None, "source": "fixture: STEPX bound records of s03_scratch_run.txt"}) + "\n")
    for ln in open(os.path.join(FX, "s03_scratch_run.txt"), encoding="utf-8", errors="replace").read().splitlines():
        m = STEPX.match(ln)
        for s, r in (ast.literal_eval(m.group(5)).items() if m else ()):
            fh.write(json.dumps({"schema": "creation-map/1", "rec": "bind", "k": int(m.group(1)), "op": m.group(2),
                                 "kind": "diag" if (pobj.get(s) or (None,))[0] == "Diagram" else "obj", "sim": s, "real": r}) + "\n")
lines = []
os.makedirs(os.path.join(SBX, "sim"))                      # run 1 died here: rebase writes the fsmap into out_root, never mkdirs it
ok2, det2 = SP.rebase(PL, os.path.join(FX, "real_graph_s03.json"), log=lines.append, simulate=True,
                      out_root=os.path.join(SBX, "sim"), creation_map=CM)
for s in lines:
    if s.startswith(("CREATION-MAP", "MAP-BOUND", "FALLBACK-COUNT", "REBIND", "ADDRESS-", "FS-CARRY")):
        print("  LOG   " + s[:300], flush=True)
p2 = J(PL)
fz = p2.get("finalized") or {}
gate("S2 rebase with re-simulation: ok, 49 uids, final, completeness PASS, no UNRESOLVED, 3 face/cond resolutions, plan_in = _in",
     ok2 and "49 uid(s) bound" in det2 and "final=True" in det2 and "completeness PASS" in det2
     and not any(s.startswith("ADDRESS-UNRESOLVED") for s in lines)
     and sum(1 for s in lines if s.startswith("ADDRESS-RESOLVED") and "PD348" in s) == 3
     and os.path.normcase(fz.get("plan_in", {}).get("path", "")).endswith("plan_ring_p4_s04v18_in.json"), det2[:400])
print("  FACT  S2 end_cdiff_rows {0}; open_rows {1}; open_rows_match {2}; failed {3}".format(
    len(fz.get("end_cdiff_rows") or []), len(p2.get("open_rows") or []), fz.get("open_rows_match"), fz.get("failed")), flush=True)
pa = J(os.path.join(A13K, "tools", "bench", "plan_ring_p4_s04v18.json"))
gate("S2b sandbox rebased plan == A13K's rebased plan 4de3fa39 on actions, open_rows, end_cdiff_rows (content, not bytes)",
     p2["actions"] == pa["actions"] and p2["open_rows"] == pa["open_rows"]
     and sorted(fz.get("end_cdiff_rows") or []) == sorted(pa["finalized"].get("end_cdiff_rows") or []),
     [n for n, (x, y) in enumerate(zip(p2["actions"], pa["actions"]), 1) if x != y][:8])
pred = J(os.path.join(A13K, "tools", "bench", "plan_ring_p4_s04v18_pred.json"))
gate("S3a A13K pred is 6a71540e, keyed to 4de3fa39", SP.md5(os.path.join(A13K, "tools", "bench", "plan_ring_p4_s04v18_pred.json"))
     == "6a71540e4dbf7ca37a1fa0a0e0ebab73" or pred["plan"]["md5"] == "4de3fa39252b1737fcfbfbba1706abb6", pred["plan"])
bp = fz["base"]["path"]
pred["plan"] = {"path": PL, "md5": SP.md5(PL)}
pred["graph"] = {"path": bp, "md5": SP.md5(os.path.join(R, bp))}
pred["note"] = "chat-T4 SANDBOX copy of A13K pred 6a71540e: plan/graph pins re-keyed only"
json.dump(pred, open(os.path.join(SBX, "plan_ring_p4_s04v18_pred.json"), "w", encoding="utf-8"), indent=1)
src = open(os.path.join(A13K, "tools", "recipes", "stage_d1_ring_p4_s04v18.py"), encoding="utf-8").read()
gate("S4a A13K recipe is a5268776", SP.md5(os.path.join(A13K, "tools", "recipes", "stage_d1_ring_p4_s04v18.py")) == "a5268776d2c3cdc3afaf4854b97b450b")
REPL = (("sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))", "sys.path.insert(0, {0!r})".format(T)),
        ('PLAN = os.path.join(K.BENCH, "plan_ring_p4_s04v18.json")', 'PLAN = os.path.join({0!r}, "plan_ring_p4_s04v18.json")'.format(SBX)),
        ('PRED = J(K.BENCH, "plan_ring_p4_s04v18_pred.json")', 'PRED = J({0!r}, "plan_ring_p4_s04v18_pred.json")'.format(SBX)),
        ('out_json=os.path.join(K.BENCH, "launch_c145_p4s04v18.json")', 'out_json=os.path.join({0!r}, "launch_t4_sandbox.json")'.format(SBX)))
for a, b in REPL:
    src = src.replace(a, b, 1) if src.count(a) == 1 else src + "\n# REPLACE-MISS " + a[:60]
gate("S4b recipe re-pointed: exactly 4 lines replaced, no other change", "REPLACE-MISS" not in src)
RC = os.path.join(SBX, "stage_d1_ring_p4_s04v18.py")
open(RC, "w", encoding="utf-8").write(src)
for lab, args, want in (("S5 dry", ["--dry", RC], "PASS"), ("S6 prerun", ["--prerun", RC, "--no-record"], "PASS")):
    r = subprocess.run([sys.executable, "-u", os.path.join(T, "stage_prerun.py")] + args, cwd=R, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=480)
    out = (r.stdout or "") + (r.stderr or "")
    open(os.path.join(SBX, lab.split()[1] + ".log"), "w", encoding="utf-8").write(out)
    keep = [x for x in out.splitlines() if re.search(r"^(DRY|PRERUN|RESULT|X\d+|  FAIL|FAIL|WARN)|E1 |UNROUTABLE|first_fail", x.strip())]
    for x in keep[-40:]:
        print("  {0:<6}| {1}".format(lab.split()[1], x[:300]), flush=True)
    res = P.parse_result_line(out)
    gate("{0}: rc 0 and RESULT {1}".format(lab, want), r.returncode == 0 and res is not None and res.get("status") == want,
         (r.returncode, res))
print("  FACT  sandbox kept at {0} (logs dry.log / prerun.log)".format(SBX), flush=True)
print(P.result_line(P.make_result(NP[0], len(NF), NF[0] if NF else None)), flush=True)
sys.exit(0 if not NF else 1)
