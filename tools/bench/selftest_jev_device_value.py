r"""selftest_jev_device_value.py - offline self-test of tools/jev_device_value.py + tools/bench/jev_device_value_labels.py.
No network: jev.ask_n is replaced by a stub. Checks (a) the labels file is well-formed (>=30 items, both devices labelled,
only the three classes), (b) scoring: a stub that answers the true label scores 1.0 and a stub that always answers
'prevented' is scored with the right accuracy and false-positive count, (c) totals over a fake 5-item corpus,
(d) the real corpus parser returns all three item kinds."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS); sys.path.insert(0, HERE)
import jev_device_value as D  # noqa: E402
import jev_device_value_labels as M  # noqa: E402
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok)); print("%s  %s  %s" % ("PASS" if ok else "FAIL", name, detail))


LAB = os.path.join(HERE, "jev_device_value_labels.json")
L = json.load(open(LAB, encoding="utf-8"))
check("L1 labels >= 30 items", len(L["items"]) >= 30, len(L["items"]))
check("L2 two devices a,b", sorted(L["devices"]) == ["a", "b"], sorted(L["devices"]))
check("L3 every item labelled for a and b with a known class",
      all(set(i["labels"]) == {"a", "b"} and set(i["labels"].values()) <= set(D.CLASSES) for i in L["items"]))
truth = {(i["text"]): i["labels"] for i in L["items"]}
dev_of = {v: k for k, v in L["devices"].items()}


def oracle(state, questions, n=None, purpose=""):
    lab = truth[state["item"]][dev_of[state["device"]]]
    return {c: (0.8 if c == lab else 0.1) for c in D.CLASSES}, {"spread": 0.0}, None


def always_prev(state, questions, n=None, purpose=""):
    return {"prevented": 0.7, "reduced": 0.2, "unrelated": 0.1}, {"spread": 0.0}, None


r = M.measure(LAB, ask=oracle)
check("S1 oracle stub scores 1.0 on both devices", r["a"]["all"]["accuracy"] == 1.0 == r["b"]["all"]["accuracy"],
      (r["a"]["all"]["accuracy"], r["b"]["all"]["accuracy"]))
r = M.measure(LAB, ask=always_prev)
n_prev_a = sum(i["labels"]["a"] == "prevented" for i in L["items"])
n_unrel_a = sum(i["labels"]["a"] == "unrelated" for i in L["items"])
check("S2 always-prevented: accuracy = share of 'prevented' labels",
      abs(r["a"]["all"]["accuracy"] - round(n_prev_a / float(len(L["items"])), 3)) < 1e-9, r["a"]["all"]["accuracy"])
check("S3 always-prevented: fp(unrelated->prevented) = number of unrelated labels",
      r["a"]["all"]["fp_unrelated_to_prevented"] == n_unrel_a, (r["a"]["all"]["fp_unrelated_to_prevented"], n_unrel_a))

FAKE = [{"id": 0, "kind": "violation", "text": "v0", "cycle": "1", "date": "2026-09-20", "loss_min": 30.0, "loss_usd": 4.0},
        {"id": 1, "kind": "violation", "text": "v1", "cycle": "2", "date": "2026-09-21", "loss_min": 20.0, "loss_usd": None},
        {"id": 2, "kind": "log", "text": "l2", "cycle": "?", "date": "2026-09-22", "loss_min": 2.0, "loss_usd": None},
        {"id": 3, "kind": "finding", "text": "f3", "cycle": "3", "date": "2026-09-23", "loss_min": None, "loss_usd": None},
        {"id": 4, "kind": "log", "text": "l4", "cycle": "?", "date": "2026-09-24", "loss_min": 9.0, "loss_usd": None}]
ANS = {"v0": "prevented", "v1": "reduced", "l2": "prevented", "f3": "unrelated", "l4": None}


def fake_ask(state, questions, n=None, purpose=""):
    a = ANS[state["item"]]
    if a is None:
        return None, None, "stub: no answer"
    return {c: (0.9 if c == a else 0.05) for c in D.CLASSES}, {"spread": 0.0}, None


t = D.totals(D.classify("fake device", FAKE, ask=fake_ask))
check("T1 counts 2/1/1/1 (prevented/reduced/unrelated/unknown)",
      (t["prevented"], t["reduced"], t["unrelated"], t["unknown"]) == (2, 1, 1, 1), t)
check("T2 loss_min prevented 32, reduced_half 10, expected 42",
      (t["loss_min_prevented"], t["loss_min_reduced_half"], t["loss_min_expected"]) == (32.0, 10.0, 42.0))
check("T3 loss_usd expected 4.0 ('?' counted as 0)", t["loss_usd_expected"] == 4.0, t["loss_usd_expected"])
check("T4 days 5, per day 8.4", (t["days"], t["loss_min_expected_per_day"]) == (5, 8.4),
      (t["days"], t["loss_min_expected_per_day"]))
C = D.corpus()
kinds = {k: sum(i["kind"] == k for i in C) for k in ("violation", "finding", "log")}
check("C1 real corpus has all three kinds", all(kinds.values()), kinds)
check("C2 every violation item carries a numeric loss_min",
      all(isinstance(i["loss_min"], float) for i in C if i["kind"] == "violation"))
print("=== SELFTEST: %d pass / %d fail" % (sum(RES), len(RES) - sum(RES)))
sys.exit(0 if all(RES) else 1)
