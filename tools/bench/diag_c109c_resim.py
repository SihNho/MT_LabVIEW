r"""diag_c109c_resim - card 109-3 S2/S3, OFFLINE (no LabVIEW, no COM). Re-simulates plan_l2a2, plan_disp and plan_l2a3 with
the CURRENT tools/stagesim.py and compares with their recorded finals.
  arg 'pre'  = before the op_wire keep-stub-uid fix (baseline: does the current code reproduce the recorded finals?)
  arg 'post' = after it; l2a3 is then written to its official place (tools/bench/sim/l2a3 + tools/bench/plan_l2a3.json)
PRIOR ART: stagesim.simulate (the same entry the plans were finalized with, stagesim.py:1151); stage_d1_l2a3.py:71-74 (gate D).
PREDICTION: l2a2 / disp end rows + open rows == recorded (both tags; disp against the card-106-3 re-sim record, 6 rows,
tools/bench/sim/c106c_resim_summary.json:13,65-66 - the 21-row plan_disp.json predates 106-3's cdiff inputs, diag_c109c_resim_pre.log);
post: every stage's end rows == its pre-fix re-sim; l2a3 open rows == recorded; l2a3 gate-D
prediction pre = new 2 / lost [9921, 11389] (the c109b dry log), post = new [] / lost [] == the real run (c109b log :172).
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c109c_resim_<tag>.log -- py -u tools/bench/diag_c109c_resim.py <tag>"""
import json, os, sys                                                               # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS, protocol                                                    # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
TAG = sys.argv[1] if len(sys.argv) > 1 else "pre"
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def resim(name, recorded, official=False, rows_record=None):
    R = J(recorded); F = R["finalized"]                                           # noqa: E702
    if rows_record:                                                               # disp: the POST-106-3 finalize record (the 02:15 plan_disp.json
        F = dict(F, end_cdiff_rows=rows_record)                                   # predates card 106-3's cdiff inputs; c106c_resim_summary.json:65-66
        print("RESIM {0}: end-row baseline = card 106-3 re-sim record ({1} rows), not the plan file's {2}".format(
            name, len(rows_record), len(R["finalized"]["end_cdiff_rows"] or [])), flush=True)
    pin, base = os.path.join(ROOT, F["plan_in"]["path"]), os.path.join(ROOT, F["base"]["path"])
    print("RESIM {0}: plan_in {1} (md5 now {2}, recorded {3}); base {4} (md5 now {5}, recorded {6})".format(
        name, F["plan_in"]["path"], SS.md5_file(pin), F["plan_in"]["md5"], F["base"]["path"], SS.md5_file(base), F["base"]["md5"]), flush=True)
    kw = {} if official else {"out_root": os.path.join(B, "sim", "c109c_" + TAG), "plan_out_dir": os.path.join(B, "sim", "c109c_" + TAG)}
    pins = dict((x["n"], x["path"]) for x in R["finalized"]["step_files"])
    pre = os.path.join(B, "sim", "c109c_pre", "plan_{0}.json".format(name))
    if TAG == "post" and os.path.exists(pre):                                      # PREPIN: pre-fix re-sim states vs the pinned files,
        pre_p = dict((x["n"], x["path"]) for x in J(pre)["finalized"]["step_files"])   # read BEFORE an official run overwrites them
        d = [n for n in sorted(pins) if n not in pre_p or J(pre_p[n])["state"] != J(pins[n])["state"]]
        STATE_DIFF[(name, "pre_vs_pinned")] = d
        print("STATES {0}: PRE-FIX re-sim differs from the pinned files at {1} ({2} pinned steps)".format(name, d, len(pins)), flush=True)
    S = SS.simulate(pin, base, log=lambda *_a: None, **kw)
    print("RESIM {0}: final {1} failed {2} end_cdiff_rows {3} open_rows_match {4} plan_out {5}".format(
        name, S["final"], S["failed"], len(S["end_cdiff_rows"] or []), S["open_rows_match"], S["plan_out"]), flush=True)
    pair = lambda k: [int(k.split("|")[0]), k.split("|")[2]] if isinstance(k, str) else [int(k[0]), k[1]]   # noqa: E731
    got, want = sorted(pair(k) for k in S["end_cdiff_rows"] or []), sorted(pair(k) for k in F["end_cdiff_rows"] or [])
    gate("{0} end_cdiff_rows (node, term) == recorded ({1} rows)".format(name, len(want)), got == want,
         {"extra": [x for x in got if x not in want], "missing": [x for x in want if x not in got]})
    gate("{0} final / open_rows == recorded".format(name), S["final"] == R["final"] and S["open_rows"] == F["open_rows"],
         (S["final"], S["open_rows_match"], S["open_rows"]))
    pre = os.path.join(B, "sim", "c109c_pre", "plan_{0}.json".format(name))
    if TAG == "post" and os.path.exists(pre):                                      # the op_wire change alone: pre-fix vs post-fix
        P0 = J(pre)["finalized"]
        gate("{0} post-fix end rows == pre-fix end rows (full keys, {1})".format(name, len(P0["end_cdiff_rows"] or [])),
             S["end_cdiff_rows"] == P0["end_cdiff_rows"] and S["open_rows_match"] == P0["open_rows_match"],
             (S["end_cdiff_rows"], P0["end_cdiff_rows"]))
    # review c109c-resim-disp-baseline s4 (R4 style, diag_c106c_resim.py:63): every re-simulated step STATE vs the pinned step
    # file named by the recorded plan, and (post) vs the pre-fix re-sim; a wiring change can alter a state and not the end rows
    now = [(s["n"], s["file"]["path"]) for s in S["steps"] if s.get("file")]
    if not official:                                                               # official l2a3 overwrote its pins: see PREPIN
        d_pin = [n for n, p in now if n not in pins or J(p)["state"] != J(pins[n])["state"]]
        STATE_DIFF[(name, "pinned")] = d_pin
        print("STATES {0}: {1} steps, differ from the pinned files at {2}".format(name, len(now), d_pin), flush=True)
    if TAG == "post" and os.path.exists(pre):
        pre_p = dict((x["n"], x["path"]) for x in J(pre)["finalized"]["step_files"])
        d_pre = [n for n, p in now if n not in pre_p or J(p)["state"] != J(pre_p[n])["state"]]
        STATE_DIFF[(name, "pre")] = d_pre
        print("STATES {0}: differ from the PRE-FIX re-sim at {1}".format(name, d_pre), flush=True)
    return R, S


STATE_DIFF = {}


R2, S2 = resim("l2a2", os.path.join(B, "plan_l2a2.json"))
RD, SD = resim("disp", os.path.join(B, "sim", "disp", "plan_disp.json"),
               rows_record=J(os.path.join(B, "sim", "c106c_resim_summary.json"))["end_rows"])
old3 = J(os.path.join(B, "plan_l2a3.json"))
R3, S3 = resim("l2a3", os.path.join(B, "plan_l2a3.json"), official=(TAG == "post"))
new3 = J(S3["plan_out"]["path"])
if TAG == "post":
    for nm in ("l2a2", "disp"):
        gate("S2 {0}: step states - pre-fix == pinned, post-fix == pre-fix (R4 style)".format(nm),
             STATE_DIFF.get((nm, "pre_vs_pinned")) == [] and STATE_DIFF.get((nm, "pre")) == [] and STATE_DIFF.get((nm, "pinned")) == [],
             dict((k[1], v) for k, v in STATE_DIFF.items() if k[0] == nm))
    gate("S3 l2a3: pre-fix states == pinned; post-fix differs from pre-fix ONLY at the two wire steps [5, 6]",
         STATE_DIFF.get(("l2a3", "pre_vs_pinned")) == [] and STATE_DIFF.get(("l2a3", "pre")) == [5, 6],
         dict((k[1], v) for k, v in STATE_DIFF.items() if k[0] == "l2a3"))
gate("l2a3 plan rows unchanged (actions + open_rows identical to the plan before this run)",
     new3["actions"] == old3["actions"] and new3["open_rows"] == old3["open_rows"], len(new3["actions"]))
base_t = J(R3["finalized"]["base"]["path"])["terminals"]
end_t = S3["_state"]["terminals"]
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])      # noqa: E731  (stage_d1_l2a3.py:23)
sim_new, sim_lost = sorted(wires(end_t) - wires(base_t)), sorted(wires(base_t) - wires(end_t))   # stage_d1_l2a3.py:71
print("D PREDICTION ({0}): new {1} lost {2}".format(TAG, sim_new, sim_lost), flush=True)
for w in (9921, 11389):
    print("  END WIRE {0}: {1}".format(w, sorted((r["term_uid"], r["owner_uid"], r["term_name"], r["is_source"]) for r in end_t
                                              if r["wire_uid"] == w)), flush=True)
for st in S3["steps"][5:]:
    print("  STEP {0} effect {1}".format(st["n"], st.get("effect_summary")), flush=True)
real_new, real_lost = [], []                                                       # stage_d1_l2a3_c109b.log:172
d_ok = len(real_new) == len(sim_new) and set(real_lost) == set(sim_lost)            # the gate-D arithmetic, stage_d1_l2a3.py:73-74
if TAG == "post":
    gate("S3 replayed gate D: prediction new {0} lost {1} vs the 109-2 real run new [] lost [] -> D {2}".format(
        sim_new, sim_lost, "PASS" if d_ok else "FAIL"), d_ok, (sim_new, sim_lost))
else:
    print("PRE-FIX D replay against the real run would be {0} (expected FAIL: the c109b defect)".format("PASS" if d_ok else "FAIL"))
n_pass = sum(1 for _l, ok in gates if ok); n_fail = len(gates) - n_pass            # noqa: E702
first = next((l for l, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, [S3["plan_out"]])))
sys.exit(0 if n_fail == 0 else 1)
