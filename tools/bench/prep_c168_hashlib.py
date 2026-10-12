# ---
# labview: none
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/brief_168-a1-1.md
# ---
r"""prep_c168_hashlib - the card-start / card-end hash check as ONE shared function (card 168-a1-1, docs/script-writing.md rules 1, 4).

Found before writing: tools/bench/diag_c167_a1_1_hash.py (and diag_c166_a1_1_hash.py before it) do this job as module-level scripts
(importing one runs it), so each card pasted a fresh copy. This module holds the same calls ONCE: protocol.input_md5_changes (card inputs)
and prep_c156_a1_1_lib.md5 / Gate (the seven claudeDev VI pins below are DATA, copied from diag_c167_a1_1_hash.py:22-25). Cards 168-a1-1 and
168-a1-2 call check(); their thin scripts hold only the card path and the mode.

check(card_path, mode, gate=None) -> {"pass", "fail", "bad_inputs", "pins": [(name, md5, pin, ok)], "n_inputs"}: prints one GATE line per check
  (I: every md5-pinned card input equal; H: each VI pin) through prep_c156_a1_1_lib.Gate (non-fatal). Pure reads (bytes + hashlib).
Self-test (offline, `--selftest`): T1 replays card 168-a1-1 (all inputs + 7 pins equal); T2 a %TEMP% copy of that card with one input md5
altered must report exactly that input as drift; T3 a pin list with one wrong pin must fail that pin only. PREDICTION 3/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c168_hashlib_selftest.log -- py -u tools/bench/prep_c168_hashlib.py --selftest"""
import json, os, sys, tempfile                                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    _p in sys.path or sys.path.insert(0, _p)                                                # noqa: E701
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
VI_PINS = [("D1_ring_p5_20261010_172913.vi", "75773b0d"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
           ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
           ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"), ("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"),
           ("D1_ring_p5s02d_20261010_152518.vi", "6dcd5c3d")]


def check(card_path, mode, gate=None, pins=None):
    """Hash check of a task/1 card: every md5-pinned input vs disk + the claudeDev VI pins. Returns {"pass","fail","bad_inputs","pins",
    "n_inputs"}; prints GATE lines via prep_c156_a1_1_lib.Gate (non-fatal). Read-only. Self-test: this file's --selftest."""
    gate = gate or L.Gate(fatal_default=False)
    p0, f0 = gate.G["pass"], gate.G["fail"]
    card = json.load(open(card_path if os.path.isabs(card_path) else os.path.join(ROOT, card_path), encoding="utf-8"))
    bad = PR.input_md5_changes(card)
    n = sum(1 for it in card.get("inputs") or [] if isinstance(it, dict) and it.get("md5"))
    gate("I {0} md5-pinned card inputs equal ({1})".format(n, mode), not bad, bad or "all equal")
    rows = []
    for name, pin in (VI_PINS if pins is None else pins):
        p = os.path.join(CD, name)
        m = L.md5(p) if os.path.isfile(p) else "missing"
        ok = m.startswith(pin)
        rows.append((name, m, pin, ok))
        gate("H {0} md5 {1} vs pin {2}".format(name, m, pin), ok, "equal" if ok else "UNEQUAL")
    return {"pass": gate.G["pass"] - p0, "fail": gate.G["fail"] - f0, "bad_inputs": bad, "pins": rows, "n_inputs": n}


class _Quiet(object):
    """Gate stand-in for the self-test's DELIBERATE drift cases: counts like Gate, prints 'EXPECTED-DRIFT ...' instead of a GATE line,
    so a log scanner never reads a planted failure as a real one."""

    def __init__(self):
        self.G = {"pass": 0, "fail": 0, "first": None}

    def __call__(self, label, ok, d="", fatal=None):
        self.G["pass" if ok else "fail"] += 1
        print("EXPECTED-DRIFT {0} | {1} | {2}".format("equal" if ok else "unequal", label, str(d)[:300]), flush=True)


def selftest():
    """T1 replay of card 168-a1-1, T2 one altered input md5 detected, T3 one wrong pin detected. Prints gates + RESULT; returns rc."""
    card = os.path.join(ROOT, "tools", "bench", "cards", "task_168-a1-1.json")
    out = L.Gate(fatal_default=False)
    r1 = check(card, "selftest-T1")
    out("T1 card 168-a1-1 replay: inputs + 7 pins equal", r1["fail"] == 0 and r1["pass"] == 1 + len(VI_PINS) and r1["n_inputs"] == 13,
        "pass {0} fail {1} inputs {2}".format(r1["pass"], r1["fail"], r1["n_inputs"]))
    c = json.load(open(card, encoding="utf-8"))
    for it in c["inputs"]:
        it["path"] = os.path.join(ROOT, it["path"])
    c["inputs"][2]["md5"] = "0" * 32
    fd, tmp = tempfile.mkstemp(suffix="_c168_hashlib_selftest.json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(c, f)
    try:
        r2 = check(tmp, "selftest-T2 (one drift expected)", _Quiet(), pins=[])
    finally:
        os.remove(tmp)
    want = os.path.basename(c["inputs"][2]["path"])
    out("T2 altered input md5 reported as drift (exactly 1, {0})".format(want),
        r2["fail"] == 1 and len(r2["bad_inputs"]) == 1 and want in r2["bad_inputs"][0], r2["bad_inputs"])
    r3 = check(card, "selftest-T3 (one bad pin expected)", _Quiet(), pins=[VI_PINS[0], (VI_PINS[1][0], "ffffffff")])
    out("T3 wrong pin reported (exactly 1 of 2)", r3["fail"] == 1 and [x[3] for x in r3["pins"]] == [True, False],
        [x[:2] + (x[3],) for x in r3["pins"]])
    print(PR.result_line(PR.make_result(out.G["pass"], out.G["fail"], out.G["first"], [])), flush=True)
    return 1 if out.G["fail"] else 0


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.exit(selftest())
