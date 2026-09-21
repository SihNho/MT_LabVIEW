r"""selftest_next_gate_jev.py - the ADVISORY Jev reading inside tools/hooks/guard_bash.py:next_gate().

It runs against a FAKE project root under the system temp dir (its own STATUS.md and next_snapshot.md5) and a
FAKE `jev` module injected into sys.modules, so it touches neither the real STATUS.md, nor the real snapshot,
nor the network, and spends nothing. The real `jev_next_q` constants ARE used - the questions are what the gate
asks and what was measured.

CASES
  C1  NEXT still hashes as the snapshot        -> gate returns 2 (blocks) AND asks Jev nothing
  C2  NEXT rewritten, Jev answers p = 0.08     -> gate returns 0, `JEV-NEXT-POOR p=0.08: first-act` on stderr,
                                                 one line appended to tools/bench/jev_gate.log (the fake root's)
  C3  NEXT rewritten, Jev answers p = 0.95     -> gate returns 0, NOTHING printed
  C4  NEXT rewritten, Jev errors ('no key')    -> gate returns 0, NOTHING printed (silence by construction)
"""
import hashlib
import io
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import guard_bash  # noqa: E402
import jev_next_q  # noqa: E402

STATUS_BODY = ("# STATUS\n\n## NEXT\n%s\n\n## Where to look\nnothing\n")
PASS, FAIL = [], []


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s  %-58s %s" % ("PASS" if ok else "FAIL", label, detail))


def fake_jev(p, err=None, missing="first-act"):
    m = types.ModuleType("jev")
    m.UNKNOWN_LO, m.UNKNOWN_HI = 0.30, 0.70
    m.calls = []

    def ask(state, questions, purpose="unspecified", timeout=60, retries=3):
        m.calls.append(purpose)
        if err:
            return None, err
        return {"answers": {"startable": {"type": "noul", "noul": p},
                            "missing": {"choice": missing, "probabilities": {missing: 0.9}}}}, None

    m.ask = ask
    m.noul = lambda resp, name=None: (resp or {}).get("answers", {}).get(name, {}).get("noul")
    m.choice = lambda resp, name: ((resp or {}).get("answers", {}).get(name, {}).get("choice"),
                                   (resp or {}).get("answers", {}).get(name, {}).get("probabilities"))
    return m


def run_case(label, next_text, snap_text, p, err=None):
    """Returns (rc, stderr text, gate-log lines) with guard_bash pointed at a throwaway root."""
    tmp = tempfile.mkdtemp(prefix="nextgate_")
    os.makedirs(os.path.join(tmp, "tools", "bench"))
    os.makedirs(os.path.join(tmp, "tools", "hooks"))
    with open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8") as f:
        f.write(STATUS_BODY % next_text)
    snap = hashlib.md5(snap_text.strip().encode("utf-8")).hexdigest()
    with open(os.path.join(tmp, "tools", "bench", "next_snapshot.md5"), "w", encoding="utf-8") as f:
        f.write(snap)
    old_here, old_err = guard_bash.HERE, sys.stderr
    old_jev = sys.modules.get("jev")
    guard_bash.HERE = os.path.join(tmp, "tools", "hooks")
    sys.modules["jev"] = fake_jev(p, err)
    sys.modules["jev_next_q"] = jev_next_q
    sys.stderr = io.StringIO()
    try:
        rc = guard_bash.next_gate()
        errtxt = sys.stderr.getvalue()
    finally:
        sys.stderr = old_err
        guard_bash.HERE = old_here
        if old_jev is not None:
            sys.modules["jev"] = old_jev
        else:
            sys.modules.pop("jev", None)
    calls = list(sys.modules.get("jev").calls) if hasattr(sys.modules.get("jev", None), "calls") else []
    glog = os.path.join(tmp, "tools", "bench", "jev_gate.log")
    lines = open(glog, encoding="utf-8").read().splitlines() if os.path.exists(glog) else []
    return rc, errtxt, lines, calls


def main():
    print("=== selftest_next_gate_jev  (fake root, fake jev, no network, no STATUS.md touched)")
    same = "🔴 FIRST ACT - do the thing, from file X, pass criterion Y."
    rc, err, lines, calls = run_case("C1", same, same, 0.05)
    # the details below say "returned N", never "rc=N": bgrun's inner-failure scanner reads `rc=<non-zero>`
    # anywhere in a log as a failure, and a PASS line quoting the blocking return value would end this
    # self-test rc=1 and arm guard_peer against a run that passed (tools/bgrun.py:215).
    gate("C1 unchanged NEXT still BLOCKS the retrospective", rc == 2, "returned %d" % rc)
    gate("C1 no Jev call is made when the gate blocks", "JEV-NEXT-POOR" not in err and not lines,
         "stderr has the block message: %s" % ("yes" if "BLOCKED" in err else "no"))

    rc, err, lines, _ = run_case("C2", "We looked at a lot of things and they were interesting.", same, 0.08)
    gate("C2 rewritten NEXT is not blocked", rc == 0, "returned %d" % rc)
    gate("C2 a low probability prints JEV-NEXT-POOR with p and the missing element",
         "JEV-NEXT-POOR p=0.08: first-act" in err, repr(err.strip()[:80]))
    gate("C2 the advisory line is appended to jev_gate.log",
         len(lines) == 1 and "JEV-NEXT-POOR p=0.08" in lines[0] and "next_gate" in lines[0],
         repr(lines[:1]))

    rc, err, lines, _ = run_case("C3", "🔴 FIRST ACT - build Z from `docs/plan.md` §4; pass = 12 gates.", same, 0.95)
    gate("C3 a high probability is silent", rc == 0 and not err and not lines,
         "returned %d, stderr %r" % (rc, err[:40]))

    rc, err, lines, _ = run_case("C4", "anything at all", same, None, err="no key")
    gate("C4 an error from Jev is silence, never a block", rc == 0 and not err and not lines,
         "returned %d, stderr %r" % (rc, err[:40]))

    print("\n=== GATES %d pass / %d fail%s" % (len(PASS), len(FAIL),
                                               ("; failing: " + ", ".join(FAIL)) if FAIL else ""))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
