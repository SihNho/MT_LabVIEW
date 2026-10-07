r"""selftest_elpred - card 143-3 step 2 (OFFLINE, no LabVIEW): self-test of the FIXED Error List predictor
(tools/bench/prep_c143_3_elrule.py, PD333(b)).
PREDICTION CONTRACT:
  U1-U4 synthetic: an unwired created Local adds 1; a While cond cut adds 1; an item open at start and wired at end is debited 1;
        a created node with an unwired input adds 1 (PD322(e) kept).
  S02  re-derive P4 session 2 (plan_ring_p4_s02v18.json step_00 -> step_34, base = session 1's measured 51) == 53 (MEASURED,
       errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json item_count 53; diag_c143_2_facts.md), new items == the Local
       of symbol -20 (#6902) and the cond of body #23166.
  S01  re-derive P4 session 1 (plan_ring_p4_s01.json, base = P3b-2b expected 51) == 51 (MEASURED, diag_c141_3_facts.md / PD326(a)).
  PD349 (card chat-T5; the bench arms' fix, A13K card 144-a2-2's form ported to main - SR class + A narrowed by terminal class):
  U5   a created RSR whose inner sink is unwired adds ONE item ('sr'), not also 'input'; its unwired outer source and the LSR's
       unwired inner source add nothing.
  U6   a created While body Diagram whose only unwired sink is its cond row adds ONE item ('cond'), not also 'input'; with a
       second unwired sink it is also 'input' (narrowing by terminal class, not by uid).
  S03  re-derive P4 session 3 (plan_ring_p4_s03v18.json, base = s02 measured 53, extra owners = its base doc) == 55,
       new == [cond -46, local -49, sr -36, sr -27], closed == [cond 23166, local 6902] (the old rule gave 56).
  UNC  uncertain_base_newly_unwired_inputs == [] for s01, s02 and s03.
  R1   the RECORDED Error List reads count 51 / 53 / 55 for s01 / s02 / s03 (s03 = arm A13K's read, copied to
       tools/bench/elrule_fixtures/) and each re-derived total equals its recording.
  R2   per class (local, cond, sr) the recorded count change s01->s02 and s02->s03 equals the re-derived new - closed items
       (recordings classified with elrule.item_class on raw + detail).
  R3   independent stage: L2 b1 -> b2a recordings hold 2 -> 0 'Shift Register: unwired from inside' items and the re-derived
       plan_l2b2a.json closes exactly 2 'sr' items (the old rule: 0). Over all 45 finalized plans only three re-derived deltas
       change: s03v18 (+3 -> +2), l2b2a (0 -> -2, this gate) and plan_ring_p4s1 (+11 -> +10, never launched, X10-refused, PD319).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_elpred.log -- py -u tools/bench/selftest_elpred.py"""
import collections, json, os, sys                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import prep_c143_3_elrule as EL                                                             # noqa: E402
from tools import elrule as ELR                                                             # noqa: E402  (item_class)
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
SR = [T(20, -6, "RightShiftRegister", "", False, 0, "InnerTerminal"), T(21, -6, "RightShiftRegister", "", True, 0, "OuterTerminal"),
      T(22, -7, "LeftShiftRegister", "", True, 0, "InnerTerminal"), T(23, -7, "LeftShiftRegister", "", False, 9, "OuterTerminal")]
r = EL.predict(base, {"terminals": base["terminals"] + SR, **OWN}, 10, created=[-6, -7])
gate("U5 a created RSR with an unwired inner sink adds ONE 'sr' item (not also 'input'); unwired sources add none",
     r["predicted_total"] == 11 and r["new_items"] == [["sr", -6]], r["new_items"])
OWN2 = {"owners": {"100": ["WhileLoop", 99], "-8": ["WhileLoop", -9]}}
r = EL.predict(base, {"terminals": base["terminals"] + [T(30, -8, "Diagram", "", False, 0)], **OWN2}, 10, created=[-8, -9])
r6b = EL.predict(base, {"terminals": base["terminals"] + [T(30, -8, "Diagram", "", False, 0), T(31, -8, "Diagram", "x", False, 0)], **OWN2},
                 10, created=[-8, -9])
gate("U6 a created body whose only unwired sink is its cond row adds ONE 'cond' item; with another unwired sink also 'input'",
     r["new_items"] == [["cond", -8]] and r6b["new_items"] == [["cond", -8], ["input", -8]], [r["new_items"], r6b["new_items"]])


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
p03 = J("tools/bench/plan_ring_p4_s03v18.json")
b03 = J(((p03.get("finalized") or {}).get("base") or p03.get("base") or {})["path"])
r3, a3, b3, m3 = session("tools/bench/plan_ring_p4_s03v18.json", 53, (b03,))
print("SELFTEST s03 re-derived = {0} (base 53, new {1}, closed {2}; steps {3} -> {4}; created {5}; uncertain {6}; detail_end {7})".format(
    r3["predicted_total"], r3["new_items"], r3["closed_items"], a3, b3, m3, r3["uncertain_base_newly_unwired_inputs"], r3["detail_end"]), flush=True)
gate("S03 re-derived s03 == 55 (old rule 56)", r3["predicted_total"] == 55, r3["predicted_total"])
gate("S03b new == [cond -46, local -49, sr -36, sr -27]; closed == [cond 23166, local 6902]",
     r3["new_items"] == [["cond", -46], ["local", -49], ["sr", -36], ["sr", -27]]
     and r3["closed_items"] == [["cond", 23166], ["local", 6902]], [r3["new_items"], r3["closed_items"]])
gate("UNC uncertain == [] for s01, s02, s03", all(x["uncertain_base_newly_unwired_inputs"] == [] for x in (r1, r2, r3)),
     [x["uncertain_base_newly_unwired_inputs"] for x in (r1, r2, r3)])

# ---- R1-R3: against the RECORDED Error List reads (PD349)
CLS = ("local", "cond", "sr")


def rec(path):
    """(item count, {class: n}) of one recorded Error List read, classified with elrule.item_class on raw + detail."""
    it = J(path).get("items") or []
    c = collections.Counter(ELR.item_class("{0} {1}".format(x.get("raw", ""), x.get("detail", ""))) for x in it)
    return len(it), dict((k, c.get(k, 0)) for k in CLS)


def delta(r):
    n = collections.Counter(k[0] for k in r["new_items"])
    c = collections.Counter(k[0] for k in r["closed_items"])
    return dict((k, n.get(k, 0) - c.get(k, 0)) for k in CLS)


REC = {"s01": "tools/bench/errorlist_D1_ring_p4s01_20261002_232547_20261002_233212.json",
       "s02": "tools/bench/errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json",
       "s03": "tools/bench/elrule_fixtures/errorlist_p4s03_armA13K_20261007_103040.json"}
R = dict((k, rec(p)) for k, p in REC.items())
print("SELFTEST recordings {0}".format(R), flush=True)
gate("R1 recorded counts s01/s02/s03 == 51/53/55 == re-derived",
     [R[k][0] for k in ("s01", "s02", "s03")] == [51, 53, 55] == [r1["predicted_total"], r2["predicted_total"], r3["predicted_total"]],
     [[R[k][0] for k in ("s01", "s02", "s03")], [r1["predicted_total"], r2["predicted_total"], r3["predicted_total"]]])
rd12 = dict((k, R["s02"][1][k] - R["s01"][1][k]) for k in CLS)
rd23 = dict((k, R["s03"][1][k] - R["s02"][1][k]) for k in CLS)
gate("R2 per-class recorded change s01->s02 == re-derived s02 and s02->s03 == re-derived s03 (local, cond, sr)",
     rd12 == delta(r2) and rd23 == delta(r3), [rd12, delta(r2), rd23, delta(r3)])
pl = J("tools/bench/plan_l2b2a.json")
sf = pl["finalized"]["step_files"]
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
made = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - \
    set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
rl2 = EL.predict(st0, last, 0, made)
lb1 = rec("tools/bench/errorlist_D1_l2_b1_20260927_193100_c111.json")
lb2 = rec("tools/bench/errorlist_D1_l2_b2a_20260928_001426_20260928_001821.json")
gate("R3 L2 b1 -> b2a recorded sr items 2 -> 0 == re-derived plan_l2b2a closes 2 sr (sr delta -2)",
     lb1[1]["sr"] == 2 and lb2[1]["sr"] == 0 and delta(rl2)["sr"] == -2 and len(rl2["closed_items"]) == 2,
     [lb1, lb2, rl2["new_items"], rl2["closed_items"]])
json.dump({"s02": r2, "s01": r1, "s03": r3, "recordings": R, "l2b2a": rl2},
          open(os.path.join(ROOT, "tools", "bench", "selftest_elpred.json"), "w", encoding="utf-8"), indent=1)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
# ---
# labview: none
# hardware: none
# ---
