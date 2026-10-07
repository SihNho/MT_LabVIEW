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
  PD351(c) (card 145-a2-2; created SubVI calls by the MEASURED pane rule, tools/bench/subvi_requiredness.json):
  U7   NEGATIVE: a created SubVI whose Required (rule 1) terminal is unwired adds ONE 'input' item naming only that terminal
       (its unwired Recommended terminal adds nothing); the same node with the Required terminal wired adds 0.
  U8   a created SubVI absent from the table, or with no VI identity, adds 0 and lists its unwired sinks as uncertain.
  S04  re-derive P4 session 4 (plan_ring_p4_s04v18.json f349c39a, base = s03 measured 55, extra owners = its base doc) == 58,
       new == [input -53, input -34, input -26, local -51, local -32], closed == [cond 29699, local 29720]; PS1 (-1) and SQ1
       (-38) are NOT items (all their unwired sinks measured rule 0/2); uncertain_subvi_terminals == [].
  R4   the RECORDED s04 read (errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json, md5 5e53096a) counts 58 == re-derived,
       and its per-class change from s03 equals the re-derived s04 new - closed (local, cond, sr).
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
# ---- PD351(c), card 145-a2-2: created SubVI calls by the MEASURED pane rule
SYN = {"vis": {"Syn.vi": {"terminals": [{"name": "req", "rule": 1}, {"name": "rec", "rule": 2}, {"name": "out", "rule": 2}]}}}
SUB = lambda w: [T(40, -11, "SubVI", "req", False, w), T(41, -11, "SubVI", "rec", False, 0), T(42, -11, "SubVI", "out", True, 0)]  # noqa: E731
r7 = ELR.predict(base, {"terminals": base["terminals"] + SUB(0), **OWN}, 10, created=[-11], subvis={-11: "Syn.vi"}, table=SYN)
r7b = ELR.predict(base, {"terminals": base["terminals"] + SUB(9), **OWN}, 10, created=[-11], subvis={-11: "Syn.vi"}, table=SYN)
gate("U7 NEGATIVE: created SubVI with an unwired Required terminal adds 1 (10 -> 11, item names only 'req'); wired -> 10",
     r7["predicted_total"] == 11 and r7["new_items"] == [["input", -11]] and r7["detail_end"].get("input") == [[-11, ["req"]]]
     and r7b["predicted_total"] == 10 and r7b["new_items"] == [],
     [r7["predicted_total"], r7["new_items"], r7["detail_end"].get("input"), r7b["predicted_total"]])
r8 = ELR.predict(base, {"terminals": base["terminals"] + SUB(0), **OWN}, 10, created=[-11], subvis={-11: "Other.vi"}, table=SYN)
r8b = ELR.predict(base, {"terminals": base["terminals"] + SUB(0), **OWN}, 10, created=[-11], table=SYN)
gate("U8 SubVI not in table / identity unknown: adds 0, its 2 unwired sinks reported uncertain",
     r8["predicted_total"] == 10 and r8b["predicted_total"] == 10
     and [len(x[2]) for x in r8["uncertain_subvi_terminals"]] == [2] and [len(x[2]) for x in r8b["uncertain_subvi_terminals"]] == [2],
     [r8["uncertain_subvi_terminals"], r8b["uncertain_subvi_terminals"]])
p04 = J("tools/bench/plan_ring_p4_s04v18.json")
b04 = J(((p04.get("finalized") or {}).get("base") or p04.get("base") or {})["path"])
sf4 = p04["finalized"]["step_files"]
st04, last04 = J(sf4[0]["path"])["state"], J(sf4[-1]["path"])["state"]
made4 = set(int(u) for u in (last04.get("sym") or {}).values() if isinstance(u, int)) - \
    set(int(u) for u in (st04.get("sym") or {}).values() if isinstance(u, int))
sv4 = ELR.subvis_from_plan(p04, st04, last04)
r4 = ELR.predict(st04, last04, 55, made4, extra_owner_states=(b04,), subvis=sv4)
print("SELFTEST s04 re-derived = {0} (base 55, new {1}, closed {2}; steps {3} -> {4}; created {5}; subvis {6}; uncertain {7} / {8}; "
      "while_bodies {9}; detail_end {10})".format(r4["predicted_total"], r4["new_items"], r4["closed_items"], sf4[0]["path"],
                                                  sf4[-1]["path"], sorted(made4), sv4, r4["uncertain_base_newly_unwired_inputs"],
                                                  r4["uncertain_subvi_terminals"], r4["while_bodies"], r4["detail_end"]), flush=True)
gate("S04 re-derived s04 == 58 (old rule 60)", r4["predicted_total"] == 58, r4["predicted_total"])
gate("S04b new == [input -53, input -34, input -26, local -51, local -32]; closed == [cond 29699, local 29720]; PS1 -1 / SQ1 -38 no item",
     r4["new_items"] == [["input", -53], ["input", -34], ["input", -26], ["local", -51], ["local", -32]]
     and r4["closed_items"] == [["cond", 29699], ["local", 29720]] and sv4 == {-1: "RingPickSlot_v0.vi", -38: "RingSeqCheck_v0.vi"},
     [r4["new_items"], r4["closed_items"], sv4])
gate("S04c uncertain == [] (base inputs and SubVI terminals)",
     r4["uncertain_base_newly_unwired_inputs"] == [] and r4["uncertain_subvi_terminals"] == [],
     [r4["uncertain_base_newly_unwired_inputs"], r4["uncertain_subvi_terminals"]])
REC4 = "tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json"
import hashlib                                                                              # noqa: E402
md4 = hashlib.md5(open(os.path.join(ROOT, REC4), "rb").read()).hexdigest()
R4 = rec(REC4)
rd34 = dict((k, R4[1][k] - R["s03"][1][k]) for k in CLS)
print("SELFTEST s04 recording {0} md5 {1}; per-class s03->s04 {2}; re-derived {3}".format(R4, md4, rd34, delta(r4)), flush=True)
gate("R4 recorded s04 (5e53096a) counts 58 == re-derived; per-class change s03->s04 == re-derived new - closed",
     md4.startswith("5e53096a") and R4[0] == 58 == r4["predicted_total"] and rd34 == delta(r4), [md4[:8], R4, rd34, delta(r4)])
BAD = lambda p: sum(1 for x in (J(p).get("items") or []) if "unwired or bad terminal" in "{0} {1}".format(x.get("raw", ""), x.get("detail", "")).lower())  # noqa: E731
print("INFO 'unwired or bad terminal' items s03 {0} -> s04 {1} (re-derived input delta {2})".format(
    BAD(REC["s03"]), BAD(REC4), sum(1 for k in r4["new_items"] if k[0] == "input") - sum(1 for k in r4["closed_items"] if k[0] == "input")),
    flush=True)
json.dump({"s02": r2, "s01": r1, "s03": r3, "s04": r4, "recordings": R, "l2b2a": rl2},
          open(os.path.join(ROOT, "tools", "bench", "selftest_elpred.json"), "w", encoding="utf-8"), indent=1)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
# ---
# labview: none
# hardware: none
# ---
