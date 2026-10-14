# read-only: compare every out_p64/p64p3r2/<script>_<mode>.log with the retry-1 log of the same name (out_p64/p64p3r1/).
# Only TEMP dir names made by tempfile (random suffixes) are masked; every other byte must be equal.
import os, re                                                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(HERE, "..", "p64p3r1")
NAMES = ["p64_own_dry.log", "p64_abba_mock.log", "p64_abba_dry.log", "p64_leg_dry.log", "p64_sum_dry.log", "p64_beadmap_dry.log"]
TMP = re.compile(r"(p64abba_mock_|p64own_mock_|tmp)[A-Za-z0-9_]{6,10}")


def lines(p):
    return [TMP.sub(r"\1<TMP>", x.rstrip("\r\n")) for x in open(p, encoding="utf-8", errors="replace")]


for n in NAMES:
    a, b = lines(os.path.join(R1, n)), lines(os.path.join(HERE, n))
    res = [x for x in b if x.startswith("RESULT")]
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
    raw_eq = open(os.path.join(R1, n), "rb").read() == open(os.path.join(HERE, n), "rb").read()
    print("%-22s lines r1 %d r2 %d | raw bytes equal %s | differing lines after TEMP mask %d | %s"
          % (n, len(a), len(b), raw_eq, len(diff) + abs(len(a) - len(b)), res[-1] if res else "NO RESULT LINE"))
    for i, x, y in diff[:5]:
        print("   line %d\n     r1: %s\n     r2: %s" % (i, x[:400], y[:400]))
