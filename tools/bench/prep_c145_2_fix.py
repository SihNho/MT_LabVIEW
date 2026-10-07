# ---
# labview: none
# hardware: none
# ---
r"""prep_c145_2_fix - card 145-a1-2 steps 1-2 (OFFLINE, no LabVIEW). Corrects ONLY the SQ1 row (p4_s2_seqcheck, class SubVI) of
plan_ring_p4_s04v18.json (9ff46b0e) to the MEASURED 12-row terminal table of a real RingSeqCheck_v0.vi drop, then re-simulates the plan on
its unchanged real base exactly as stage_prerun.rebase does after its binding (stage_prerun.py:4362-4412: final/finalized dropped, a TEMP copy
simulated with stagesim.simulate, sim step files guarded by stagesim.WriteGuard and restored unless FINAL, finalized.rebase + plan_in carried).
Row content comes from the measured log (diag_c144_p4s04v18_scratch.log:231-242, md5 64a6b63b, card 145-a1-1), never retyped; terminal ORDER =
the measured t-index order, as the PS1 row already is (plan :77-138 == log :67-78), so stagesim's addr_pos indexes equal the real ones.
Existing tools checked: stage_prerun.rebase (refuses a non-provisional base, :4205), stagesim.simulate (:2442), stagesim.WriteGuard; no new op.
PREDICTION CONTRACT: M0 input md5s == card; L 12 measured rows (8 named + 4 '' sinks t0,t4,t5,t6); D the edited plan differs from the old ONLY in
  actions[SQ1].terminals/why; S re-simulation FINAL, failed None; E end_cdiff_rows / open_rows / open_rows_match / fs_routes / route_check rows /
  fs_border_gate.status == old; A addr_pos == old except SQ1 rows, whose index == measured t-index (last 9, n1 11); W plan written.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c145_2_fix.log -- py -u tools/bench/prep_c145_2_fix.py"""
import copy, hashlib, json, os, re, shutil, sys, tempfile                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
PLAN, PLAN_MD5 = os.path.join(B, "plan_ring_p4_s04v18.json"), "9ff46b0ece1f238c831d7786616c4f05"
LOGF, LOG_MD5 = os.path.join(B, "diag_c144_p4s04v18_scratch.log"), "64a6b63b9dc901559aba54d48b843baf"
OLDP = os.path.join(B, "prep_c145_2_plan_9ff46b0e.json")                                    # byte copy of the old plan, kept
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        if G.get("wg") is not None:                                                         # a failed check after the sim: step files back
            print("FACT sim step files restored {0}".format(G["wg"].restore()), flush=True)
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


gate("M0 plan 9ff46b0e and failing log 64a6b63b md5 == card/facts", md5(PLAN) == PLAN_MD5 and md5(LOGF) == LOG_MD5, (md5(PLAN), md5(LOGF)))
lines = open(LOGF, encoding="utf-8", errors="replace").read().splitlines()
rx = re.compile(r"create subvi p4_s2_seqcheck new #29724 t(\d+)\s+'([^']*)'\s+is_source=(True|False)")
rows = []
for ln_no in range(231, 243):                                                                # log :231-242 (1-based)
    m = rx.search(lines[ln_no - 1])
    rows.append((int(m.group(1)), m.group(2), m.group(3) == "True") if m else None)
gate("L 12 measured rows t0..t11 at log :231-242; 8 named + 4 '' sinks", None not in rows and [r[0] for r in rows] == list(range(12))
     and sum(1 for r in rows if r[1] == "") == 4 and all(not r[2] for r in rows if r[1] == ""), rows)
shutil.copyfile(PLAN, OLDP)
old = json.load(open(PLAN, encoding="utf-8"))
k = next(i for i, a in enumerate(old["actions"]) if a.get("id") == "p4_s2_seqcheck")
new = copy.deepcopy(old)
a = new["actions"][k]
gate("Q SQ1 row is create/SubVI/as SQ1 with the 8 named terminals == the measured named rows",
     a["op"] == "create" and a["class"] == "SubVI" and a["as"] == "SQ1"
     and sorted((t["name"], t["is_source"]) for t in a["terminals"]) == sorted((r[1], r[2]) for r in rows if r[1]), a["terminals"])
a["terminals"] = [{"name": r[1], "is_source": r[2], "term_class": "Terminal"} for r in rows]
a["why"] = ("ROUTE subvi (drop_subvi, stagexec.py:438-441,3047-3054) | MEASURED terminals (card 145-a1-2): real drop of RingSeqCheck_v0.vi "
            "(0295a8d3) = 12 rows in t-index order t0 '' | t1 valid, t2 next discards, t3 next last | t4-t6 '' | t7 discards, t8 Latest, "
            "t9 last, t10 n2, t11 n1 (diag_c144_p4s04v18_scratch.log:230-242, 145-a1-1; pane read back 11 n1 .. 7 discards | 3 next last, "
            "2 next discards, 1 valid; 0 and 4-6 free: diag_c142_4_facts.md:22-23, build_ringseqcheck_v0.log:216-217); was PROVISIONAL 8 keys "
            "(review archive/peer/2026-10-07-c145-1-sq1-bind.md) | PD330(a) S2 replaces p4_eq_seq..p4_inc_disc + inner wires (G5 scalar core)")
diff = [i for i, (x, y) in enumerate(zip(old["actions"], new["actions"])) if x != y]
gate("D actions differ ONLY at the SQ1 row (index {0}) and only in terminals/why".format(k),
     diff == [k] and len(old["actions"]) == len(new["actions"])
     and dict((f, v) for f, v in old["actions"][k].items() if f not in ("terminals", "why")) == dict((f, v) for f, v in a.items() if f not in ("terminals", "why"))
     and dict((f, v) for f, v in old.items() if f not in ("actions", "final", "finalized")) == dict((f, v) for f, v in new.items() if f not in ("actions", "final", "finalized")), diff)
ofz = old["finalized"]
OLD_SYM = json.load(open(os.path.join(ROOT, ofz["last_step"]["path"]), encoding="utf-8"))["state"]["sym"]
gate("O old last step file md5 == plan's (read before the sim overwrites it)", md5(os.path.join(ROOT, ofz["last_step"]["path"])) == ofz["last_step"]["md5"], ofz["last_step"])
new.pop("final", None)
new.pop("finalized", None)
base_path = os.path.join(ROOT, ofz["base"]["path"])
gate("B base file md5 == plan's (a63f5929)", md5(base_path) == ofz["base"]["md5"] == new["base"]["md5"], (md5(base_path), ofz["base"]))
tmp = tempfile.mkdtemp(prefix="c145_2_resim_")
tp = os.path.join(tmp, os.path.basename(PLAN))
json.dump(new, open(tp, "w", encoding="utf-8"), indent=1)
wg = SS.WriteGuard(dirs=(os.path.join(SS.SIM_ROOT, new.get("stage") or "plan"),))
G["wg"] = wg
try:
    S = SS.simulate(tp, base_path, plan_out_dir=tmp, log=lambda m: print(m, flush=True))
    gate("S re-simulation FINAL, failed None", S["final"] and S["failed"] is None, (S["final"], S["failed"]))
    out = json.load(open(S["plan_out"]["path"] if os.path.isabs(S["plan_out"]["path"]) else os.path.join(ROOT, S["plan_out"]["path"]), encoding="utf-8"))
except Exception:
    wg.restore()
    raise
finally:
    shutil.rmtree(tmp, ignore_errors=True)
fz = out["finalized"]
for f in ("end_cdiff_rows", "open_rows", "open_rows_match", "open_rows_match_legacy", "fs_routes", "undecided", "first_divergent", "cdiff_inputs"):
    gate("E finalized.{0} == old".format(f), fz.get(f) == ofz.get(f), (fz.get(f), ofz.get(f)))
gate("E route_check PASS, rows == old", fz["route_check"]["status"] == "PASS" and fz["route_check"]["rows"] == ofz["route_check"]["rows"], fz["route_check"]["status"])
gate("E fs_border_gate PASS == old", fz["fs_border_gate"] == ofz["fs_border_gate"], fz["fs_border_gate"])
sq = lambda L: [r for r in L if str(r.get("addr", "")).startswith("new:SQ1.")]               # noqa: E731
nsq = lambda L: [r for r in L if not str(r.get("addr", "")).startswith("new:SQ1.")]          # noqa: E731
tix = dict((r[1], r[0]) for r in rows if r[1])
_o, _n = nsq(ofz["addr_pos"]), nsq(fz["addr_pos"])
print("FACT addr_pos non-SQ1 rows old {0} new {1}; only-old {2}; only-new {3}".format(len(_o), len(_n), [r for r in _o if r not in _n],
      [r for r in _n if r not in _o]), flush=True)
print("FACT addr_pos SQ1 old {0} -> new {1}".format([(r["addr"], r["index"]) for r in sq(ofz["addr_pos"])], [(r["addr"], r["index"]) for r in sq(fz["addr_pos"])]), flush=True)
# run b (after prep_c145_2_fix.log rc=1, review c145-2-fix-addrpos): stagesim allocates symbolic ids per node AND per terminal (old end sym
# PS1 -1 + 12 rows -> WT2 -14; SQ1 -38 + 8 rows -> LRL1 -47, sim/ring_p4_s04v18/step_23_wire.json), so 4 more SQ1 rows shift every symbolic
# id allocated after SQ1 by -4. Non-SQ1 rows are compared on (n, addr, source, index, class, name); their owner only by that shift rule.
KEYF = ("n", "addr", "source", "index", "class", "name")
key = lambda r: tuple(r.get(f) for f in KEYF)                                                 # noqa: E731
shift_ok = len(_o) == len(_n) and all(y["owner"] == (x["owner"] - 4 if isinstance(x["owner"], int) and x["owner"] <= OLD_SYM["new:SQ1"] - 9 else x["owner"])
                                      for x, y in zip(_o, _n))
nsym = json.load(open(os.path.join(ROOT, fz["last_step"]["path"]), encoding="utf-8"))["state"]["sym"]
print("FACT end sym old {0} -> new {1}".format(OLD_SYM, nsym), flush=True)
gate("A addr_pos == old except SQ1 rows on (n, addr, source, index, class, name); owners shifted -4 for old <= -47 only; SQ1 index == measured t-index",
     [key(r) for r in _n] == [key(r) for r in _o] and shift_ok
     and len(sq(fz["addr_pos"])) == len(sq(ofz["addr_pos"])) and all(r["index"] == tix[r["name"]] for r in sq(fz["addr_pos"])), sq(fz["addr_pos"]))
gate("A2 new end sym == old end sym (read before the sim) with every id after SQ1 (old <= old SQ1 - 9) shifted by -4",
     nsym == dict((s, (u - 4 if u <= OLD_SYM["new:SQ1"] - 9 else u)) for s, u in OLD_SYM.items()), nsym)
changed_steps = [s["n"] for s, t in zip(fz["step_files"], ofz["step_files"]) if s["md5"] != t["md5"]]
print("FACT step files changed (md5) {0} of {1}".format(changed_steps, len(fz["step_files"])), flush=True)
fz["rebase"] = ofz["rebase"]                                                                 # stage_prerun.py:4406-4409 form, carried
fz["plan_in"] = ofz["plan_in"]
fz["resim"] = {"card": "145-a1-2", "why": "SQ1 terminal row corrected to the measured 12-row table; re-simulated on the unchanged real base",
               "from_plan": {"path": rel(PLAN), "md5": PLAN_MD5}, "old_copy": {"path": rel(OLDP), "md5": md5(OLDP)},
               "measured": "tools/bench/diag_c144_p4s04v18_scratch.log:230-242 (md5 64a6b63b)", "sim_input_md5": fz.get("plan_in", {}).get("md5")}
json.dump(out, open(PLAN, "w", encoding="utf-8"), indent=1)
chk = json.load(open(PLAN, encoding="utf-8"))
gate("W plan written FINAL; actions == edited; open_rows_match; plan_in = *_in", chk.get("final") is True and chk["actions"] == new["actions"]
     and chk["finalized"]["open_rows_match"] is True and chk["finalized"]["plan_in"]["path"].endswith("plan_ring_p4_s04v18_in.json"), md5(PLAN))
print("FACT md5 plan old {0} -> new {1}; summary {2}; last_step {3}".format(PLAN_MD5, md5(PLAN), fz["summary"]["md5"], fz["last_step"]["md5"]), flush=True)
ARTS.extend([{"path": rel(PLAN), "md5": md5(PLAN)}, {"path": rel(OLDP), "md5": md5(OLDP)}])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
