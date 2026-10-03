r"""selftest_elpred - card 143-3 step 2 (OFFLINE, no LabVIEW): self-test of the FIXED Error List predictor
(tools/bench/prep_c143_3_elrule.py, PD333(b)).
PREDICTION CONTRACT:
  U1-U4 synthetic: an unwired created Local adds 1; a While cond cut adds 1; an item open at start and wired at end is debited 1;
        a created node with an unwired input adds 1 (PD322(e) kept).
  S02  re-derive P4 session 2 (plan_ring_p4_s02v18.json step_00 -> step_34, base = session 1's measured 51) == 53 (MEASURED,
       errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json item_count 53; diag_c143_2_facts.md), new items == the Local
       of symbol -20 (#6902) and the cond of body #23166.
  S01  re-derive P4 session 1 (plan_ring_p4_s01.json, base = P3b-2b expected 51) == 51 (MEASURED, diag_c141_3_facts.md / PD326(a)).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_elpred.log -- py -u tools/bench/selftest_elpred.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import prep_c143_3_elrule as EL                                                             # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


def T(u, o, cls, name, src, w, tc="Terminal"):
    return {"term_uid": u, "owner_uid": o, "owner_class": cls, "term_name": name, "is_source": src, "wire_uid": w, "term_class": tc}


OWN = {"owners": {"100": ["WhileLoop", 99]}}
base = {"terminals": [T(1, 100, "Diagram", "", False, 5), T(2, 10, "Local", "A", True, 6), T(3, 11, "Local", "B", True, 0)], **OWN}
r = EL.predict(base, {"terminals": [T(1, 100, "Diagram", "", False, 5), T(2, 10, "Local", "A", True, 6), T(3, 11, "Local", "B", True, 0),
                                    T(4, -2, "Local", "C", True, 0)], **OWN}, 10, created=[-2])
gate("U1 an unwired created Local adds 1 (10 -> 11)", r["predicted_total"] == 11, r["new_items"])
r = EL.predict(base, {"terminals": [T(1, 100, "Diagram", "", False, 0), T(2, 10, "Local", "A", True, 6), T(3, 11, "Local", "B", True, 0)], **OWN},
               10, created=[])
gate("U2 a While cond cut adds 1 (10 -> 11)", r["predicted_total"] == 11, r["new_items"])
r = EL.predict(base, {"terminals": [T(1, 100, "Diagram", "", False, 5), T(2, 10, "Local", "A", True, 6), T(3, 11, "Local", "B", True, 7)], **OWN},
               10, created=[])
gate("U3 an open Local wired at the end is debited (10 -> 9)", r["predicted_total"] == 9, r["closed_items"])
r = EL.predict(base, {"terminals": base["terminals"] + [T(8, -4, "Function", "x", False, 0), T(9, -4, "Function", "y", True, 3)], **OWN},
               10, created=[-4])
gate("U4 a created node with an unwired input adds 1 (PD322(e) kept)", r["predicted_total"] == 11, r["new_items"])


def session(plan_path, base_total, extra=()):
    p = J(plan_path)
    sf = (p.get("finalized") or {}).get("step_files") or []
    st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
    made = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - \
        set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
    return EL.predict(st0, last, base_total, made, extra_owner_states=extra), sf[0]["path"], sf[-1]["path"], sorted(made)


g02 = J("tools/bench/graph_ring_p4s02_20261003_112505.json")
r2, a2, b2, m2 = session("tools/bench/plan_ring_p4_s02v18.json", 51, (g02,))
print("SELFTEST s02 re-derived = {0} (base 51, new {1}, closed {2}; steps {3} -> {4}; created {5}; uncertain {6}; detail_end {7})".format(
    r2["predicted_total"], r2["new_items"], r2["closed_items"], a2, b2, m2, r2["uncertain_base_newly_unwired_inputs"], r2["detail_end"]), flush=True)
gate("S02 re-derived s02 == 53 (measured)", r2["predicted_total"] == 53, r2["predicted_total"])
gate("S02b new items == [cond 23166, local -20]", r2["new_items"] == [["cond", 23166], ["local", -20]], r2["new_items"])
r1, a1, b1, m1 = session("tools/bench/plan_ring_p4_s01.json", 51)
print("SELFTEST s01 re-derived = {0} (base 51, new {1}, closed {2}; steps {3} -> {4}; created {5}; uncertain {6}; open_at_start {7})".format(
    r1["predicted_total"], r1["new_items"], r1["closed_items"], a1, b1, m1, r1["uncertain_base_newly_unwired_inputs"], r1["open_at_start"]), flush=True)
gate("S01 re-derived s01 == 51 (measured)", r1["predicted_total"] == 51, r1["predicted_total"])
json.dump({"s02": r2, "s01": r1}, open(os.path.join(ROOT, "tools", "bench", "selftest_elpred.json"), "w", encoding="utf-8"), indent=1)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
