r"""diag_c113c_plan - card 113-2 (OFFLINE, no LabVIEW), after T1 (stagexec connect_route widened for LoopTunnel OUTER faces, self-test
tools/bench/selftest_stagexec_c113a.log 124/0):
 S   the T2 scratch plan: rows b2_04 (CT #28170 -> LoopTunnel #31051 outer, ForLoop #1359) and b2_07 (LoopTunnel #29172 outer, ForLoop
     #29874 -> CT indicator #28786) copied from tools/bench/plan_l2b2b_in.json, on the SAVED B2a graph; open_rows = B2b's 15 declared, then
     re-declared from the simulated end (rows the other 7 B2b rows would close stay open in this scratch) -> sim/c113c/plan_c113c_bed.json.
 P2  plan_l2b2b_in.json (UNCHANGED, 9 rows, 15 open rows declared by card 113-1) re-simulated with route_check -> tools/bench/plan_l2b2b.json;
     plan_l2b2b_d4.json keeps its 20 scope nodes (namediff_l2b2b.json, card 113-1 P1) and gets the new plan md5.
PRIOR ART: diag_c112c_plan.py (scratch plan) + diag_c113b_plan.py (P2), whose round loop this repeats. No new tool.
PREDICTION: S FINAL, routes [ctltun, ctlsink] with owner loops #1359 / #29874; P2 FINAL, open_rows_match, route check PASS 9/9:
  b2_01 nested, b2_02 cfw, b2_03 nested, b2_04 ctltun, b2_05 ctltun, b2_06 cfw, b2_07 ctlsink, b2_08 cfw, b2_16 ctltun.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c113c_plan.log -- py -u tools/bench/diag_c113c_plan.py"""
import hashlib, json, os, sys                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS, protocol                                                       # noqa: E401,E402
GR = os.path.join(HERE, "graph_l2b2a_20260928.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates, arts = [], []


def gate(lab, ok, det=""):
    gates.append((lab, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:900]), flush=True)


kp = lambda keys: sorted(set((SS.V.key_parts(k)[0], SS.V.key_parts(k)[2]) for k in keys or []))   # noqa: E731


def sim(pin, path, out_root, out_dir, why_new):
    S = None
    for rnd in (1, 2):
        json.dump(pin, open(path, "w", encoding="utf-8"), indent=1)
        S = SS.simulate(path, GR, out_root=out_root, plan_out_dir=out_dir, route_check=True)
        end = kp(S.get("end_cdiff_rows"))
        print("ROUND", rnd, os.path.basename(path), "FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"],
              "end pairs", len(end), "declared", len(pin["open_rows"]), flush=True)
        if S["final"] or S["failed"] or why_new is None:
            break
        have = set((int(r["node"]), r["term"]) for r in pin["open_rows"])
        pin["open_rows"] = [r for r in pin["open_rows"] if (int(r["node"]), r["term"]) in set(end)] + \
            [{"node": n, "term": t, "why": why_new} for n, t in end if (n, t) not in have]
    rc = S.get("route_check") or {}
    for r in rc.get("rows") or []:
        print("ROUTE-ROW", os.path.basename(path), r.get("k"), r.get("ids"), r.get("route"), "|", r.get("how"), "|", r.get("unroutable"), flush=True)
    return S, rc


PIN_FULL = os.path.join(HERE, "plan_l2b2b_in.json")
FULL = json.load(open(PIN_FULL, encoding="utf-8"))
gate("P2 input plan_l2b2b_in.json md5 == card 113-2 pin d13c0de4", md5(PIN_FULL) == "d13c0de4f260373ecde033d1e8a04a13", md5(PIN_FULL))
# ---- S: the T2 scratch plan (b2_04 + b2_07)
OUT = os.path.join(HERE, "sim", "c113c")
os.makedirs(OUT, exist_ok=True)
spin = {"schema": "stageplan/1", "stage": "c113c_bed", "goal": "card 113-2 T2 scratch: rows b2_04 + b2_07 of plan_l2b2b_in.json on a byte copy of "
        "the B2a bed (live check of OpCtlSinkWire_v1 on a LoopTunnel owner loop, review c113b-route s4)", "base": FULL["base"], "context": FULL["context"],
        "actions": [dict(a) for a in FULL["actions"] if a["id"] in ("b2_04", "b2_07")], "open_rows": [dict(r) for r in FULL["open_rows"]]}
S2, rc2 = sim(spin, os.path.join(OUT, "plan_c113c_bed_in.json"), OUT, OUT,
              "scratch c113c: left for B2b (closed there by its other 7 rows), from the simulated end")
routes2 = [r.get("route") for r in rc2.get("rows") or []]
gate("S scratch plan FINAL, open_rows_match, routes == [ctltun, ctlsink]", bool(S2["final"] and S2["open_rows_match"]) and routes2 == ["ctltun", "ctlsink"],
     (S2["final"], S2["open_rows_match"], routes2))
if S2.get("plan_out"):
    arts.append({"path": S2["plan_out"]["path"], "md5": S2["plan_out"]["md5"]})
# ---- P2: the full 9-row plan, input unchanged
S, rc = sim(FULL, PIN_FULL, os.path.join(HERE, "sim", "l2b2"), HERE, None)
want = {"b2_01": "nested", "b2_02": "cfw", "b2_03": "nested", "b2_04": "ctltun", "b2_05": "ctltun", "b2_06": "cfw", "b2_07": "ctlsink",
        "b2_08": "cfw", "b2_16": "ctltun"}
got = dict((r["ids"][0], r.get("route")) for r in rc.get("rows") or [] if r.get("ids"))
gate("P2 FINAL and open_rows_match", bool(S["final"] and S["open_rows_match"]), (S["final"], S["open_rows_match"], S["failed"]))
gate("P2 route check PASS, 9/9 rows routed, none UNROUTABLE", rc.get("status") == "PASS" and len(got) == 9 and
     not any(r.get("unroutable") for r in rc.get("rows") or []), (rc.get("status"), str(rc.get("first_fail"))[:600]))
gate("P2 routes == prediction", got == want, got)
gate("P2 input unchanged by the re-simulation (open_rows already re-declared by 113-1)", md5(PIN_FULL) == "d13c0de4f260373ecde033d1e8a04a13", md5(PIN_FULL))
D4P = os.path.join(HERE, "plan_l2b2b_d4.json")
if S.get("plan_out") and S["final"]:
    arts.append({"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]})
    d4 = json.load(open(D4P, encoding="utf-8"))
    d4["plan_md5"], d4["card"] = S["plan_out"]["md5"], d4["card"] + "; plan_md5 re-pinned by card 113-2 (diag_c113c_plan.py), scope unchanged"
    json.dump(d4, open(D4P, "w", encoding="utf-8"), indent=1)
    arts.append({"path": "tools/bench/plan_l2b2b_d4.json", "md5": md5(D4P)})
    gate("P2 D4 scope = 20 nodes (namediff_l2b2b.json, unchanged)", len(d4["scope_nodes"]) == 20, len(d4["scope_nodes"]))
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None), arts)))
