r"""selftest_stagesim_pin - card 115-1 B1 (PD229(b); review archive/peer/2026-09-28-c114d-regress.md:94-107): the ONE check
that pins `stagesim.py selftest`'s output inside selftest_stagesim_l2a1_80.py (E1) and selftest_stagesim_unflip_81.py (U3).

card 114-4 turned the old exact pin (42/0, broke at 57 / 71 / 75) into "0 fail"; the review showed that alone lets a
DELETED gate or a self-test that quietly skips a block pass. This adds back what an exact count gave, without breaking on
growth: fail == 0, rc == 0, pass >= FLOOR (75 = the count on record, diag_c114d_regress_r2.log:3) and every FROZEN label
G01..G42 printed as a PASS line. SELFTEST_STAGESIM_PASS_FLOOR may only RAISE the floor (the negative run), never lower it.

    py tools/bench/selftest_stagesim_pin.py     (negative cases on doctored stdout; RESULT line; exit 0/1)
"""
import os
import re
import sys

FLOOR_ON_RECORD = 75
FROZEN = ["G{0:02d}".format(i) for i in range(1, 43)]


def floor():
    try:
        return max(FLOOR_ON_RECORD, int(os.environ.get("SELFTEST_STAGESIM_PASS_FLOOR") or 0))
    except ValueError:
        return FLOOR_ON_RECORD


def check(stdout, rc):
    """-> (ok, detail). stdout = the whole `stagesim.py selftest` output."""
    m = re.findall(r"=== GATES: (\d+) pass / (\d+) fail", stdout or "")
    got = tuple(int(x) for x in m[-1]) if m else None
    passed = set(re.findall(r"^\s+PASS\s+(G\d\d)\b", stdout or "", re.M))
    missing = [g for g in FROZEN if g not in passed]
    fl = floor()
    ok = got is not None and got[1] == 0 and rc == 0 and got[0] >= fl and not missing
    return ok, {"got": got, "rc": rc, "floor": fl, "frozen_missing": missing[:10]}


def _selftest():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import protocol
    G = []

    def gate(l, ok, d=""):
        G.append((l, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:300]), flush=True)
    good = "".join("  PASS  {0} x\n".format(g) for g in FROZEN) + \
        "".join("  PASS  G{0} y\n".format(i) for i in range(43, 76)) + "=== GATES: 75 pass / 0 fail\n"
    gate("P1 75/0, rc 0, G01-G42 all PASS -> ok", check(good, 0)[0], check(good, 0)[1])
    gate("P2 growth 80/0 passes (floor, not exact)", check(good.replace("75 pass", "80 pass"), 0)[0])
    no7 = good.replace("  PASS  G07 x\n", "")
    gate("N1 a frozen label removed (G07 absent) -> FAIL, names G07", not check(no7, 0)[0] and
         check(no7, 0)[1]["frozen_missing"] == ["G07"], check(no7, 0)[1])
    g7f = good.replace("  PASS  G07 x\n", "  FAIL  G07 x\n")
    gate("N2 a frozen label printed FAIL -> FAIL", not check(g7f, 0)[0], check(g7f, 0)[1])
    low = good.replace("75 pass", "74 pass")
    gate("N3 count below the floor (74) -> FAIL", not check(low, 0)[0], check(low, 0)[1])
    gate("N4 rc 1 with 0 fail -> FAIL", not check(good, 1)[0])
    gate("N5 no GATES line (crash) -> FAIL", not check(good.replace("=== GATES", "=== XX"), 0)[0])
    gate("N6 one failing gate (75/1) -> FAIL", not check(good.replace("0 fail", "1 fail"), 0)[0])
    os.environ["SELFTEST_STAGESIM_PASS_FLOOR"] = "10"
    gate("N7 the env override cannot LOWER the floor (10 -> stays 75)", floor() == 75, floor())
    os.environ["SELFTEST_STAGESIM_PASS_FLOOR"] = "999"
    gate("N8 the env override RAISES it (999) -> 75/0 FAILs", not check(good, 0)[0], check(good, 0)[1])
    del os.environ["SELFTEST_STAGESIM_PASS_FLOOR"]
    n = sum(1 for _l, ok in G if ok)
    first = next((l for l, ok in G if not ok), None)
    print("=== GATES: {0} pass / {1} fail".format(n, len(G) - n))
    print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
    return 0 if first is None else 1


if __name__ == "__main__":
    sys.exit(_selftest())
