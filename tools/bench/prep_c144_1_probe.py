# ---
# labview: none
# hardware: none
# ---
r"""prep_c144_1_probe - card 144-1 step 3 (OFFLINE, no LabVIEW). Does 'new:LRB1.value' / 'new:LWB1.value' still resolve after chat-T5's
measured terminal-class table (termclass_table.json 63b94815)? Reads the step files the finalize wrote on 10-03
(tools/bench/sim/ring_p4_s03v18/step_07_wire.json, step_08_wire.json) AND re-runs stagesim.simulate (current code, route_check off) on the
plan's base into tools/bench/sim/c144_1_probe/ (plan and stored steps untouched), then reports the term each '.value' end bound to and
whether every fresh step state equals the stored one.
Existing tools checked: prep_c143_6_probe2.log (the 143-6 probe; its .py was not kept) - same question, same expected answer.
PREDICTION CONTRACT: step 7 'new:LRB1.value' -> the Local's one row 'BufDiff', a source, wired; step 8 'new:LWB1.value' -> the Local's one row
  'BufDiff', a sink, wired - in the stored step files AND in a fresh simulation with the current stagesim; fresh step states == stored (21).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c144_1_probe.log -- py -u tools/bench/prep_c144_1_probe.py"""
import json, os, sys                                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


def rows(state, owner):
    return [(t["term_uid"], t.get("term_name"), t.get("is_source"), t.get("wire_uid"), t.get("owner_class"), t.get("term_class"))
            for t in state.get("terminals") or [] if t.get("owner_uid") == owner]


def look(state, sym, want_src):
    s = state.get("sym") or {}
    own = s.get(sym)
    r = rows(state, own) if isinstance(own, int) else []
    ok = len(r) == 1 and r[0][1] == "BufDiff" and r[0][2] is want_src and r[0][3] not in (None, 0)
    return own, r, ok


p = J("tools/bench/plan_ring_p4_s03v18.json")
acts = dict((a["id"], a) for a in p["actions"])
print("FACT plan p4_w_b_arr src {0} dst {1} | p4_w_b_out src {2} dst {3}".format(acts["p4_w_b_arr"].get("src"), acts["p4_w_b_arr"].get("dst"),
      acts["p4_w_b_out"].get("src"), acts["p4_w_b_out"].get("dst")), flush=True)
sd = os.path.join(ROOT, "tools", "bench", "sim", "ring_p4_s03v18")
for fn, sym, src in (("step_07_wire.json", "new:LRB1", True), ("step_08_wire.json", "new:LWB1", False)):
    st = J(os.path.join(sd, fn))["state"]
    own, r, ok = look(st, sym, src)
    print("FACT stored {0} {1}.value -> owner {2} rows {3}".format(fn, sym, own, r), flush=True)
    gate("stored {0}: {1}.value = the Local's one row 'BufDiff' ({2}), wired".format(fn, sym, "source" if src else "sink"), ok, r)
import stagesim as SS                                                                      # noqa: E402
OUT = os.path.join(ROOT, "tools", "bench", "sim", "c144_1_probe")
os.makedirs(OUT, exist_ok=True)
gp = os.path.join(ROOT, p["finalized"]["base"]["path"])
SS.simulate(os.path.join(ROOT, "tools", "bench", "plan_ring_p4_s03v18.json"), gp, out_root=OUT, plan_out_dir=OUT, log=print, route_check=False)
fd = os.path.join(OUT, p["stage"])
sm = J(os.path.join(fd, "summary.json"))
print("FACT fresh sim (current stagesim + termclass_table): failed {0} final {1} open_rows_match {2} end rows {3}".format(
      sm.get("failed"), sm.get("final"), sm.get("open_rows_match"), len(sm.get("end_cdiff_rows") or [])), flush=True)
for fn, sym, src in (("step_07_wire.json", "new:LRB1", True), ("step_08_wire.json", "new:LWB1", False)):
    st = J(os.path.join(fd, fn))["state"]
    own, r, ok = look(st, sym, src)
    print("FACT fresh {0} {1}.value -> owner {2} rows {3}".format(fn, sym, own, r), flush=True)
    gate("fresh {0}: {1}.value = the Local's one row 'BufDiff' ({2}), wired".format(fn, sym, "source" if src else "sink"), ok, r)
same = []
for fn in sorted(os.listdir(sd)):
    if fn.startswith("step_") and os.path.exists(os.path.join(fd, fn)):
        same.append((fn, J(os.path.join(sd, fn))["state"] == J(os.path.join(fd, fn))["state"]))
diff = [f for f, s in same if not s]
print("FACT fresh vs stored step states: {0} compared, differ {1}".format(len(same), diff), flush=True)
gate("fresh simulation states == stored finalize step files (all steps)", not diff and len(same) == len(p["actions"]) + 1, diff)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
