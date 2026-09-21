r"""jev_run_all.py - ONE runner for this cycle's Jev work, so it is ONE bgrun and ONE notification
(CLAUDE.md section 3 item 1: "One LabVIEW batch = one runner = one notification"; this one touches no LabVIEW).

Order, and why: the SELF-TEST first, because it costs nothing and proves the wiring before any measurement is
attributed to it; then insertion #1's 40-pair trial; then insertion #6's 30-pair trial. Each part's return code is
reported, and the runner's own rc is non-zero if any part failed.

  py tools/bgrun.py --material --max-min 25 --log tools/bench/jev_discharge.log -- py -u tools/bench/jev_run_all.py
"""
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(HERE), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def run(name, fn):
    print("\n" + "#" * 96)
    print("### %s" % name)
    print("#" * 96, flush=True)
    t0 = time.time()
    try:
        rc = fn()
    except Exception as e:                # noqa: BLE001 - report, never lose the parts that already ran
        import traceback
        traceback.print_exc()
        rc = 99
        print("  FAIL  %s raised %s: %s" % (name, type(e).__name__, str(e)[:200]))
    print("\n--- %s finished rc=%s in %.1f s ---" % (name, rc, time.time() - t0), flush=True)
    return rc


def main():
    print("=== jev_run_all (docs/jev-integration-plan.md rows #1 and #6) ===")
    print("NO LabVIEW, NO COM, NO motor, NO camera. Disk reads + HTTPS to api.typesafe.ai only.\n")
    import jev
    print("key: %s" % ("present, never printed" if jev.get_key() else "ABSENT - the trials will stop early"))

    import selftest_guard_peer_jev
    import jev_discharge_trial
    import jev_priorart_trial

    rcs = {
        "selftest_guard_peer_jev": run("SELF-TEST: guard_peer JEV-DISCHARGE branches",
                                       selftest_guard_peer_jev.main),
        "jev_discharge_trial": run("TRIAL A: does an archived review already cover this failure? (row #1)",
                                   jev_discharge_trial.main),
        "jev_priorart_trial": run("TRIAL B: is this step already prior-art reviewed? (row #6)",
                                  jev_priorart_trial.main),
    }
    print("\n" + "=" * 96)
    print("SUMMARY")
    print("=" * 96)
    for k, v in rcs.items():
        print("  %-28s rc=%s  %s" % (k, v, "ok" if v == 0 else "NON-ZERO"))
    ledger = os.path.join(HERE, "jev_usage.jsonl")
    if os.path.exists(ledger):
        with open(ledger, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        print("  jev usage ledger: %d line(s) total -> %s" % (len(lines), os.path.relpath(ledger, HERE)))
    gl = os.path.join(HERE, "jev_gate.log")
    if os.path.exists(gl):
        with open(gl, encoding="utf-8", errors="replace") as f:
            gls = [ln for ln in f.read().splitlines() if ln.strip()]
        print("  jev_gate.log: %d line(s); last: %s" % (len(gls), gls[-1][:120] if gls else "(none)"))
    return 0 if all(v == 0 for v in rcs.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
